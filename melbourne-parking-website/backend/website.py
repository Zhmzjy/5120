from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from models.parking import db
import os

def create_website():
    website = Flask(__name__, static_folder='../frontend/dist', static_url_path='')

    # Database configuration - use environment variable for Railway
    database_url = os.getenv('DATABASE_URL', 'postgresql://melbourne_parking:zjy0312!@localhost:5432/melbourne_parking_system')

    # Fix for Railway PostgreSQL URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    website.config['SQLALCHEMY_DATABASE_URI'] = database_url
    website.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(website)

    # CORS configuration for production
    cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS(website, origins=cors_origins)

    # Register blueprints
    from api.parking_routes import parking_routes
    from api.statistics_routes import statistics_routes
    from api.analytics_routes import analytics_routes

    website.register_blueprint(parking_routes, url_prefix='/api/parking')
    website.register_blueprint(statistics_routes, url_prefix='/api/statistics')
    website.register_blueprint(analytics_routes, url_prefix='/api/analytics')

    # Serve frontend static files
    @website.route('/')
    def serve_index():
        return send_file('../frontend/dist/index.html')

    @website.route('/<path:path>')
    def serve_static(path):
        # Serve API routes normally
        if path.startswith('api/'):
            return website.send_static_file(path)

        # Check if file exists in dist folder
        try:
            return send_from_directory('../frontend/dist', path)
        except:
            # If file doesn't exist, serve index.html for SPA routing
            return send_file('../frontend/dist/index.html')

    return website

if __name__ == '__main__':
    app = create_website()
    print("Melbourne Parking Website backend starting on http://localhost:5002")
    app.run(debug=True, port=5002)
