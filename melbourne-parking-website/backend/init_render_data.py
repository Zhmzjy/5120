#!/usr/bin/env python3
"""
Render Data Initialization Script
Purpose: Initialize SQLite database with parking data for Render deployment
Author: Melbourne Parking System
Date: August 12, 2025
"""

import os
import sqlite3
import csv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _safe_int(value, default=None):
    """Safely convert value to integer with default fallback"""
    if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
        return default
    try:
        return int(float(str(value)))  # Handle decimal strings
    except (ValueError, TypeError):
        return default

def _safe_float(value, default=None):
    """Safely convert value to float with default fallback"""
    if value is None or str(value).strip() == '' or str(value).lower() == 'nan':
        return default
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return default

def _safe_string(value, default=''):
    """Safely convert value to string with default fallback"""
    if value is None:
        return default
    return str(value).strip()

def _generate_default_id(row_index):
    """Generate a default ID for records without KerbsideID"""
    return 9000000 + row_index  # Start from 9000000 to avoid conflicts

def _get_default_coordinates():
    """Get default coordinates for Melbourne CBD center"""
    return -37.8136, 144.9631  # Melbourne CBD center

def init_render_database():
    """Initialize SQLite database with essential data for Render deployment"""

    # Use absolute path with environment variable fallback
    db_path = os.getenv('DATABASE_PATH', '/opt/render/project/src/parking.db')

    # Log the database path being used
    logger.info(f"🗄️ Using database path: {db_path}")

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create database connection
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("🗄️  Initializing database...")

        # Create all required tables
        create_database_tables(cursor)

        # Import data from CSV files
        import_all_data(cursor)

        # Commit changes
        conn.commit()

        # Verify and report results
        verify_data_import(cursor)

        logger.info("🎉 Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def create_database_tables(cursor):
    """Create all database tables with proper schema"""

    logger.info("📋 Creating database tables...")

    # Create parking_bays table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_bays (
            kerbside_id INTEGER PRIMARY KEY,
            road_segment_id INTEGER,
            road_segment_description TEXT,
            latitude DECIMAL(10,7) NOT NULL,
            longitude DECIMAL(10,7) NOT NULL,
            last_updated DATE,
            location_string TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create parking_status_current table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_status_current (
            kerbside_id INTEGER PRIMARY KEY,
            zone_number INTEGER,
            status_description VARCHAR(20) NOT NULL,
            last_updated TIMESTAMP,
            status_timestamp TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kerbside_id) REFERENCES parking_bays (kerbside_id)
        )
    ''')

    # Create parking_status_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kerbside_id INTEGER NOT NULL,
            zone_number INTEGER,
            status_description VARCHAR(20) NOT NULL,
            status_timestamp TIMESTAMP,
            last_updated TIMESTAMP,
            data_collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kerbside_id) REFERENCES parking_bays (kerbside_id)
        )
    ''')

    # Create victoria_population_growth table for population statistics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS victoria_population_growth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_period VARCHAR(50) NOT NULL,
            population_increase INTEGER,
            growth_rate DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create melbourne_population_history table for detailed population data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS melbourne_population_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sa2_code VARCHAR(20),
            sa2_name VARCHAR(200),
            sa3_name VARCHAR(200),
            sa4_name VARCHAR(200),
            year_2001 INTEGER, year_2002 INTEGER, year_2003 INTEGER, year_2004 INTEGER, year_2005 INTEGER,
            year_2006 INTEGER, year_2007 INTEGER, year_2008 INTEGER, year_2009 INTEGER, year_2010 INTEGER,
            year_2011 INTEGER, year_2012 INTEGER, year_2013 INTEGER, year_2014 INTEGER, year_2015 INTEGER,
            year_2016 INTEGER, year_2017 INTEGER, year_2018 INTEGER, year_2019 INTEGER, year_2020 INTEGER,
            year_2021 INTEGER,
            population_change_2011_2021 INTEGER,
            growth_rate_2011_2021 DECIMAL(5,2),
            area_km2 DECIMAL(10,2),
            population_density_2021 DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    logger.info("✅ Database tables created")

