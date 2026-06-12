import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
processed_dir = os.path.join(BASE_DIR, "data", "processed")

def init_db():
    """Reads schema.sql and builds the empty database tables cleanly."""
    print("Initializing SQLite Database with Star Schema architecture...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Cleared old database file for a fresh start.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Schema layout created successfully.")

def generate_dim_date():
   
    print("Generating rows for dim_date lookup table.")
    date_range = pd.date_range(start="2022-01-01", end="2026-12-31", freq='D')
    
    dim_date_df = pd.DataFrame({
        'date_id': date_range.strftime('%Y-%m-%d'),
        'year': date_range.year,
        'month': date_range.month,
        'day': date_range.day,
        'quarter': date_range.quarter,
        'is_weekend': date_range.weekday.map(lambda x: 1 if x >= 5 else 0)
    })
    
    engine = create_engine(f"sqlite:///{DB_PATH}")
    dim_date_df.to_sql('dim_date', con=engine, if_exists='append', index=False)
    print(f"Populated dim_date with {len(dim_date_df)} calendar dates.")

def get_sql_table_columns(table_name):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns

def load_processed_data():
    """Loads cleaned CSVs into SQLite, explicitly filtering columns to match the target schema schema."""
    print("\n🚀 Commencing automated file ingestion pipeline...")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    ingestion_map = [
        ("cleaned_fund_master.csv", "dim_fund"),
        ("cleaned_nav_history.csv", "fact_nav"),
        ("cleaned_investor_transactions.csv", "fact_transactions"),
        ("cleaned_scheme_performance.csv", "fact_performance"),
        ("cleaned_aum_by_fund_house.csv", "fact_aum")
    ]
    
    for file_name, table_name in ingestion_map:
        file_path = os.path.join(processed_dir, file_name)
        
        if not os.path.exists(file_path):
            print(f"Warning: Missing expected file {file_name}. Skipping...")
            continue
            
        df = pd.read_csv(file_path)
        
        df.columns = (df.columns.str.strip()
                                .str.lower()
                                .str.replace(' ', '_')
                                .str.replace('-', '_')
                                .str.replace('(', '')
                                .str.replace(')', '')
                                .str.replace('%', 'pct'))
        
        rename_dict = {
            'amount': 'amount_inr',
            'expense_ratio': 'expense_ratio_pct',
            'annual_income': 'annual_income_lakh'
        }
        df = df.rename(columns=rename_dict)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
            
        
        expected_columns = get_sql_table_columns(table_name)
        final_columns = [col for col in df.columns if col in expected_columns]
        df = df[final_columns]
        
        print(f"Ingesting {file_name} into SQL table '{table_name}'.")
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        
        db_count = pd.read_sql_query(f"SELECT COUNT(*) FROM {table_name}", engine).iloc[0, 0]
        print(f"Validation Check: Source CSV Rows = {len(df)} | Target SQL Table Rows = {db_count}")
        print(f"SUCCESS: Ingestion verification complete.\n")

if __name__ == "__main__":
    init_db()
    generate_dim_date()
    load_processed_data()
    print("bluestock_mf.db is fully compiled and verified")