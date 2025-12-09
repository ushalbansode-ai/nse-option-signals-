"""
Configuration settings for NSE Option Chain Analyzer
"""

class NSEConfig:
    """NSE API Configuration"""
    
    # Base URLs
    BASE_URL = "https://www.nseindia.com"
    OPTION_CHAIN_URL = f"{BASE_URL}/api/option-chain-indices"
    OPTION_CHAIN_EQUITY_URL = f"{BASE_URL}/api/option-chain-equities"
    
    # Supported symbols
    INDEX_SYMBOLS = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
    
    # Rate limiting (seconds)
    MIN_REQUEST_DELAY = 3
    MAX_REQUEST_DELAY = 5
    
    # Request timeout
    REQUEST_TIMEOUT = 15
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 5


class AnalysisConfig:
    """Analysis configuration"""
    
    # PCR thresholds
    PCR_BULLISH_THRESHOLD = 1.3
    PCR_BEARISH_THRESHOLD = 0.7
    
    # IV Skew thresholds
    IV_SKEW_EXTREME = 15
    IV_SKEW_MODERATE = 10
    
    # Liquidity thresholds
    MIN_VOLUME = 5000
    MAX_SPREAD_PCT = 5
    MIN_LIQUID_STRIKES = 5
    
    # Volume/OI ratio thresholds
    HIGH_ACTIVITY_RATIO = 0.5
    MODERATE_ACTIVITY_RATIO = 0.3


class TradingConfig:
    """Trading configuration"""
    
    # Default risk settings
    DEFAULT_CAPITAL = 100000
    DEFAULT_RISK_PER_TRADE = 2.0
    MAX_RISK_PER_TRADE = 5.0
    
    # Position sizing
    MAX_POSITION_SIZE_PCT = 25
    MIN_LOTS = 1
    
    # Lot sizes
    LOT_SIZES = {
        'NIFTY': 50,
        'BANKNIFTY': 15,
        'FINNIFTY': 40,
        'MIDCPNIFTY': 75
    }
    
    # Strike selection
    STRIKE_GAPS = {
        'NIFTY': 50,
        'BANKNIFTY': 100,
        'FINNIFTY': 50,
        'MIDCPNIFTY': 25
    }
