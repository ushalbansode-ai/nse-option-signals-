import os
from datetime import time

class Config:
    SYMBOLS = ['NIFTY', 'BANKNIFTY']
    REFRESH_INTERVAL = 30  # seconds
    NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={}"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Trading hours
    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)
