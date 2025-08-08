#!/usr/bin/env python3
"""
Entry point for Melbourne Parking Website backend server
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website import create_website

if __name__ == '__main__':
    app = create_website()
    port = int(os.environ.get('PORT', 5002))
    print(f"Melbourne Parking Website backend starting on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