def import_all_data(cursor):
    """Import data from CSV files or create sample data"""

    # Try to import from CSV files in project root
    csv_base_path = '../../'

    # Import Victoria population growth data
    victoria_csv = os.path.join(csv_base_path, 'Australian Bureau of Statistics (1).csv')
    if os.path.exists(victoria_csv):
        import_victoria_population_data(cursor, victoria_csv)
    else:
        logger.warning("Victoria population CSV not found, creating sample data")
        create_sample_victoria_data(cursor)

    # Import Melbourne population history data
    melbourne_csv = os.path.join(csv_base_path, 'only_melbourne_city_1_without_none.csv')
    if os.path.exists(melbourne_csv):
        import_melbourne_population_data(cursor, melbourne_csv)
    else:
        logger.warning("Melbourne population CSV not found, creating sample data")
        create_sample_melbourne_data(cursor)

    # Import parking bays
    parking_bays_file = os.path.join(csv_base_path, 'on-street-parking-bays.csv')
    if os.path.exists(parking_bays_file):
        import_parking_bays_from_csv(cursor, parking_bays_file)
    else:
        logger.warning("CSV file not found, creating sample parking bays data")
        create_sample_parking_bays(cursor)

    # Import sensor status
    sensor_file = os.path.join(csv_base_path, 'on-street-parking-bay-sensors.csv')
    if os.path.exists(sensor_file):
        import_sensor_status_from_csv(cursor, sensor_file)
    else:
        logger.warning("Sensor CSV file not found, creating sample status data")
        create_sample_status_data(cursor)

def import_victoria_population_data(cursor, csv_file):
    """Import Victoria population growth data from Australian Bureau of Statistics CSV"""

    logger.info(f"🏛️ Importing Victoria population data from {csv_file}")

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            # Skip the first row (headers) and read CSV
            lines = file.readlines()
            reader = csv.reader(lines[1:])  # Skip first row

            for row in reader:
                if len(row) > 0 and 'Vic.' in str(row[0]):
                    # Found Victoria row, parse data
                    periods = [
                        ("Between 2016 and 2017", 1, 2),
                        ("Between 2017 and 2018", 3, 4),
                        ("Between 2018 and 2019", 5, 6),
                        ("Between 2019 and 2020", 7, 8),
                        ("Between 2020 and 2021", 9, 10)
                    ]

                    for period, num_idx, rate_idx in periods:
                        try:
                            pop_increase = None
                            growth_rate = None

                            if num_idx < len(row) and row[num_idx]:
                                pop_increase = _safe_int(row[num_idx])

                            if rate_idx < len(row) and row[rate_idx]:
                                growth_rate = _safe_float(row[rate_idx])

                            cursor.execute('''
                                INSERT OR REPLACE INTO victoria_population_growth 
                                (year_period, population_increase, growth_rate)
                                VALUES (?, ?, ?)
                            ''', (period, pop_increase, growth_rate))

                        except Exception as e:
                            logger.warning(f"Error parsing Victoria data for {period}: {e}")
                            continue

                    logger.info("✅ Imported Victoria population growth data")
                    return

        logger.warning("Victoria data not found in CSV, creating sample data")
        create_sample_victoria_data(cursor)

    except Exception as e:
        logger.error(f"Failed to import Victoria population data: {e}")
        create_sample_victoria_data(cursor)

