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
    """Get current parking bay status for map display with balanced street distribution"""
    try:
        # Get optional query parameters
        limit = request.args.get('limit', type=int)
        bounds = request.args.get('bounds')  # Format: "lat1,lng1,lat2,lng2"

        # Use a different approach for balanced distribution across streets
        if limit is None:
            limit = 1500

        # First, get all unique streets
        streets_query = db.session.query(
            ParkingBay.road_segment_description
        ).join(
            ParkingStatusCurrent, ParkingBay.kerbside_id == ParkingStatusCurrent.kerbside_id
        ).filter(
            ParkingBay.road_segment_description.isnot(None)
        )

        # Apply geographic bounds filter to streets if provided
        if bounds:
            try:
                lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
                streets_query = streets_query.filter(
                    ParkingBay.latitude.between(min(lat1, lat2), max(lat1, lat2)),
                    ParkingBay.longitude.between(min(lng1, lng2), max(lng1, lng2))
                )
            except (ValueError, TypeError):
                pass

        unique_streets = streets_query.distinct().all()
        street_names = [street[0] for street in unique_streets]

        # Calculate how many parking bays per street for balanced distribution
        if len(street_names) > 0:
            bays_per_street = max(2, limit // len(street_names))  # At least 2 bays per street
            remaining_limit = limit
        else:
            bays_per_street = limit
            remaining_limit = limit

        results = []

        # Get balanced data from each street
        for street_name in street_names:
            if remaining_limit <= 0:
                break

            # Get limited number of bays from this street
            current_street_limit = min(bays_per_street, remaining_limit)

            street_query = db.session.query(
                ParkingBay,
                ParkingStatusCurrent
            ).join(
                ParkingStatusCurrent, ParkingBay.kerbside_id == ParkingStatusCurrent.kerbside_id
            ).filter(
                ParkingBay.road_segment_description == street_name
            )

            # Apply geographic bounds filter if provided
            if bounds:
                try:
                    lat1, lng1, lat2, lng2 = map(float, bounds.split(','))
                    street_query = street_query.filter(
                        ParkingBay.latitude.between(min(lat1, lat2), max(lat1, lat2)),
                        ParkingBay.longitude.between(min(lng1, lng2), max(lng1, lng2))
                    )
                except (ValueError, TypeError):
                    pass

            street_bays = street_query.limit(current_street_limit).all()

            # Add street bays to results
            for bay, status in street_bays:
                results.append({
                    'kerbside_id': bay.kerbside_id,
                    'latitude': float(bay.latitude),
                    'longitude': float(bay.longitude),
                    'status': status.status_description,
                    'road_segment': bay.road_segment_description,
                    'zone_number': status.zone_number
                })
                remaining_limit -= 1

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results,
            'distribution_info': {
                'total_streets': len(street_names),
                'target_bays_per_street': bays_per_street,
                'actual_bays_returned': len(results)
            }
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
