# fyers_data_api.py

import json
from datetime import datetime, timedelta
from fyers_api import fyersModel
from flask import jsonify

# --- IMPORTANT: Your Fyers API Credentials ---
# REPLACE with your actual IDs (I have your originals, but use the correct ones here)
CLIENT_ID = "J3PIUDQS20-10" 
TOKEN = "8TM69GG411" 

# Initialize the Fyers API Model
try:
    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID, 
        is_async=False, 
        token=TOKEN, 
        log_path="."
    )
except Exception as e:
    # Handle initialization failure gracefully
    print(f"Error initializing FyersModel: {e}")
    fyers = None


def fetch_and_format_chart_data(symbol_nse):
    """Fetches historical OHLCV data from Fyers and formats it for Lightweight Charts."""
    
    if not fyers:
        return []

    # Fyers requires the symbol in the format "NSE:SYMBOL-EQ"
    fyers_symbol = f"NSE:{symbol_nse}-EQ"
    
    # Calculate the date range (last 6 months / 180 days)
    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=180)

    # Convert datetime objects to Unix timestamps (in seconds) for the Fyers API
    data_params = {
        "symbol": fyers_symbol,
        "resolution": "D", # D for Daily candles (change to '60' for hourly, '1' for minute)
        "date_format": 1,
        "range_from": int(start_dt.timestamp()),
        "range_to": int(end_dt.timestamp()),
        "cont_flag": 1
    }
    
    response = fyers.history(data=data_params)
    
    chart_data_list = []
    if response and response.get('s') == 'ok' and 'candles' in response:
        for candle in response['candles']:
            # Fyers candle format: [timestamp, open, high, low, close, volume]
            
            # Convert timestamp (in seconds) to ISO format (YYYY-MM-DD) for the chart
            dt_object = datetime.fromtimestamp(candle[0])
            date_str = dt_object.strftime('%Y-%m-%d')
            
            chart_data_list.append({
                'time': date_str,
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                # 'volume': candle[5] # Volume can be added here if needed
            })
    
    return chart_data_list