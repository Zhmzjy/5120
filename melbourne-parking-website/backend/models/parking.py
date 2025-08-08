from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ParkingBay(db.Model):
    __tablename__ = 'parking_bays'

    kerbside_id = db.Column(db.Integer, primary_key=True)
    road_segment_id = db.Column(db.Integer)
    road_segment_description = db.Column(db.Text)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    last_updated = db.Column(db.Date)
    location_string = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    current_status = db.relationship('ParkingStatusCurrent', backref='parking_bay', uselist=False)

    def to_json(self):
        return {
            'kerbside_id': self.kerbside_id,
            'road_segment_description': self.road_segment_description,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'status': self.current_status.status_description if self.current_status else 'Unknown'
        }

class ParkingStatusCurrent(db.Model):
    __tablename__ = 'parking_status_current'

    kerbside_id = db.Column(db.Integer, db.ForeignKey('parking_bays.kerbside_id'), primary_key=True)
    zone_number = db.Column(db.Integer)
    status_description = db.Column(db.String(20), nullable=False)
    last_updated = db.Column(db.DateTime)
    status_timestamp = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            'kerbside_id': self.kerbside_id,
            'zone_number': self.zone_number,
            'status_description': self.status_description,
            'status_timestamp': self.status_timestamp.isoformat() if self.status_timestamp else None
        }
