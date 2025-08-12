from flask import Blueprint, jsonify, request
from models.parking import ParkingBay, ParkingStatusCurrent, db
from sqlalchemy import func
import math

parking_routes = Blueprint('parking_routes', __name__)

@parking_routes.route('/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify API is working"""
    try:
        # Test database connection and count records
        bay_count = db.session.query(ParkingBay).count()
        status_count = db.session.query(ParkingStatusCurrent).count()

        return jsonify({
            'status': 'API is working',
            'database_connected': True,
            'parking_bays_count': bay_count,
            'parking_status_count': status_count,
            'message': 'Backend is running successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'API working but database error',
            'database_connected': False,
            'error': str(e)
        }), 500

@parking_routes.route('/current', methods=['GET'])
def get_current_parking_status():
    """Get current parking bay status for map display - unified with statistics logic"""
    try:
        # Get optional query parameters
        limit = request.args.get('limit', type=int)
        bounds = request.args.get('bounds')  # Format: "lat1,lng1,lat2,lng2"

        # Base query - use same logic as street statistics (INNER JOIN)
        query = db.session.query(
            ParkingBay,
            ParkingStatusCurrent
        ).join(
            ParkingStatusCurrent, ParkingBay.kerbside_id == ParkingStatusCurrent.kerbside_id
        )

        # Apply geographic bounds filter if provided
        if bounds:
            try:
                lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
                query = query.filter(
                    ParkingBay.latitude.between(min(lat1, lat2), max(lat1, lat2)),
                    ParkingBay.longitude.between(min(lng1, lng2), max(lng1, lng2))
                )
            except (ValueError, TypeError):
                pass  # Ignore invalid bounds format

        # Remove default limit to match statistics logic - only apply if explicitly requested
        if limit and limit > 0:
            parking_bays = query.limit(limit).all()
        else:
            # No limit - show all parking bays with status data to match statistics
            parking_bays = query.all()

        results = []
        for bay, status in parking_bays:
            results.append({
                'kerbside_id': bay.kerbside_id,
                'latitude': float(bay.latitude),
                'longitude': float(bay.longitude),
                'status': status.status_description,
                'road_segment': bay.road_segment_description,
                'zone_number': status.zone_number
            })

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@parking_routes.route('/streets', methods=['GET'])
def get_streets_list():
    """Get list of streets with parking statistics"""
    try:
        # Get streets with total bay counts and available bay counts separately
        streets_data = db.session.query(
            ParkingBay.road_segment_description,
            func.count(ParkingBay.kerbside_id).label('total_bays')
        ).join(
            ParkingStatusCurrent, ParkingBay.kerbside_id == ParkingStatusCurrent.kerbside_id
        ).filter(
            ParkingBay.road_segment_description.isnot(None)
        ).group_by(
            ParkingBay.road_segment_description
        ).order_by(
            func.count(ParkingBay.kerbside_id).desc()
        ).limit(50).all()

        results = []
        for street_name, total_bays in streets_data:
            # Get available bays count for this specific street
            available_count = db.session.query(
                func.count(ParkingBay.kerbside_id)
            ).join(
                ParkingStatusCurrent, ParkingBay.kerbside_id == ParkingStatusCurrent.kerbside_id
            ).filter(
                ParkingBay.road_segment_description == street_name,
                ParkingStatusCurrent.status_description == 'Unoccupied'
            ).scalar() or 0

            # Calculate occupancy rate
            occupied_bays = total_bays - available_count
            occupancy_rate = round((occupied_bays / total_bays * 100), 1) if total_bays > 0 else 0

            results.append({
                'street_name': street_name,
                'total_bays': total_bays,
                'available_bays': available_count,
                'occupied_bays': occupied_bays,
                'occupancy_rate': occupancy_rate
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@parking_routes.route('/nearby', methods=['GET'])
def find_nearby_parking():
    """Find nearby available parking spaces"""
    try:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))
        radius = float(request.args.get('radius', 500))  # Default 500 meters

        # Calculate bounding box for efficiency
        lat_range = radius / 111000  # Roughly 111km per degree latitude
        lng_range = radius / (111000 * math.cos(math.radians(lat)))

        nearby_bays = db.session.query(
            ParkingBay,
            ParkingStatusCurrent
        ).join(
            ParkingStatusCurrent, ParkingBay.kerbside_id == ParkingStatusCurrent.kerbside_id
        ).filter(
            ParkingStatusCurrent.status_description == 'Unoccupied',
            ParkingBay.latitude.between(lat - lat_range, lat + lat_range),
            ParkingBay.longitude.between(lng - lng_range, lng + lng_range)
        ).all()

        # Calculate actual distance and sort
        available_spaces = []
        for bay, status in nearby_bays:
            distance = calculate_distance(lat, lng, float(bay.latitude), float(bay.longitude))
            if distance <= radius:
                available_spaces.append({
                    'kerbside_id': bay.kerbside_id,
                    'latitude': float(bay.latitude),
                    'longitude': float(bay.longitude),
                    'distance': round(distance, 1),
                    'road_segment': bay.road_segment_description,
                    'zone_number': status.zone_number
                })

        # Sort by distance
        available_spaces.sort(key=lambda x: x['distance'])

        return jsonify({
            'success': True,
            'data': available_spaces[:20],  # Return top 20 nearest
            'search_center': {'lat': lat, 'lng': lng},
            'search_radius': radius
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth's radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lng / 2) * math.sin(delta_lng / 2))

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
