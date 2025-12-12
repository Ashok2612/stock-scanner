import pandas as pd
import nselib
from nselib import capital_market

print("Connecting to NSE to fetch stock list...")
try:
    # 1. Fetch the raw data
    df_all_stocks = capital_market.equity_list()
    
    # 2. FIX: Remove hidden spaces from column names
    # This turns ' SERIES' into 'SERIES'
    df_all_stocks.columns = [c.strip() for c in df_all_stocks.columns]

    # 3. Filter for only normal stocks (Series 'EQ')
    df_active = df_all_stocks[df_all_stocks['SERIES'] == 'EQ']
    
    # 4. Select useful columns
    master_list = df_active[['SYMBOL', 'NAME OF COMPANY', 'FACE VALUE']]
    
    # 5. Save to CSV
    master_list.to_csv("master_stock_list.csv", index=False)
    
    print(f"Success! Found {len(master_list)} active stocks.")
    print("Saved master list to: master_stock_list.csv")
    print(master_list.head())

except Exception as e:
    print("Error:", e)