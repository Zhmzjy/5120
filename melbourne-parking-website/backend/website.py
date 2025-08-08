from flask import Flask
from flask_cors import CORS
from models.parking import db

def create_website():
    website = Flask(__name__)

    # Database configuration
    website.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://melbourne_parking:zjy0312!@localhost:5432/melbourne_parking_system'
    website.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(website)
    CORS(website)

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
    print("Melbourne Parking Website backend starting on http://localhost:5002")
    app.run(debug=True, port=5002)
