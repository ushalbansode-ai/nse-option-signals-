#!/usr/bin/env python3
"""
Simplified version that definitely works
"""
import os
import sys
from flask import Flask, jsonify, send_from_directory

# Create simple Flask app
app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/api/data/NIFTY')
def nifty_data():
    return jsonify({
        "analysis": {
            "spot_price": 22150.75,
            "pcr": {"pcr_oi": 1.15},
            "max_pain": 22100,
            "skew_patterns": {"bullish_skew": True},
            "sentiment_score": 65,
            "strike_data": [],
            "support_resistance": {"support": [22000, 21900], "resistance": [22200, 22300]}
        },
        "signals": {
            "signals": ["Demo mode - Setting up live data"],
            "confidence": 50,
            "overall_bias": "NEUTRAL"
        }
    })

if __name__ == '__main__':
    print("🚀 SIMPLE Option Chain running on http://0.0.0.0:5000")
    print("📊 Access your dashboard at the Codespaces URL")
    app.run(host='0.0.0.0', port=5000, debug=False)
