import pandas as pd
import numpy as np

# --- CONFIGURATION ---
SIGNAL_MA = 61          
RSI_MIN = 55            
RSI_MAX = 65            
TREND_LONG = 200        
TREND_SHORT = 50        
MIN_VOLUME = 50000      

print("--- STARTING MASTER SCAN (FORCE FIX MODE) ---")

# 1. Helper: RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 2. Load and CLEAN Data
try:
    print("Loading database...", end=" ")
    df = pd.read_csv("all_stock_data.csv")
    
    # Clean Column Names
    df.columns = [c.strip() for c in df.columns]
    
    # --- CRITICAL FIX 1: Handle Date Format (07-Apr-2025) ---
    # We use %b for "Apr", "May", etc.
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y', errors='coerce')
    
    # If the above failed (resulting in NaT), try the number format just in case
    if df['Date'].isnull().all():
         df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    
    # --- CRITICAL FIX 2: Force Convert Prices to Numbers ---
    cols_to_fix = ['Close', 'Open', 'High', 'Low', 'Volume']
    
    for col in cols_to_fix:
        if col in df.columns:
            # Convert to string, remove commas, then convert to float
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows where data is bad (NaN)
    df.dropna(subset=['Close', 'Date'], inplace=True)
    
    # Sort data
    df = df.sort_values(by=['Symbol', 'Date'])
    
    print("Done.")
    print(f"Data Types Check:\n{df.dtypes}") # Proof it worked

except FileNotFoundError:
    print("\nError: 'all_stock_data.csv' not found.")
    exit()

# 3. Analysis Logic
def check_strategies(stock_df):
    # Need enough data
    if len(stock_df) < 200: return None, None

    # Calculate Indicators
    # We copy to avoid "SettingWithCopy" warnings
    stock_df = stock_df.copy()
    closes = stock_df['Close']
    
    # MAs
    ma_signal = closes.rolling(window=SIGNAL_MA).mean()
    ma_200 = closes.rolling(window=TREND_LONG).mean()
    ma_50 = closes.rolling(window=TREND_SHORT).mean()
    rsi = calculate_rsi(closes)
    
    # Get Today values
    today_close = closes.iloc[-1]
    today_rsi = rsi.iloc[-1]
    today_200 = ma_200.iloc[-1]
    today_50 = ma_50.iloc[-1]
    today_vol = stock_df['Volume'].iloc[-1]
    
    # Get Yesterday values
    prev_close = closes.iloc[-2]
    prev_signal_ma = ma_signal.iloc[-2]
    cur_signal_ma = ma_signal.iloc[-1]

    # Skip NaN
    if pd.isna(today_rsi) or pd.isna(today_200) or pd.isna(cur_signal_ma): 
        return None, None

    # Volume Filter
    if today_vol < MIN_VOLUME: return None, None

    # --- LOGIC 1: BUY SIGNAL ---
    signal_result = None
    crossed = (prev_close < prev_signal_ma) and (today_close > cur_signal_ma)
    rsi_ok = (today_rsi >= RSI_MIN) and (today_rsi <= RSI_MAX)
    
    if crossed and rsi_ok:
        signal_result = {
            'Symbol': stock_df['Symbol'].iloc[-1],
            'Close': today_close,
            'Date': stock_df['Date'].iloc[-1].strftime('%Y-%m-%d'),
            'Type': 'Buy Signal',
            'RSI': round(today_rsi, 2)
        }

    # --- LOGIC 2: UPTREND ---
    trend_result = None
    if (today_close > today_200) and (today_close > today_50):
        trend_result = {
            'Symbol': stock_df['Symbol'].iloc[-1],
            'Close': today_close,
            'SMA_50': round(today_50, 2),
            'SMA_200': round(today_200, 2)
        }

    return signal_result, trend_result

# 4. Run Scan
buy_signals = []
watchlist = []
grouped = df.groupby('Symbol')
total = len(grouped)

print(f"Scanning {total} stocks...")

for i, (symbol, stock_data) in enumerate(grouped):
    if i % 100 == 0: print(f"Scanning... [{i}/{total}]", end="\r")
    try:
        sig, trend = check_strategies(stock_data)
        if sig: buy_signals.append(sig)
        if trend: watchlist.append(trend)
    except Exception as e:
        # print(f"Skipping {symbol}: {e}") # Uncomment to see specific errors
        continue

print(f"Scanning... [{total}/{total}] - Done!      ")

# 5. Save Results
print("\n" + "="*40)
print(f"RESULTS REPORT")
print("="*40)

if buy_signals:
    df_sig = pd.DataFrame(buy_signals)
    df_sig.to_csv("buy_signals.csv", index=False)
    print(f" [!] FOUND {len(df_sig)} BUY SIGNALS")
    print(df_sig.to_string(index=False))
else:
    print(" [ ] No Buy Signals found today.")

print("-" * 40)

if watchlist:
    df_watch = pd.DataFrame(watchlist)
    df_watch.to_csv("uptrend_watchlist.csv", index=False)
    print(f" [i] Found {len(df_watch)} stocks in Strong Uptrend")
    # print(df_watch.head().to_string(index=False))
else:
    print(" [ ] No Uptrend stocks found.")