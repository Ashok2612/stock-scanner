import pandas as pd
from nselib import capital_market
from datetime import date, timedelta
import time
import os

# --- CONFIGURATION ---
DAYS_HISTORY = 300  # Enough for 200 SMA
BATCH_SIZE = 50     # Save every 50 stocks
OUTPUT_FILE = "all_stock_data.csv"

# Dates
today = date.today().strftime("%d-%m-%Y")
start_date = (date.today() - timedelta(days=DAYS_HISTORY)).strftime("%d-%m-%Y")

print(f"--- STARTING DOWNLOAD ---")
print(f"Fetching data from {start_date} to {today}")

# 1. Load Master List
try:
    df_master = pd.read_csv("master_stock_list.csv")
    symbols = df_master['SYMBOL'].tolist()
    print(f"Found {len(symbols)} stocks to fetch.")
except Exception as e:
    print("Error: master_stock_list.csv not found. Run fetch_master_list.py first.")
    exit()

# 2. Check Resume Status
if os.path.exists(OUTPUT_FILE):
    existing = pd.read_csv(OUTPUT_FILE)
    processed = existing['Symbol'].unique().tolist()
    print(f"Resuming... Skipping {len(processed)} stocks already downloaded.")
    symbols = [s for s in symbols if s not in processed]
else:
    # Create file with STRICT headers
    with open(OUTPUT_FILE, 'w') as f:
        f.write("Symbol,Date,Open,High,Low,Close,Volume\n")

current_batch = []

# 3. Main Loop
for i, symbol in enumerate(symbols):
    print(f"Fetching {symbol} [{i+1}/{len(symbols)}]...", end=" ")
    
    try:
        # Fetch raw data
        data = capital_market.price_volume_and_deliverable_position_data(
            symbol=symbol, 
            from_date=start_date, 
            to_date=today
        )
        
        if data is None or data.empty:
            print("No Data.")
            continue

        # --- THE FIX: SELECT & RENAME COLUMNS ---
        # NSELib returns many columns. We pick only what we need.
        # We also handle different naming conventions if they change.
        
        # 1. Normalize column names (remove spaces, proper case)
        data.columns = [c.strip() for c in data.columns]
        
        # 2. Add Symbol column
        data['Symbol'] = symbol
        
        # 3. Select specific columns (using nselib standard names)
        # Note: 'TotalTradedQuantity' is Volume. 'ClosePrice' is Close.
        subset = data[['Symbol', 'Date', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'TotalTradedQuantity']].copy()
        
        # 4. Rename to match our CSV Header
        subset.columns = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        
        # Add to batch
        current_batch.append(subset)
        print("Done.")

    except Exception as e:
        print(f"Failed ({e})")

    # Save Batch
    if len(current_batch) >= BATCH_SIZE:
        print(f"--- Saving batch of {len(current_batch)} ---")
        pd.concat(current_batch).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
        current_batch = []
        time.sleep(1)

# Final Save
if current_batch:
    pd.concat(current_batch).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)

print("\nDOWNLOAD COMPLETE!")