#!/usr/bin/env python3
"""
Main entry point for the Melbourne Parking System backend
This file is used by Railway for deployment
"""

import os
import sys
from website import create_website

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Create Flask application
app = create_website()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    host = '0.0.0.0'
    debug = os.environ.get('FLASK_ENV') != 'production'

    print(f"Starting Melbourne Parking System backend on {host}:{port}")
    print(f"Debug mode: {debug}")

    app.run(host=host, port=port, debug=debug)
