import os
import pandas as pd
import numpy as np

raw_dir = os.path.join("data", "raw")
processed_dir = os.path.join("data", "processed")

def clean_nav_history():
    print("Cleaning nav_history.csv")
    file_path = os.path.join(raw_dir, "02_nav_history.csv")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'].str.strip(), errors='coerce') ## fixing date formats
    df = df.drop_duplicates()  ## removing duplicates
    df = df[df['nav'] > 0]  ## validating nav > 0
    df = df.sort_values(by=['amfi_code', 'date']).reset_index(drop=True)
    
    print("Forward-fill missing NAV for holidays/weekends")
    cleaned_frames = []
    for amfi, group in df.groupby('amfi_code'):
        group = group.set_index('date')
        full_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq='D')
        group = group.reindex(full_range)
        group['amfi_code'] = group['amfi_code'].fillna(amfi).astype(int)
        group['nav'] = group['nav'].ffill()  # Forward-fill the missing prices
        group = group.reset_index().rename(columns={'index': 'date'})
        cleaned_frames.append(group)
        
    final_df = pd.concat(cleaned_frames, ignore_index=True)
    
    final_df.to_csv(os.path.join(processed_dir, "cleaned_nav_history.csv"), index=False)
    print(f"Successfully cleaned nav_history rows: {len(final_df)}")


def clean_investor_transactions():
    print("Cleaning investor_transactions.csv")
    file_path = os.path.join(raw_dir, "08_investor_transactions.csv")
    df = pd.read_csv(file_path)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'].str.strip(), errors='coerce')
    df['transaction_type'] = df['transaction_type'].str.strip().str.capitalize()
    df = df[df['amount_inr'] > 0]
    df['kyc_status'] = df['kyc_status'].str.strip().str.capitalize()
    df.to_csv(os.path.join(processed_dir, "cleaned_investor_transactions.csv"), index=False)
    print(f"Success! Cleaned investor_transactions rows: {len(df)}")


def clean_scheme_performance():
    print("Cleaning scheme_performance.csv")
    file_path = os.path.join(raw_dir, "07_scheme_performance.csv")
    df = pd.read_csv(file_path)
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df['expense_ratio_pct'] = pd.to_numeric(df['expense_ratio_pct'], errors='coerce')
    df['expense_anomaly'] = np.where((df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5), 1, 0)
    
    # Save the output
    df.to_csv(os.path.join(processed_dir, "cleaned_scheme_performance.csv"), index=False)
    print(f"Success! Cleaned scheme_performance rows: {len(df)}")


def clean_remaining_files():
    """Quickly copy/clean remaining files into processed directory so all 10 are together."""
    print("Relocating and checking remaining files")
    files = [
        "01_fund_master.csv", "03_aum_by_fund_house.csv", 
        "04_monthly_sip_inflows.csv", "05_category_flows.csv", 
        "06_industry_folio_count.csv", "09_portfolio_holdings.csv", 
        "10_benchmark_indices.csv"
    ]
    for file in files:
        raw_path = os.path.join(raw_dir, file)
        if os.path.exists(raw_path):
            temp_df = pd.read_csv(raw_path)
            
            temp_df.columns = temp_df.columns.str.strip().str.lower()
            out_name = f"cleaned_{file.split('_', 1)[-1]}" if '_' in file else f"cleaned_{file}"
            temp_df.to_csv(os.path.join(processed_dir, out_name), index=False)
            
    print("All remaining files exported to data/processed/")

if __name__ == "__main__":
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    clean_remaining_files()
    print("\nPHASE 1 COMPLETE: All 10 cleaned datasets are ready in data/processed/")