import pandas as pd
import numpy as np
from collections import deque

class OptionAnalytics:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        
    def calculate_oi_skew(self, strike_data):
        """Calculate OI skew between CE and PE for each strike"""
        for strike in strike_data:
            total_oi = strike['ce_oi'] + strike['pe_oi']
            if total_oi > 0:
                strike['oi_skew'] = (strike['ce_oi'] - strike['pe_oi']) / total_oi
                strike['oi_skew_absolute'] = strike['ce_oi'] - strike['pe_oi']
            else:
                strike['oi_skew'] = 0
                strike['oi_skew_absolute'] = 0
        return strike_data
    
    def volume_oi_efficiency(self, strike_data, avg_volume_window=5):
        """Calculate volume to OI efficiency ratio"""
        for strike in strike_data:
            # CE Volume-OI efficiency
            if strike['ce_oi'] > 0:
                strike['ce_volume_oi_ratio'] = strike['ce_volume'] / strike['ce_oi']
            else:
                strike['ce_volume_oi_ratio'] = 0
                
            # PE Volume-OI efficiency
            if strike['pe_oi'] > 0:
                strike['pe_volume_oi_ratio'] = strike['pe_volume'] / strike['pe_oi']
            else:
                strike['pe_volume_oi_ratio'] = 0
                
        return strike_data
    
    def identify_buildup(self, strike_data):
        """Identify fresh long/short buildup"""
        for strike in strike_data:
            # CE Buildup
            if strike['ce_change_oi'] > 0 and strike['ce_last_price'] > 0:
                if strike['ce_change_oi'] > 1000:  # Threshold
                    strike['ce_buildup'] = 'LONG' if strike['ce_last_price'] > 0 else 'SHORT'
                else:
                    strike['ce_buildup'] = 'NEUTRAL'
            else:
                strike['ce_buildup'] = 'NEUTRAL'
                
            # PE Buildup
            if strike['pe_change_oi'] > 0 and strike['pe_last_price'] > 0:
                if strike['pe_change_oi'] > 1000:  # Threshold
                    strike['pe_buildup'] = 'LONG' if strike['pe_last_price'] > 0 else 'SHORT'
                else:
                    strike['pe_buildup'] = 'NEUTRAL'
            else:
                strike['pe_buildup'] = 'NEUTRAL'
                
        return strike_data
    
    def calculate_pcr(self, strike_data):
        """Calculate Put-Call Ratio"""
        total_ce_oi = sum(strike['ce_oi'] for strike in strike_data)
        total_pe_oi = sum(strike['pe_oi'] for strike in strike_data)
        total_ce_volume = sum(strike['ce_volume'] for strike in strike_data)
        total_pe_volume = sum(strike['pe_volume'] for strike in strike_data)
        
        pcr_oi = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        pcr_volume = total_pe_volume / total_ce_volume if total_ce_volume > 0 else 0
        
        return {
            'pcr_oi': pcr_oi,
            'pcr_volume': pcr_volume,
            'total_ce_oi': total_ce_oi,
            'total_pe_oi': total_pe_oi
        }
    
    def find_max_pain(self, strike_data):
        """Calculate Max Pain point"""
        max_pain = None
        min_loss = float('inf')
        
        for strike in strike_data:
            total_loss = 0
            for s in strike_data:
                if s['strike'] < strike['strike']:
                    total_loss += s['ce_oi'] * (strike['strike'] - s['strike'])
                elif s['strike'] > strike['strike']:
                    total_loss += s['pe_oi'] * (s['strike'] - strike['strike'])
            
            if total_loss < min_loss:
                min_loss = total_loss
                max_pain = strike['strike']
                
        return max_pain
    
    def analyze_skew_patterns(self, strike_data, spot_price):
        """Analyze OI skew patterns for trading signals"""
        atm_strikes = [s for s in strike_data if abs(s['strike'] - spot_price) <= 100]
        otm_ce = [s for s in strike_data if s['strike'] > spot_price + 200]
        otm_pe = [s for s in strike_data if s['strike'] < spot_price - 200]
        
        # Bullish signal: High CE OI at higher strikes + Low PE OI at lower strikes
        avg_ce_oi_otm = sum(s['ce_oi'] for s in otm_ce) / len(otm_ce) if otm_ce else 0
        avg_pe_oi_otm = sum(s['pe_oi'] for s in otm_pe) / len(otm_pe) if otm_pe else 0
        
        return {
            'bullish_skew': avg_ce_oi_otm > avg_pe_oi_otm * 1.2,
            'bearish_skew': avg_pe_oi_otm > avg_ce_oi_otm * 1.2,
            'neutral_skew': True
        }
