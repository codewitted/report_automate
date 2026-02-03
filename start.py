#!/usr/bin/env python3
"""
Quick Start Script for Jira Report Automation

This script provides a simple way to start the web interface.
Just run this file and open your browser!
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    try:
        import flask
        import requests
        import reportlab
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e.name}")
        print("\nPlease install dependencies by running:")
        print("  pip install -r requirements.txt")
        return False

def open_browser():
    """Open the browser after a short delay."""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main entry point."""
    print("=" * 60)
    print("Jira Report Automation - Quick Start")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    print("Starting web server...")
    print("The browser will open automatically in a few seconds.")
    print()
    print("If the browser doesn't open, go to: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Open browser in a separate thread
    Timer(2.0, open_browser).start()
    
    # Start the Flask app
    try:
        from app import app
        app.run(debug=False, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped. Goodbye!")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
