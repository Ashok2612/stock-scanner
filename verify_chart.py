import pandas as pd
import mplfinance as mpf

# --- CONFIGURATION ---
SYMBOL = "ABB"          
DAYS_TO_SHOW = 100      
MA_PERIOD = 61          

try:
    print(f"Generating chart for {SYMBOL}...")
    
    # 1. Load Data
    df = pd.read_csv("all_stock_data.csv")
    df.columns = [c.strip() for c in df.columns]
    
    # 2. Filter for Stock
    stock_df = df[df['Symbol'] == SYMBOL].copy()
    
    # 3. FIX: Handle Dates
    stock_df['Date'] = pd.to_datetime(stock_df['Date'], format='%d-%b-%Y', errors='coerce')
    if stock_df['Date'].isnull().all():
         stock_df['Date'] = pd.to_datetime(stock_df['Date'], format='%d-%m-%Y', errors='coerce')

    # 4. FIX: Handle Commas in Prices (The "Numeric Types" Error)
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in cols:
        stock_df[col] = stock_df[col].astype(str).str.replace(',', '', regex=False)
        stock_df[col] = pd.to_numeric(stock_df[col], errors='coerce')

    # 5. Prepare for Plot
    stock_df = stock_df.set_index('Date')
    stock_df = stock_df.sort_index()
    recent_data = stock_df.tail(DAYS_TO_SHOW)
    
    # 6. Calculate MA
    # (Calculate on full data first for accuracy)
    stock_df['MA_61'] = stock_df['Close'].rolling(window=MA_PERIOD).mean()
    
    # 7. Plot
    mpf.plot(
        recent_data,
        type='candle',
        style='charles',
        title=f"{SYMBOL} - Swing Setup (61 SMA)",
        ylabel='Price (INR)',
        volume=True,
        mav=(MA_PERIOD), 
        savefig=f"{SYMBOL}_chart.png"
    )
    
    print(f"Success! Chart saved as: {SYMBOL}_chart.png")

except Exception as e:
    print("Error:", e)