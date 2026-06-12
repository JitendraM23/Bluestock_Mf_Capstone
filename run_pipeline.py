"""
Master Execution Script - Bluestock MF Capstone
This script sequentially executes the ETL pipeline, analytics, and recommender engine.
"""
import os

def run_script(script_name):
    print(f"\n[{'='*40}]")
    print(f"Executing: {script_name}...")
    # Using python3 or python depending on your OS alias
    os.system(f"python {script_name}")
    print(f" Finished: {script_name}")

if __name__ == "__main__":
    print("🌟 Starting Bluestock MF Master Pipeline 🌟")
    
    # List the scripts you created throughout the week in order of execution
    scripts = [
        "etl_pipeline.py",       # Day 2/3 Script
        "advanced_analytics.py", # Day 6 Script (VaR, Sharpe, Cohorts)
        "recommender.py"         # Day 6 Script (Fund Recommender)
    ]
    
    for script in scripts:
        # Check if the file exists before running
        if os.path.exists(script):
            run_script(script)
        else:
            print(f" Warning: {script} not found in current directory. Skipping.")
            
    print("\n Pipeline Execution Complete! Database and reports are up to date.")