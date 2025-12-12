import pandas as pd

print("--- CHECKING DATA TYPES ---")
try:
    df = pd.read_csv("all_stock_data.csv")
    
    # Get the first Close price
    first_price = df['Close'].iloc[0]
    
    print(f"Sample Price Value: {first_price}")
    print(f"Computer sees it as: {type(first_price)}")
    
    if isinstance(first_price, str):
        print("\n[!] PROBLEM FOUND: The prices are text (Strings).")
        print("    We need to remove commas and convert to numbers.")
    else:
        print("\n[OK] The prices are numbers (Float/Int).")

except Exception as e:
    print("Error:", e)