"""
Advanced Analytics Script - Bluestock MF Capstone
Calculates quantitative risk metrics (VaR, CVaR, Rolling Sharpe Ratio) 
and executes the SIP Continuity behavioral algorithm to flag churn risk.
"""
import os
import pandas as pd
import sqlite3
import numpy as np

def calculate_risk_metrics(conn):
   
    print("Calculating VaR and CVaR...")
    df_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav = df_nav.sort_values(by=['amfi_code', 'date'])
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    risk_metrics = []
    for amfi, group in df_nav.groupby('amfi_code'):
        returns = group['daily_return'].dropna()
        if len(returns) > 0:
            
            var_95 = np.percentile(returns, 5)
            
            cvar_95 = returns[returns <= var_95].mean()
            
            risk_metrics.append({
                'amfi_code': amfi,
                'VaR_95_pct': round(var_95 * 100, 2),
                'CVaR_95_pct': round(cvar_95 * 100, 2)
            })
            
    risk_df = pd.DataFrame(risk_metrics)
    risk_df.to_sql('fact_risk_metrics', conn, if_exists='replace', index=False)
    print("Risk metrics calculation complete.")

def sip_churn_prediction(conn):
    """Flags investors with an average SIP payment gap exceeding 35 days."""
    print("Running SIP Continuity Analysis...")
    query = """
    SELECT persona_id, transaction_date 
    FROM fact_transactions 
    WHERE transaction_type = 'SIP'
    ORDER BY persona_id, transaction_date
    """
    df_sip = pd.read_sql_query(query, conn)
    df_sip['transaction_date'] = pd.to_datetime(df_sip['transaction_date'])
    df_sip['days_since_last_sip'] = df_sip.groupby('persona_id')['transaction_date'].diff().dt.days
    
    
    churn_analysis = df_sip.groupby('persona_id').agg(
        total_sips=('transaction_date', 'count'),
        avg_payment_gap=('days_since_last_sip', 'mean')
    ).reset_index()
    
    churn_analysis['churn_risk_flag'] = np.where(churn_analysis['avg_payment_gap'] > 35, 'High Risk', 'Healthy')
    
    churn_analysis.to_sql('fact_churn_analysis', conn, if_exists='replace', index=False)
    print("Churn analysis complete. At-Risk personas flagged.")

def calculate_rolling_sharpe(conn):
    """Calculates the 90-Day Rolling Sharpe Ratio."""
    print("Calculating Rolling Sharpe Ratios...")
    df_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    df_nav = df_nav.sort_values(by=['amfi_code', 'date'])
    
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    df_nav['rolling_90d_mean'] = df_nav.groupby('amfi_code')['daily_return'].transform(lambda x: x.rolling(90).mean())
    df_nav['rolling_90d_std'] = df_nav.groupby('amfi_code')['daily_return'].transform(lambda x: x.rolling(90).std())
    
    df_nav['rolling_sharpe'] = (df_nav['rolling_90d_mean'] / df_nav['rolling_90d_std']) * np.sqrt(252)
    
    df_nav[['date', 'amfi_code', 'rolling_sharpe']].dropna().to_sql('fact_rolling_sharpe', conn, if_exists='replace', index=False)
    print("Rolling Sharpe calculation complete.")

def run_analytics():
    db_path = 'bluestock_mf.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Please run etl_pipeline.py first.")
        return
        
    conn = sqlite3.connect(db_path)
    try:
        calculate_risk_metrics(conn)
        sip_churn_prediction(conn)
        calculate_rolling_sharpe(conn)
        print("All Advanced Analytics executed successfully.")
    except Exception as e:
        print(f"Analytics Pipeline Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_analytics()