import pandas as pd
import numpy as np
import sqlite3

print("Finding up the best Recommender")

conn = sqlite3.connect("bluestock_mf.db")
df_funds = pd.read_sql_query("SELECT amfi_code, scheme_name, category FROM dim_fund", conn)
df_nav = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)

print("Calculating Sharpe Ratios on the fly...")
df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()

metrics = df_nav.groupby('amfi_code')['daily_return'].agg(['mean', 'std']).reset_index()
metrics['Sharpe_Ratio'] = (metrics['mean'] / metrics['std']) * np.sqrt(252)
df_master = pd.merge(metrics, df_funds, on='amfi_code', how='left')

def assign_risk(category):
    cat = str(category).upper()
    if 'DEBT' in cat or 'LIQUID' in cat or 'GILT' in cat:
        return 'Low'
    elif 'HYBRID' in cat or 'BALANCED' in cat or 'INDEX' in cat:
        return 'Moderate'
    else:
        return 'High' # Equity, Small Cap, Mid Cap, Sectoral, etc.

df_master['risk_grade'] = df_master['category'].apply(assign_risk)
def get_recommendations(risk_appetite, df):
    """
    Takes a risk appetite (Low, Moderate, High) and returns the top 3 funds by Sharpe Ratio.
    """
    risk = risk_appetite.capitalize()
    
    if risk not in ['Low', 'Moderate', 'High']:
        return " Error: Please enter 'Low', 'Moderate', or 'High'."
    
    filtered_funds = df[df['risk_grade'] == risk].copy()
    
    if filtered_funds.empty:
        print(f"\nNo funds found in the database for the [{risk}] Risk Profile.")
        return None
    
    top_3 = filtered_funds.sort_values(by='Sharpe_Ratio', ascending=False).head(3)
    result = top_3[['scheme_name', 'category', 'Sharpe_Ratio']].reset_index(drop=True)
    result.index = range(1, len(result) + 1) 
    
    print(f"\nTop Fund Recommendations for [{risk}] Risk Profile:")
    print(result)   
    return result
print(" Testing the Recommender Engine for all 3 profiles:")

get_recommendations('Low', df_master)
get_recommendations('Moderate', df_master)
get_recommendations('High', df_master)