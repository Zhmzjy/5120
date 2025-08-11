#!/usr/bin/env python3
"""
Melbourne Parking Website - Main Application Entry Point
This file starts the Flask application server
"""

import os
from website import create_website

# Create Flask application instance
app = create_website()

if __name__ == '__main__':
    # Get port from environment variable (Render sets PORT automatically)
    port = int(os.environ.get('PORT', 5000))

    # Run the application
    print(f"Starting Melbourne Parking System backend on 0.0.0.0:{port}")
    print(f"Debug mode: {os.environ.get('FLASK_ENV') != 'production'}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') != 'production'
    )
