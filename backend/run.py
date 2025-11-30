#!/usr/bin/env python3
"""
Main entry point for Option Chain Analyzer
Run this file to start the application
"""
import os
import sys
import logging
import socket
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_port_available(port=5000):
    """Check if port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_available_port(start_port=5000):
    """Find an available port starting from start_port"""
    port = start_port
    while port < start_port + 10:
        if check_port_available(port):
            return port
        port += 1
    return start_port  # Fallback to original port

def setup_environment():
    """Setup environment and check dependencies"""
    print("🔍 Checking environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists('requirements.txt'):
        print("❌ Please run this script from the backend directory")
        print("💡 Try: cd backend && python run.py")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    
    print("✅ Environment check passed")

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        import flask
        import pandas
        import requests
        print("✅ All dependencies are already installed")
    except ImportError as e:
        print(f"⚠️ Missing dependency: {e}")
        print("Installing from requirements.txt...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")

def main():
    """Main function to start the application"""
    print("🚀 Starting NSE Option Chain Analyzer...")
    
    # Setup
    setup_environment()
    install_dependencies()
    
    # Find available port
    port = find_available_port(5000)
    if port != 5000:
        print(f"⚠️ Port 5000 is busy, using port {port}")
    
    # Import after dependency check
    try:
        from app import app, fetch_and_process_data
        from config import Config
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all files are in the backend directory")
        sys.exit(1)
    
    # Initial data fetch
    print("📊 Fetching initial market data...")
    try:
        fetch_and_process_data()
        print("✅ Initial data fetched successfully")
    except Exception as e:
        print(f"⚠️ Initial data fetch failed: {e}")
        print("💡 This might be a network issue. Continuing...")
    
    # Start Flask application
    print(f"🌐 Starting web server on http://localhost:{port}")
    print("📈 Dashboard available at: http://localhost:{port}")
    print("📱 Mobile access: http://YOUR-IP:{port} (see instructions below)")
    print("🔄 Auto-refresh interval: 30 seconds")
    print("⏹️  Press Ctrl+C to stop the application")
    print("\n" + "="*50)
    
    try:
        app.run(
            debug=False,
            host='0.0.0.0',  # Allow external connections
            port=port,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Option Chain Analyzer...")
    except Exception as e:
        print(f"❌ Application error: {e}")

if __name__ == '__main__':
    main()
