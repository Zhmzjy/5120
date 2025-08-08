"""
Analytics API routes for Melbourne Parking Website
Handles population data analysis and historical trends
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import csv
import os
import random

analytics_routes = Blueprint('analytics', __name__)

@analytics_routes.route('/population', methods=['GET'])
def get_population_data():
    """Get Victoria population growth data from CSV file"""
    try:
        csv_file_path = os.path.join(os.path.dirname(__file__), '../../..', 'Australian Bureau of Statistics (1).csv')

        population_data = []

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            lines = list(csv_reader)

            # Process each state's data (skip header rows)
            for i in range(2, len(lines)):
                row = lines[i]
                if len(row) >= 10:
                    state = row[0].strip('"')

                    # Extract growth numbers (columns 1, 3, 5, 7, 9)
                    growth_numbers = []
                    growth_rates = []

                    for j in range(1, 10, 2):  # Odd columns contain numbers
                        if j < len(row):
                            num_str = row[j].replace(',', '').replace('"', '')
                            try:
                                growth_numbers.append(int(num_str))
                            except ValueError:
                                pass

                    for j in range(2, 11, 2):  # Even columns contain rates
                        if j < len(row):
                            rate_str = row[j].replace('"', '')
                            growth_rates.append(rate_str)

                    if growth_numbers and growth_rates:
                        population_data.append({
                            'state': state,
                            'growthNumbers': growth_numbers,
                            'growthRates': growth_rates,
                            'periods': ['2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021']
                        })

        return jsonify(population_data)

    except FileNotFoundError:
        # Return mock data if CSV file not found
        mock_data = [{
            'state': 'Vic.',
            'growthNumbers': [209495, 214408, 236429, 215728, 188855],
            'growthRates': ['4.2', '4.2', '4.5', '4.0', '3.5'],
            'periods': ['2016-2017', '2017-2018', '2018-2019', '2019-2020', '2020-2021']
        }]
        return jsonify(mock_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_routes.route('/historical', methods=['GET'])
def get_historical_data():
    """Get historical parking usage trends"""
    try:
        period = request.args.get('period', '1m')  # '7d', '1m', '3m'

        # Generate mock historical data based on period
        historical_data = generate_mock_historical_data(period)

        return jsonify(historical_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_routes.route('/correlation', methods=['GET'])
def get_population_parking_correlation():
    """Get correlation analysis between population growth and parking demand"""
    try:
        # Mock correlation data
        correlation_data = {
            'correlation_coefficient': 0.73,
            'analysis': {
                'strength': 'Strong positive correlation',
                'interpretation': 'Population growth strongly correlates with parking demand',
                'recommendations': [
                    'Increase parking capacity in high-growth areas',
                    'Implement smart parking solutions',
                    'Consider public transport alternatives'
                ]
            },
            'data_points': [
                {'year': '2017', 'population_growth': 4.2, 'parking_demand_increase': 3.8},
                {'year': '2018', 'population_growth': 4.2, 'parking_demand_increase': 4.1},
                {'year': '2019', 'population_growth': 4.5, 'parking_demand_increase': 4.7},
                {'year': '2020', 'population_growth': 4.0, 'parking_demand_increase': 3.2},
                {'year': '2021', 'population_growth': 3.5, 'parking_demand_increase': 2.9}
            ]
        }

        return jsonify(correlation_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_mock_historical_data(period):
    """Generate realistic mock historical parking data"""

    # Determine number of data points based on period
    if period == '7d':
        days = 7
        date_format = lambda d: d.strftime('%a %d/%m')
    elif period == '1m':
        days = 30
        date_format = lambda d: d.strftime('%d/%m')
    else:  # 3m
        days = 90
        date_format = lambda d: d.strftime('%d/%m')

    data = []
    current_date = datetime.now()

    for i in range(days):
        date = current_date - timedelta(days=days-1-i)

        # Generate realistic occupancy patterns
        hour = date.hour if period == '7d' else 12  # Use noon for longer periods
        day_of_week = date.weekday()

        # Base occupancy rate
        base_occupancy = 45

        # Time-based patterns
        if period == '7d':
            if 8 <= hour <= 10:  # Morning peak
                base_occupancy = 78
            elif 12 <= hour <= 14:  # Lunch peak
                base_occupancy = 68
            elif 17 <= hour <= 19:  # Evening peak
                base_occupancy = 82
            elif hour <= 6 or hour >= 22:  # Night/early morning
                base_occupancy = 25

        # Weekend adjustment
        if day_of_week >= 5:  # Weekend
            base_occupancy *= 0.65

        # Add seasonal variation and randomness
        seasonal_factor = 1 + 0.1 * (random.random() - 0.5)
        random_variation = random.uniform(-8, 8)

        occupancy_rate = max(15, min(95, base_occupancy * seasonal_factor + random_variation))

        # Calculate available spots
        total_spots = 3200
        occupied_spots = int(total_spots * occupancy_rate / 100)
        available_spots = total_spots - occupied_spots

        data.append({
            'period': date_format(date),
            'occupancyRate': round(occupancy_rate, 1),
            'availableSpots': available_spots,
            'occupiedSpots': occupied_spots,
            'totalSpots': total_spots,
            'timestamp': date.isoformat()
        })

    return data

def calculate_trend_direction(data):
    """Calculate trend direction from historical data"""
    if len(data) < 2:
        return 'stable'

    first_rate = data[0]['occupancyRate']
    last_rate = data[-1]['occupancyRate']
    change_percent = ((last_rate - first_rate) / first_rate) * 100

    if change_percent > 5:
        return 'increasing'
    elif change_percent < -5:
        return 'decreasing'
    else:
        return 'stable'
