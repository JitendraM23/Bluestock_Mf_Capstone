import os
import time
import requests
import pandas as pd


RAW_DATA_DIR = os.path.join("data", "raw")


TARGET_SCHEMES = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

def fetch_and_save_nav():
    print(" Starting Live API Data Fetching\n")
    
    for amfi_code, fund_name in TARGET_SCHEMES.items():
        print(f"Fetching {fund_name} Code: {amfi_code}")
        
        api_url = f"https://api.mfapi.in/mf/{amfi_code}"
        
        try:
            response = requests.get(api_url)
            
            if response.status_code == 200:
                json_response = response.json()
                nav_records = json_response.get("data", [])
                
                if nav_records:
                   
                    dataf = pd.DataFrame(nav_records)
                    dataf['amfi_code'] = amfi_code
                    file_name = f"{fund_name}:{amfi_code}.csv"
                    file_path = os.path.join(RAW_DATA_DIR, file_name)
                    dataf.to_csv(file_path, index=False)
                    
                    print(f"Success! Saved {len(dataf)} rows to {file_name}\n")
                else:
                    print(f"No data found inside the JSON for {fund_name}\n")
            else:
                print(f"API Error for {fund_name}. Status Code: {response.status_code}\n")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Connection Error for {fund_name}: {e}\n")

if __name__ == "__main__":
    fetch_and_save_nav()