import pandas as pd

print("--- DIAGNOSTIC MODE ---")
try:
    # Load just the first 5 rows
    df = pd.read_csv("all_stock_data.csv")
    
    print(f"Total Rows found: {len(df)}")
    print(f"Columns found: {list(df.columns)}")
    
    print("\n--- FIRST 5 ROWS ---")
    print(df.head())
    
    print("\n--- CHECKING SYMBOLS ---")
    unique_symbols = df['Symbol'].unique()
    print(f"Number of Unique Symbols: {len(unique_symbols)}")
    print(f"First 5 Symbols: {unique_symbols[:5]}")

except Exception as e:
    print("Error reading file:", e)