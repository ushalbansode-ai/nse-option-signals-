from option_chain import option_chain_analyzer
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import json

from nse_data import NSEDataFetcher, DataProcessor
from analytics import OptionAnalytics
from config import Config

app = Flask(__name__)
CORS(app)

# Global data storage
market_data = {
    'NIFTY': {'data': None, 'timestamp': None, 'analysis': None},
    'BANKNIFTY': {'data': None, 'timestamp': None, 'analysis': None}
}

fetcher = NSEDataFetcher()
processor = DataProcessor()
analytics = OptionAnalytics()

def fetch_and_process_data():
    """Fetch and process data for all symbols"""
    print(f"Fetching data at {datetime.now()}")
    
    for symbol in Config.SYMBOLS:
        try:
            # Fetch raw data
            raw_data = fetcher.fetch_option_chain(symbol)
            if raw_data:
                # Process data
                processed_data = processor.process_option_chain(raw_data, symbol)
                if processed_data:
                    # Perform analytics
                    strike_data = processed_data['strike_data']
                    strike_data = analytics.calculate_oi_skew(strike_data)
                    strike_data = analytics.volume_oi_efficiency(strike_data)
                    strike_data = analytics.identify_buildup(strike_data)
                    
                    pcr_data = analytics.calculate_pcr(strike_data)
                    max_pain = analytics.find_max_pain(strike_data)
                    skew_patterns = analytics.analyze_skew_patterns(
                        strike_data, processed_data['spot_price']
                    )
                    
                    analysis = {
                        'pcr': pcr_data,
                        'max_pain': max_pain,
                        'skew_patterns': skew_patterns,
                        'strike_data': strike_data,
                        'spot_price': processed_data['spot_price'],
                        'timestamp': processed_data['timestamp']
                    }
                    
                    market_data[symbol] = {
                        'data': processed_data,
                        'analysis': analysis,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    print(f"Updated {symbol} data")
                    
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data/<symbol>')
def get_symbol_data(symbol):
    if symbol in market_data and market_data[symbol]['analysis']:
        return jsonify(market_data[symbol]['analysis'])
    return jsonify({'error': 'Data not available'}), 404

@app.route('/api/dashboard')
def get_dashboard():
    dashboard_data = {}
    for symbol in Config.SYMBOLS:
        if market_data[symbol]['analysis']:
            dashboard_data[symbol] = market_data[symbol]['analysis']
    return jsonify(dashboard_data)

@app.route('/api/health')
def health():
    status = {}
    for symbol in Config.SYMBOLS:
        status[symbol] = {
            'last_update': market_data[symbol]['timestamp'],
            'data_available': market_data[symbol]['data'] is not None
        }
    return jsonify(status)

if __name__ == '__main__':
    # Initial data fetch
    fetch_and_process_data()
    
    # Setup scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=fetch_and_process_data,
        trigger="interval",
        seconds=Config.REFRESH_INTERVAL,
        id='data_fetcher'
    )
    scheduler.start()
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
