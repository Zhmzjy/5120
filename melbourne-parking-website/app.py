#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""

import os
import sys

# Add project directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, current_dir)
sys.path.insert(0, backend_dir)

from backend.website import create_website

# Create the Flask application
app = create_website()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
