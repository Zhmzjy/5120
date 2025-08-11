#!/usr/bin/env python3
"""
Railway deployment entry point for Melbourne Parking System
This script serves as the main entry point and redirects to the actual Flask app
"""

import os
import sys
import subprocess

def main():
    """Main entry point for Railway deployment"""
    # Change to the backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'melbourne-parking-website', 'backend')

    if not os.path.exists(backend_dir):
        print(f"ERROR: Backend directory not found at {backend_dir}")
        sys.exit(1)

    # Change working directory to backend
    os.chdir(backend_dir)

    # Add backend to Python path
    sys.path.insert(0, backend_dir)

    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('PORT', '8000')

    try:
        # Import and run the Flask application
        from website import create_website

        app = create_website()
        port = int(os.environ.get('PORT', 8000))

        print(f"Starting Melbourne Parking System on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)

    except ImportError as e:
        print(f"ERROR: Failed to import Flask application: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
