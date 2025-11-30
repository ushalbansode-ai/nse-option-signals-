#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    # Install dependencies
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the application
    os.chdir('backend')
    subprocess.check_call([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
