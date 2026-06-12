# Bluestock Mutual Fund Analytics Capstone

## Project Overview
An end-to-end data engineering and business intelligence project. This repository contains the ETL pipelines, predictive risk algorithms (VaR, Rolling Sharpe, Churn Prediction), and a Star Schema database used to power a comprehensive Power BI executive dashboard.

## Dataset Description
The data encompasses mutual fund metadata, daily historical NAV pricing, investor transaction logs (SIP/Lumpsum), and total AUM metrics spanning multiple years.

## Setup Instructions
1. Clone this repository to your local machine.
2. Ensure Python 3.x is installed.
3. Install required libraries: `pip install pandas numpy matplotlib sqlite3`

## How to Run the Pipeline
To execute the ETL cleaning, database ingestion, and advanced analytics models in sequence, run the master script from your terminal:
`python run_pipeline.py`

## How to Open the Dashboard
1. Ensure you have Microsoft Power BI Desktop installed.
2. Open the file `bluestock_mf_dashboard.pbix` located in the root directory.
3. If prompted, refresh the data sources to point to your local `bluestock_mf.db` SQLite file.