from flask import Flask
from flask_cors import CORS
from models.parking import db
import os

def create_website():
    website = Flask(__name__)

    # Database configuration - use environment variables for production
    if os.getenv('DATABASE_URL'):
        # Production deployment (Render) - use DATABASE_URL from environment
        website.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    else:
        # Local development database
        website.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://melbourne_parking:zjy0312!@localhost:5432/melbourne_parking_system'

    website.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(website)

    # Configure CORS for production deployment
    if os.getenv('FLASK_ENV') == 'production':
        CORS(website, origins=[
            'https://*.onrender.com',
            'https://melbourne-parking-frontend.onrender.com'
        ])
    else:
        CORS(website)  # Allow all origins in development

    # Create tables if they don't exist
    with website.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")

    # Register blueprints
    from api.parking_routes import parking_routes
    from api.statistics_routes import statistics_routes
    from api.analytics_routes import analytics_routes

    website.register_blueprint(parking_routes, url_prefix='/api/parking')
    website.register_blueprint(statistics_routes, url_prefix='/api/statistics')
    website.register_blueprint(analytics_routes, url_prefix='/api/analytics')

    return website

if __name__ == '__main__':
    app = create_website()
    port = int(os.environ.get('PORT', 5002))
    print(f"Melbourne Parking Website backend starting on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