def import_melbourne_population_data(cursor, csv_file):
    """Import Melbourne population history data"""

    logger.info(f"🏙️ Importing Melbourne population data from {csv_file}")

    imported_count = 0
    # Removed max_records limit - import all data

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Removed max_records check - import all records

                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO melbourne_population_history (
                            sa2_code, sa2_name, sa3_name, sa4_name,
                            year_2001, year_2002, year_2003, year_2004, year_2005,
                            year_2006, year_2007, year_2008, year_2009, year_2010,
                            year_2011, year_2012, year_2013, year_2014, year_2015,
                            year_2016, year_2017, year_2018, year_2019, year_2020,
                            year_2021, population_change_2011_2021, growth_rate_2011_2021,
                            area_km2, population_density_2021
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row.get('SA2 code'),
                        row.get('SA2 name'),
                        row.get('SA3 name'),
                        row.get('SA4 name'),
                        _safe_int(row.get('2001 no.')),
                        _safe_int(row.get('2002 no.')),
                        _safe_int(row.get('2003 no.')),
                        _safe_int(row.get('2004 no.')),
                        _safe_int(row.get('2005 no.')),
                        _safe_int(row.get('2006 no.')),
                        _safe_int(row.get('2007 no.')),
                        _safe_int(row.get('2008 no.')),
                        _safe_int(row.get('2009 no.')),
                        _safe_int(row.get('2010 no.')),
                        _safe_int(row.get('2011 no.')),
                        _safe_int(row.get('2012 no.')),
                        _safe_int(row.get('2013 no.')),
                        _safe_int(row.get('2014 no.')),
                        _safe_int(row.get('2015 no.')),
                        _safe_int(row.get('2016 no.')),
                        _safe_int(row.get('2017 no.')),
                        _safe_int(row.get('2018 no.')),
                        _safe_int(row.get('2019 no.')),
                        _safe_int(row.get('2020 no.')),
                        _safe_int(row.get('2021 no.')),
                        _safe_int(row.get('2011-2021 no.')),
                        _safe_float(row.get('2011-2021 %')),
                        _safe_float(row.get('Area km2')),
                        _safe_float(row.get('Population density 2021 persons/km2'))
                    ))

                    imported_count += 1

                    # Log progress every 50 records instead of limiting
                    if imported_count % 50 == 0:
                        logger.info(f"   Imported {imported_count} Melbourne population records...")

                except Exception as e:
                    logger.warning(f"Error importing Melbourne population data for {row.get('SA2 name', 'Unknown')}: {e}")
                    continue

        logger.info(f"✅ Imported {imported_count} Melbourne population records")

    except Exception as e:
        logger.error(f"Failed to import Melbourne population data: {e}")
        create_sample_melbourne_data(cursor)

