import pandas as pd

try:
    print("Reading data file...")
    df = pd.read_csv("all_stock_data.csv")
    
    # Check 1: How many rows?
    print(f"Total Rows: {len(df)}")
    
    # Check 2: How many unique stocks?
    # It should be around 1500 to 2200.
    num_stocks = len(df['Symbol'].unique())
    print(f"Unique Stocks: {num_stocks}")
    
    if num_stocks > 3000:
        print("WARNING: Too many stocks detected. Something is wrong.")
    else:
        print("SUCCESS: Data looks correct!")
        
except Exception as e:
    print(f"Error: {e}")