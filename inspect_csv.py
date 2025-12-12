import pandas as pd

print("--- INSPECTING DATA FILE ---")
try:
    # Read the first 5 rows only
    df = pd.read_csv("all_stock_data.csv")
    
    print("\n[1] The Columns are:")
    print(list(df.columns))
    
    print("\n[2] The First 5 Rows of data:")
    print(df.head().to_string())

except Exception as e:
    print("Error:", e)