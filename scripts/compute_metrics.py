"""
Compute Metrics Script - Bluestock MF Capstone
Calculates core performance indicators: CAGR, Annualized Volatility, and Max Drawdown.
Outputs results to the SQLite Star Schema and a processed CSV for the Power BI Dashboard.
"""
import pandas as pd
import numpy as np
import sqlite3
import os

def calculate_performance_metrics():
    print("Starting compute metrics process...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "data", "db", "bluestock_mf.db")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}. Please ensure etl_pipeline.py has run.")
        return

    conn = sqlite3.connect(db_path)
    
    try:
        # Read NAV data
        df_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
        df_nav['date'] = pd.to_datetime(df_nav['date'])
        df_nav = df_nav.sort_values(by=['amfi_code', 'date'])

        metrics = []
        
        for amfi, group in df_nav.groupby('amfi_code'):
            group = group.set_index('date')
            if len(group) < 2:
                continue
            
            group['daily_return'] = group['nav'].pct_change()
            
            start_val = group['nav'].iloc[0]
            end_val = group['nav'].iloc[-1]
            years = (group.index[-1] - group.index[0]).days / 365.25
            cagr = ((end_val / start_val) ** (1 / years) - 1) if years > 0 else 0
            
            volatility = group['daily_return'].std() * np.sqrt(252)
            
            
            rolling_max = group['nav'].cummax()
            drawdown = group['nav'] / rolling_max - 1
            max_drawdown = drawdown.min()
            
            metrics.append({
                'amfi_code': amfi,
                'CAGR_pct': round(cagr * 100, 2),
                'Volatility_pct': round(volatility * 100, 2),
                'Max_Drawdown_pct': round(max_drawdown * 100, 2)
            })
            
        metrics_df = pd.DataFrame(metrics)
        
        metrics_df.to_sql('fact_performance_metrics', conn, if_exists='replace', index=False)
        
        print(f"Compute metrics executed successfully. Results saved to DB.")
        
    except Exception as e:
        print(f"Error computing metrics: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    calculate_performance_metrics()