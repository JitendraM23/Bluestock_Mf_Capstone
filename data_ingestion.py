import os
import pandas as pd


raw_data_dir = os.path.join("data", "raw")
def extract_and_explore():
    a=os.path.exists(raw_data_dir)
    if not a:
        print(f"Error- The directory '{raw_data_dir}' does not exist.")
        return

    csv_files = [f for f in os.listdir(raw_data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in '{raw_data_dir}'.")
        return
        
    print(f"Found {len(csv_files)} CSV files. Starting data ingestion & exploration...\n")

    for file_name in csv_files:
        file_path = os.path.join(raw_data_dir, file_name)
        
        
        print(f" FILE: {file_name}")
        print("-" * 60)
        
        try:
            mf = pd.read_csv(file_path)
            print(f"\n 1. SHAPE (Rows, Columns):")
            print(mf.shape)
            
            print(f"\n 2. DATA TYPES:")
            print(mf.dtypes)
            
            print(f"\n 3. HEAD (First 5 Rows):")
            print(mf.head())
            print("\n")
            
            
        except Exception as e:
            print(f"Error reading {file_name}: {e}\n")

def explore_and_validate():
   
    print("DATA EXPLORATION AND VALIDATION")
    master_path = os.path.join(raw_data_dir, "01_fund_master.csv")
    nav_path = os.path.join(raw_data_dir, "02_nav_history.csv")

    try:
        
        fund_master = pd.read_csv(master_path)
        nav_history = pd.read_csv(nav_path)
    except Exception as e:
        print(f"Error loading files for validation: {e}")
        return

    print("\nExploring Fund Master Uniques\n")
    
    print(f"\nTotal Unique Fund Houses: {fund_master['fund_house'].nunique()}")
    print(fund_master['fund_house'].unique())
    
    print(f"\nTotal Unique Categories: {fund_master['category'].nunique()}")
    print(fund_master['category'].unique())

    print(f"\nTotal Unique Sub-Categories: {fund_master['sub_category'].nunique()}")
    print(fund_master['sub_category'].unique())

    print(f"\nTotal Unique Risk Grades: {fund_master['risk_category'].nunique()}")
    print(fund_master['risk_category'].unique())

    print("\nSTEP 7: Validating AMFI Codes")
    
    master_codes = set(fund_master['amfi_code'].unique())
    nav_codes = set(nav_history['amfi_code'].unique())
    missing_in_nav = master_codes - nav_codes

    print(f"Total AMFI Codes in Fund Master: {len(master_codes)}")
    print(f"Total AMFI Codes in NAV History: {len(nav_codes)}")

    if len(missing_in_nav) == 0:
        print("\nValidation Passed: Every code in fund_master exists in nav_history!")
    else:
        print(f"\nValidation Failed: Found {len(missing_in_nav)} codes in fund_master missing from nav_history.")
        print(f"Missing codes: {missing_in_nav}")
        
    print("\n FInal data Summary:")
    print("1. Missing Values: NaN values detected in 04_monthly_sip_inflows (yoy_growth_pct).")
    print("2. Data Type Issues: Date columns across multiple files are formatted as strings instead of datetime objects.")
    print("3. Structural Mismatch: 06_industry_folio_count is labeled 'month' but contains quarterly data jumps.")
    print("4. Data Entry Errors: Geographic mismatches found (e.g., City: Noida mapped to State: Delhi).")
    print("5. Logical Anomalies: SIP transaction amounts contain highly specific fractional values (e.g., 1834).")
    print(f"6. Relational Integrity: AMFI validation showed {len(missing_in_nav)} missing records between master and history.")
    

if __name__ == "__main__":
    extract_and_explore()
    explore_and_validate()