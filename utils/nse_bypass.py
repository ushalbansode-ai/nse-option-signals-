"""
NSE Bypass Utilities
Handles headers and session management to avoid blocking
"""

import requests
import logging

logger = logging.getLogger(__name__)


class NSEBypass:
    """
    Manages NSE anti-blocking measures
    """
    
    # Headers to mimic browser
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Referer': 'https://www.nseindia.com/option-chain'
    }
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.session.headers.update(self.HEADERS)
    
    def get_cookies(self) -> bool:
        """Get session cookies from NSE"""
        try:
            url = "https://www.nseindia.com"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✓ Successfully obtained NSE cookies")
                return True
            else:
                logger.error(f"Failed to get cookies: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting cookies: {str(e)}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    session = requests.Session()
    bypass = NSEBypass(session)
    bypass.get_cookies()
