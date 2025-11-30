"""
Core Option Chain Analysis Module
Contains the main OptionChain class that orchestrates the analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from nse_data import NSEDataFetcher, DataProcessor
from analytics import OptionAnalytics

class OptionChain:
    """
    Main class for option chain analysis that coordinates between
    data fetching, processing, and analytics
    """
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ['NIFTY', 'BANKNIFTY']
        self.fetcher = NSEDataFetcher()
        self.processor = DataProcessor()
        self.analytics = OptionAnalytics()
        
        # Data storage
        self.current_data = {symbol: None for symbol in self.symbols}
        self.historical_data = {symbol: [] for symbol in self.symbols}
        self.max_historical_points = 100
        
        self.logger = logging.getLogger(__name__)
        
    def fetch_all_chains(self) -> Dict:
        """
        Fetch option chain data for all symbols
        Returns: Dictionary with symbol as key and processed data as value
        """
        results = {}
        
        for symbol in self.symbols:
            try:
                self.logger.info(f"Fetching option chain for {symbol}")
                
                # Fetch raw data from NSE
                raw_data = self.fetcher.fetch_option_chain(symbol)
                if not raw_data:
                    self.logger.warning(f"No data received for {symbol}")
                    continue
                
                # Process the raw data
                processed_data = self.processor.process_option_chain(raw_data, symbol)
                if not processed_data:
                    self.logger.warning(f"Failed to process data for {symbol}")
                    continue
                
                # Perform advanced analytics
                analyzed_data = self._perform_analytics(processed_data)
                
                # Store current data
                self.current_data[symbol] = analyzed_data
                
                # Update historical data
                self._update_historical_data(symbol, analyzed_data)
                
                results[symbol] = analyzed_data
                self.logger.info(f"Successfully processed {symbol}")
                
            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")
                results[symbol] = None
        
        return results
    
    def _perform_analytics(self, processed_data: Dict) -> Dict:
        """
        Perform comprehensive analytics on processed option chain data
        """
        strike_data = processed_data['strike_data']
        spot_price = processed_data['spot_price']
        
        # Apply all analytics
        strike_data = self.analytics.calculate_oi_skew(strike_data)
        strike_data = self.analytics.volume_oi_efficiency(strike_data)
        strike_data = self.analytics.identify_buildup(strike_data)
        
        # Calculate aggregate metrics
        pcr_data = self.analytics.calculate_pcr(strike_data)
        max_pain = self.analytics.find_max_pain(strike_data)
        skew_patterns = self.analytics.analyze_skew_patterns(strike_data, spot_price)
        
        # Add support/resistance levels based on OI
        support_resistance = self._calculate_support_resistance(strike_data, spot_price)
        
        # Calculate market sentiment score
        sentiment_score = self._calculate_sentiment_score(
            pcr_data, skew_patterns, strike_data, spot_price
        )
        
        return {
            **processed_data,
            'analysis': {
                'pcr': pcr_data,
                'max_pain': max_pain,
                'skew_patterns': skew_patterns,
                'support_resistance': support_resistance,
                'sentiment_score': sentiment_score,
                'strike_data': strike_data,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _calculate_support_resistance(self, strike_data: List, spot_price: float) -> Dict:
        """
        Calculate support and resistance levels based on OI concentrations
        """
        # Find strikes with highest OI for calls and puts
        high_ce_oi_strikes = sorted(
            strike_data, 
            key=lambda x: x['ce_oi'], 
            reverse=True
        )[:5]
        
        high_pe_oi_strikes = sorted(
            strike_data, 
            key=lambda x: x['pe_oi'], 
            reverse=True
        )[:5]
        
        # Resistance: High CE OI above spot
        resistance_levels = [
            strike['strike'] for strike in high_ce_oi_strikes 
            if strike['strike'] > spot_price
        ]
        
        # Support: High PE OI below spot
        support_levels = [
            strike['strike'] for strike in high_pe_oi_strikes 
            if strike['strike'] < spot_price
        ]
        
        return {
            'support': sorted(support_levels)[-3:],  # Top 3 support levels
            'resistance': sorted(resistance_levels)[:3],  # Top 3 resistance levels
            'strong_support': min(support_levels) if support_levels else None,
            'strong_resistance': max(resistance_levels) if resistance_levels else None
        }
    
    def _calculate_sentiment_score(self, pcr_data: Dict, skew_patterns: Dict, 
                                 strike_data: List, spot_price: float) -> float:
        """
        Calculate a comprehensive market sentiment score (0-100)
        """
        score = 50  # Neutral starting point
        
        # PCR-based sentiment (0-30 points)
        pcr = pcr_data['pcr_oi']
        if pcr > 1.4:
            score += 15  # Strong bullish
        elif pcr > 1.1:
            score += 8   # Mild bullish
        elif pcr < 0.6:
            score -= 15  # Strong bearish
        elif pcr < 0.9:
            score -= 8   # Mild bearish
        
        # OI Skew sentiment (0-30 points)
        if skew_patterns['bullish_skew']:
            score += 15
        elif skew_patterns['bearish_skew']:
            score -= 15
        
        # Buildup pattern sentiment (0-20 points)
        ce_buildups = sum(1 for s in strike_data if s.get('ce_buildup') == 'LONG')
        pe_buildups = sum(1 for s in strike_data if s.get('pe_buildup') == 'LONG')
        
        if ce_buildups > pe_buildups + 5:
            score += 10  # More call buying
        elif pe_buildups > ce_buildups + 5:
            score -= 10  # More put buying
        
        # Volume-OI efficiency (0-20 points)
        high_efficiency_strikes = sum(
            1 for s in strike_data 
            if s.get('ce_volume_oi_ratio', 0) > 0.5 or s.get('pe_volume_oi_ratio', 0) > 0.5
        )
        if high_efficiency_strikes > 10:
            score += 10  # High conviction trading
        
        return max(0, min(100, score))
    
    def _update_historical_data(self, symbol: str, current_data: Dict):
        """
        Maintain a rolling window of historical data
        """
        if symbol not in self.historical_data:
            self.historical_data[symbol] = []
        
        # Add current data point
        self.historical_data[symbol].append({
            'timestamp': datetime.now(),
            'spot_price': current_data['spot_price'],
            'pcr_oi': current_data['analysis']['pcr']['pcr_oi'],
            'sentiment_score': current_data['analysis']['sentiment_score'],
            'max_pain': current_data['analysis']['max_pain']
        })
        
        # Keep only recent data points
        if len(self.historical_data[symbol]) > self.max_historical_points:
            self.historical_data[symbol] = self.historical_data[symbol][-self.max_historical_points:]
    
    def get_trading_signals(self, symbol: str) -> Dict:
        """
        Generate trading signals based on current analysis
        """
        if symbol not in self.current_data or not self.current_data[symbol]:
            return {}
        
        data = self.current_data[symbol]
        analysis = data['analysis']
        
        signals = []
        confidence = 0
        
        # Signal 1: PCR Extreme
        if analysis['pcr']['pcr_oi'] > 1.4:
            signals.append("PCR indicates oversold - Potential BUY signal")
            confidence += 25
        elif analysis['pcr']['pcr_oi'] < 0.6:
            signals.append("PCR indicates overbought - Potential SELL signal")
            confidence += 25
        
        # Signal 2: OI Skew
        if analysis['skew_patterns']['bullish_skew']:
            signals.append("OI Skew suggests bullish bias")
            confidence += 20
        elif analysis['skew_patterns']['bearish_skew']:
            signals.append("OI Skew suggests bearish bias")
            confidence += 20
        
        # Signal 3: Max Pain vs Spot
        if data['spot_price'] > analysis['max_pain']:
            signals.append("Spot above Max Pain - Mildly Bearish")
            confidence += 15
        else:
            signals.append("Spot below Max Pain - Mildly Bullish")
            confidence += 15
        
        # Signal 4: Support/Resistance Breakout
        strong_resistance = analysis['support_resistance']['strong_resistance']
        strong_support = analysis['support_resistance']['strong_support']
        
        if strong_resistance and data['spot_price'] > strong_resistance:
            signals.append("Breaking strong resistance - BULLISH")
            confidence += 20
        elif strong_support and data['spot_price'] < strong_support:
            signals.append("Breaking strong support - BEARISH")
            confidence += 20
        
        # Signal 5: Sentiment Score
        sentiment = analysis['sentiment_score']
        if sentiment > 70:
            signals.append("Strong bullish sentiment")
            confidence += 20
        elif sentiment < 30:
            signals.append("Strong bearish sentiment")
            confidence += 20
        
        return {
            'signals': signals,
            'confidence': min(100, confidence),
            'overall_bias': 'BULLISH' if sentiment > 60 else 'BEARISH' if sentiment < 40 else 'NEUTRAL',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_symbol_data(self, symbol: str) -> Optional[Dict]:
        """Get current data for a specific symbol"""
        return self.current_data.get(symbol)
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        return self.symbols

# Singleton instance
option_chain_analyzer = OptionChain()
