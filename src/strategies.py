"""
Trading Strategies Module
Generates trading strategies based on analysis
"""

from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TradingConfig, AnalysisConfig


class StrategyGenerator:
    """
    Generates actionable trading strategies
    """
    
    def __init__(self, analysis: Dict, symbol: str, spot_price: float):
        self.analysis = analysis
        self.symbol = symbol
        self.spot_price = spot_price
    
    def generate_all_strategies(self) -> List[Dict]:
        """Generate all applicable strategies"""
        strategies = []
        
        # Check each strategy
        if strategy := self.pcr_extreme_strategy():
            strategies.append(strategy)
        
        if strategy := self.iv_skew_strategy():
            strategies.append(strategy)
        
        if strategy := self.oi_momentum_strategy():
            strategies.append(strategy)
        
        return strategies
    
    def pcr_extreme_strategy(self) -> Optional[Dict]:
        """Strategy based on extreme PCR"""
        pcr_oi = self.analysis['pcr']['oi']
        
        if pcr_oi > AnalysisConfig.PCR_BULLISH_THRESHOLD:
            return {
                'name': 'PCR Extreme - Bullish',
                'type': 'CALL_BUY',
                'rationale': f'High PCR ({pcr_oi}) indicates oversold conditions',
                'confidence': 'HIGH',
                'timeframe': '1-3 days'
            }
        elif pcr_oi < AnalysisConfig.PCR_BEARISH_THRESHOLD:
            return {
                'name': 'PCR Extreme - Bearish',
                'type': 'PUT_BUY',
                'rationale': f'Low PCR ({pcr_oi}) indicates overbought conditions',
                'confidence': 'HIGH',
                'timeframe': '1-3 days'
            }
        return None
    
    def iv_skew_strategy(self) -> Optional[Dict]:
        """Strategy based on IV skew"""
        iv_skew = self.analysis['iv_skew']
        liquidity = self.analysis['liquidity']
        
        if liquidity['recommendation'] != 'Good':
            return None
        
        if abs(iv_skew['put_skew']) > AnalysisConfig.IV_SKEW_EXTREME:
            direction = 'CALL_BUY' if iv_skew['put_skew'] > 0 else 'PUT_BUY'
            return {
                'name': 'IV Skew Reversal',
                'type': direction,
                'rationale': f'{abs(iv_skew["put_skew"])}% skew indicates opportunity',
                'confidence': 'MEDIUM',
                'timeframe': 'Intraday to 2 days'
            }
        return None
    
    def oi_momentum_strategy(self) -> Optional[Dict]:
        """Strategy based on OI changes"""
        oi_changes = self.analysis['oi_changes']
        vol_oi = self.analysis['volume_oi_ratio']
        
        if vol_oi['interpretation'] != 'High momentum':
            return None
        
        if oi_changes['call_build'] and not oi_changes['put_build']:
            return {
                'name': 'OI Momentum - Call Writing Detected',
                'type': 'PUT_BUY',
                'rationale': 'Heavy call writing indicates selling pressure',
                'confidence': 'MEDIUM',
                'timeframe': 'Intraday'
            }
        elif oi_changes['put_build'] and not oi_changes['call_build']:
            return {
                'name': 'OI Momentum - Put Writing Detected',
                'type': 'CALL_BUY',
                'rationale': 'Heavy put writing indicates support',
                'confidence': 'MEDIUM',
                'timeframe': 'Intraday'
            }
        return None


if __name__ == "__main__":
    print("Strategies module loaded successfully")
