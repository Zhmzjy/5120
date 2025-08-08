from flask import Blueprint, jsonify
from models.parking import ParkingBay, ParkingStatusCurrent, db
from sqlalchemy import func

statistics_routes = Blueprint('statistics_routes', __name__)

@statistics_routes.route('/overview', methods=['GET'])
def get_parking_overview():
    """Get overall parking statistics for dashboard"""
    try:
        # Get total counts
        total_bays = db.session.query(func.count(ParkingBay.kerbside_id)).scalar()

        # Get status breakdown
        status_counts = db.session.query(
            ParkingStatusCurrent.status_description,
            func.count(ParkingStatusCurrent.kerbside_id)
        ).group_by(ParkingStatusCurrent.status_description).all()

        occupied_count = 0
        available_count = 0

        for status, count in status_counts:
            if status == 'Present':
                occupied_count = count
            elif status == 'Unoccupied':
                available_count = count

        occupancy_rate = round((occupied_count / total_bays * 100), 1) if total_bays > 0 else 0

        # Return just the data object for frontend compatibility
        return jsonify({
            'total_bays': total_bays,
            'occupied_bays': occupied_count,
            'available_bays': available_count,
            'occupancy_rate': occupancy_rate
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@statistics_routes.route('/zones', methods=['GET'])
def get_zone_statistics():
    """Get parking statistics by zone"""
    try:
        # Get zones with total bay counts first
        zones_total = db.session.query(
            ParkingStatusCurrent.zone_number,
            func.count(ParkingStatusCurrent.kerbside_id).label('total_bays')
        ).filter(
            ParkingStatusCurrent.zone_number.isnot(None)
        ).group_by(
            ParkingStatusCurrent.zone_number
        ).order_by(
            ParkingStatusCurrent.zone_number
        ).all()

        zones_data = []
        for zone_number, total_bays in zones_total:
            # Get occupied count for this zone
            occupied_count = db.session.query(
                func.count(ParkingStatusCurrent.kerbside_id)
            ).filter(
                ParkingStatusCurrent.zone_number == zone_number,
                ParkingStatusCurrent.status_description == 'Present'
            ).scalar() or 0

            # Get available count for this zone
            available_count = db.session.query(
                func.count(ParkingStatusCurrent.kerbside_id)
            ).filter(
                ParkingStatusCurrent.zone_number == zone_number,
                ParkingStatusCurrent.status_description == 'Unoccupied'
            ).scalar() or 0

            occupancy_rate = round((occupied_count / total_bays * 100), 1) if total_bays > 0 else 0

            zones_data.append({
                'zone_number': zone_number,
                'total_bays': total_bays,
                'occupied_bays': occupied_count,
                'available_bays': available_count,
                'occupancy_rate': occupancy_rate
            })

        # Return just the array for frontend compatibility
        return jsonify(zones_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
