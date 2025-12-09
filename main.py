"""
Main Entry Point for NSE Option Chain Analyzer
"""

import logging
from datetime import datetime
from src.data_fetcher import NSEDataFetcher
from src.analyzer import OptionChainAnalyzer
from src.indicators import OptionIndicators
from src.strategies import StrategyGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main analysis function"""
    
    print("\n" + "="*70)
    print("NSE OPTION CHAIN ANALYZER")
    print("="*70)
    
    # Initialize components
    fetcher = NSEDataFetcher()
    analyzer = OptionChainAnalyzer()
    indicators = OptionIndicators()
    
    # Fetch data
    symbol = 'NIFTY'
    print(f"\nFetching data for {symbol}...")
    raw_data = fetcher.fetch_option_chain(symbol)
    
    if not raw_data:
        print("✗ Failed to fetch data")
        return
    
    # Parse data
    df = analyzer.parse_option_data(raw_data)
    spot_price = fetcher.get_spot_price(raw_data)
    
    print(f"✓ Data fetched successfully")
    print(f"Spot Price: ₹{spot_price:.2f}")
    
    # Perform analysis
    print("\nAnalyzing...")
    pcr_oi, pcr_vol = analyzer.calculate_pcr(df)
    max_pain = analyzer.calculate_max_pain(df)
    oi_changes = analyzer.analyze_oi_changes(df)
    iv_skew = indicators.calculate_iv_skew(df, spot_price)
    liquidity = indicators.analyze_liquidity(df)
    volume_oi = indicators.calculate_volume_oi_ratio(df)
    levels = indicators.find_support_resistance(df)
    
    # Compile analysis
    analysis = {
        'pcr': {'oi': pcr_oi, 'volume': pcr_vol},
        'max_pain': max_pain,
        'oi_changes': oi_changes,
        'iv_skew': iv_skew,
        'liquidity': liquidity,
        'volume_oi_ratio': volume_oi,
        'support_resistance': levels
    }
    
    # Generate strategies
    strategy_gen = StrategyGenerator(analysis, symbol, spot_price)
    strategies = strategy_gen.generate_all_strategies()
    
    # Print results
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    print(f"\n📊 PCR: OI={pcr_oi}, Volume={pcr_vol}")
    print(f"🎯 Max Pain: ₹{max_pain}")
    print(f"🎭 IV Skew: {iv_skew['interpretation']} ({iv_skew['put_skew']}% put skew)")
    print(f"💧 Liquidity: {liquidity['recommendation']}")
    print(f"🛡️ Support: {levels['support_levels']}")
    print(f"⚡ Resistance: {levels['resistance_levels']}")
    
    print("\n🚨 TRADING STRATEGIES:")
    if strategies:
        for i, strategy in enumerate(strategies, 1):
            print(f"\n{i}. {strategy['name']}")
            print(f"   Type: {strategy['type']}")
            print(f"   Rationale: {strategy['rationale']}")
            print(f"   Confidence: {strategy['confidence']}")
    else:
        print("No strategies triggered")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