def import_parking_bays_from_csv(cursor, csv_file):
    """Import parking bays data from CSV file - Only import records with valid KerbsideID"""

    logger.info(f"🅿️ Importing parking bays from {csv_file}")

    imported_count = 0
    skipped_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row_index, row in enumerate(reader):
                try:
                    # Only import records with valid KerbsideID - RESTORE ORIGINAL LIMIT
                    kerbside_id = _safe_int(row.get('KerbsideID'))
                    if kerbside_id is None:
                        skipped_count += 1
                        continue  # Skip records without valid KerbsideID

                    # Get coordinates with fallback to Melbourne CBD center
                    latitude = _safe_float(row.get('Latitude'))
                    longitude = _safe_float(row.get('Longitude'))

                    if latitude is None or longitude is None:
                        default_lat, default_lng = _get_default_coordinates()
                        latitude = latitude or default_lat
                        longitude = longitude or default_lng
                        logger.info(f"Using default coordinates for KerbsideID {kerbside_id}")

                    # Parse optional fields with safe conversion
                    road_segment_id = _safe_int(row.get('RoadSegmentID'))
                    road_segment_description = _safe_string(row.get('RoadSegmentDescription'), 'Unknown Street')
                    location_string = _safe_string(row.get('Location'), 'Melbourne CBD')

                    # Insert parking bay record - only with valid KerbsideID
                    cursor.execute('''
                        INSERT OR REPLACE INTO parking_bays 
                        (kerbside_id, road_segment_id, road_segment_description, 
                         latitude, longitude, location_string)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        kerbside_id,
                        road_segment_id,
                        road_segment_description,
                        latitude,
                        longitude,
                        location_string
                    ))

                    imported_count += 1

                    # Progress logging every 1000 records
                    if imported_count % 1000 == 0:
                        logger.info(f"   Imported {imported_count} parking bays...")

                except Exception as e:
                    # Log errors but continue processing
                    logger.warning(f"Error importing parking bay row {row_index + 1}: {e}")
                    skipped_count += 1

        logger.info(f"✅ Imported {imported_count} parking bays with valid KerbsideID, skipped {skipped_count} records without valid ID")

    except Exception as e:
        logger.error(f"Failed to import parking bays: {e}")
        create_sample_parking_bays(cursor)

def import_sensor_status_from_csv(cursor, csv_file):
    """Import sensor status data from CSV file - Import ALL rows without strict validation"""

    logger.info(f"📡 Importing sensor status from {csv_file}")

    # Get valid parking bay IDs
    cursor.execute("SELECT kerbside_id FROM parking_bays")
    valid_ids = {row[0] for row in cursor.fetchall()}

    imported_count = 0
    skipped_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row_index, row in enumerate(reader):
                try:
                    # Get KerbsideID with safe conversion
                    kerbside_id = _safe_int(row.get('KerbsideID'))

                    # Skip only if KerbsideID is completely invalid
                    if kerbside_id is None:
                        logger.warning(f"Row {row_index + 1}: Invalid KerbsideID '{row.get('KerbsideID')}', skipping")
                        skipped_count += 1
                        continue

                    # Get status description with default fallback
                    status_description = _safe_string(row.get('Status_Description'), 'Unknown')

                    # If status is empty, use default
                    if not status_description or status_description == '':
                        status_description = 'Unknown'
                        logger.info(f"Using default status 'Unknown' for KerbsideID {kerbside_id}")

                    # Import even if parking bay doesn't exist - create a record anyway
                    if kerbside_id not in valid_ids:
                        logger.info(f"KerbsideID {kerbside_id} not in parking_bays, but importing sensor data anyway")

                    # Parse optional fields with safe conversion
                    zone_number = _safe_int(row.get('Zone_Number'))

                    # Insert current status - NO STRICT VALIDATION
                    cursor.execute('''
                        INSERT OR REPLACE INTO parking_status_current 
                        (kerbside_id, zone_number, status_description)
                        VALUES (?, ?, ?)
                    ''', (kerbside_id, zone_number, status_description))

                    # Also insert into history table
                    cursor.execute('''
                        INSERT INTO parking_status_history 
                        (kerbside_id, zone_number, status_description, data_collected_at)
                        VALUES (?, ?, ?, ?)
                    ''', (kerbside_id, zone_number, status_description, datetime.now()))

                    imported_count += 1

                    # Progress logging every 1000 records
                    if imported_count % 1000 == 0:
                        logger.info(f"   Imported {imported_count} sensor records...")

                except Exception as e:
                    logger.warning(f"Error importing sensor data row {row_index + 1}: {e}")
                    skipped_count += 1

        logger.info(f"✅ Imported {imported_count} sensor status records, skipped {skipped_count} due to critical errors")

    except Exception as e:
        logger.error(f"Failed to import sensor data: {e}")
        create_sample_status_data(cursor)

def create_sample_victoria_data(cursor):
    """Create sample Victoria population growth data"""

    logger.info("📝 Creating sample Victoria population data...")

    sample_data = [
        ("Between 2016 and 2017", 87500, 1.3),
        ("Between 2017 and 2018", 92300, 1.4),
        ("Between 2018 and 2019", 89700, 1.3),
        ("Between 2019 and 2020", 78400, 1.1),
        ("Between 2020 and 2021", 45200, 0.7)
    ]

    for period, increase, rate in sample_data:
        cursor.execute('''
            INSERT OR REPLACE INTO victoria_population_growth 
            (year_period, population_increase, growth_rate)
            VALUES (?, ?, ?)
        ''', (period, increase, rate))

    logger.info("✅ Created sample Victoria population data")

def create_sample_melbourne_data(cursor):
    """Create sample Melbourne population history data"""

    logger.info("📝 Creating sample Melbourne population data...")

    sample_areas = [
        ("201011001", "Melbourne", "Melbourne", "Melbourne - Inner",
         8500, 9200, 10100, 11300, 12800, 14500, 16200, 18100, 20000, 22500,
         25000, 27800, 30500, 33200, 35800, 38500, 41200, 44000, 46800, 49500, 52000,
         27000, 108.0, 15.2, 3421.1),
        ("201011002", "Melbourne - Remainder", "Melbourne", "Melbourne - Inner",
         2800, 3100, 3400, 3700, 4100, 4500, 4900, 5400, 5800, 6300,
         6800, 7400, 8000, 8600, 9200, 9800, 10400, 11000, 11600, 12200, 12800,
         6000, 88.2, 8.7, 147.1)
    ]

    for area_data in sample_areas:
        cursor.execute('''
            INSERT OR REPLACE INTO melbourne_population_history (
                sa2_code, sa2_name, sa3_name, sa4_name,
                year_2001, year_2002, year_2003, year_2004, year_2005,
                year_2006, year_2007, year_2008, year_2009, year_2010,
                year_2011, year_2012, year_2013, year_2014, year_2015,
                year_2016, year_2017, year_2018, year_2019, year_2020,
                year_2021, population_change_2011_2021, growth_rate_2011_2021,
                area_km2, population_density_2021
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', area_data)

    logger.info("✅ Created sample Melbourne population data")

def create_sample_parking_bays(cursor):
    """Create sample parking bays data for demonstration"""

    logger.info("📝 Creating sample parking bays data...")

    sample_bays = [
        (1001, 100, "Collins Street between William Street and Queen Street", -37.8136, 144.9631, "Collins St"),
        (1002, 100, "Collins Street between William Street and Queen Street", -37.8135, 144.9635, "Collins St"),
        (1003, 101, "Bourke Street between William Street and Queen Street", -37.8139, 144.9634, "Bourke St"),
        (1004, 101, "Bourke Street between William Street and Queen Street", -37.8138, 144.9638, "Bourke St"),
        (1005, 102, "Flinders Street between William Street and Queen Street", -37.8183, 144.9648, "Flinders St"),
        (1006, 102, "Flinders Street between William Street and Queen Street", -37.8182, 144.9652, "Flinders St"),
        (1007, 103, "Little Collins Street between William Street and Queen Street", -37.8151, 144.9645, "Little Collins St"),
        (1008, 103, "Little Collins Street between William Street and Queen Street", -37.8150, 144.9649, "Little Collins St"),
    ]

    for bay_data in sample_bays:
        cursor.execute('''
            INSERT OR REPLACE INTO parking_bays 
            (kerbside_id, road_segment_id, road_segment_description, latitude, longitude, location_string)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', bay_data)

    logger.info(f"✅ Created {len(sample_bays)} sample parking bays")

def create_sample_status_data(cursor):
    """Create sample status data for demonstration"""

    logger.info("📝 Creating sample status data...")

    # Get parking bay IDs
    cursor.execute("SELECT kerbside_id FROM parking_bays LIMIT 8")
    bay_ids = [row[0] for row in cursor.fetchall()]

    # Create varied status data
    sample_statuses = [
        "Unoccupied", "Occupied", "Unoccupied", "Unoccupied",
        "Occupied", "Unoccupied", "Occupied", "Unoccupied"
    ]

    for i, bay_id in enumerate(bay_ids):
        status = sample_statuses[i] if i < len(sample_statuses) else "Unoccupied"
        zone = (i % 3) + 1  # Zones 1, 2, 3

        cursor.execute('''
            INSERT OR REPLACE INTO parking_status_current 
            (kerbside_id, zone_number, status_description)
            VALUES (?, ?, ?)
        ''', (bay_id, zone, status))

        cursor.execute('''
            INSERT INTO parking_status_history 
            (kerbside_id, zone_number, status_description, data_collected_at)
            VALUES (?, ?, ?, ?)
        ''', (bay_id, zone, status, datetime.now()))

    logger.info(f"✅ Created {len(bay_ids)} sample status records")

def verify_data_import(cursor):
    """Verify and report data import results"""

    logger.info("📊 Verifying data import...")

    # Count records in each table
    bay_count = cursor.execute("SELECT COUNT(*) FROM parking_bays").fetchone()[0]
    current_status_count = cursor.execute("SELECT COUNT(*) FROM parking_status_current").fetchone()[0]
    history_count = cursor.execute("SELECT COUNT(*) FROM parking_status_history").fetchone()[0]
    victoria_count = cursor.execute("SELECT COUNT(*) FROM victoria_population_growth").fetchone()[0]
    melbourne_count = cursor.execute("SELECT COUNT(*) FROM melbourne_population_history").fetchone()[0]

    # Count available vs occupied
    available_count = cursor.execute(
        "SELECT COUNT(*) FROM parking_status_current WHERE status_description = 'Unoccupied'"
    ).fetchone()[0]

    logger.info("📈 Import Summary:")
    logger.info(f"   🅿️  Parking Bays: {bay_count}")
    logger.info(f"   📡 Current Status: {current_status_count}")
    logger.info(f"   📚 History Records: {history_count}")
    logger.info(f"   🏛️ Victoria Population Records: {victoria_count}")
    logger.info(f"   🏙️ Melbourne Population Records: {melbourne_count}")
    logger.info(f"   🟢 Available Spaces: {available_count}")
    logger.info(f"   🔴 Occupied Spaces: {current_status_count - available_count}")

if __name__ == "__main__":
    init_render_database()
