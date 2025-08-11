#!/usr/bin/env python3
"""
Render Data Initialization Script
Purpose: Initialize PostgreSQL database with parking data for Render deployment
Author: Melbourne Parking System
Date: August 12, 2025
"""

import os
import psycopg2
from psycopg2.extras import execute_values
import csv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_render_database():
    """Initialize PostgreSQL database with essential data for Render deployment"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not found")
        return False

    logger.info(f"🗄️ Connecting to PostgreSQL database...")

    try:
        # Create database connection
        conn = psycopg2.connect(database_url)
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
        return True

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def create_database_tables(cursor):
    """Create all database tables with proper schema"""

    logger.info("📋 Creating database tables...")

    # Create victoria_population_growth table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS victoria_population_growth (
            id SERIAL PRIMARY KEY,
            year_period VARCHAR(50) NOT NULL,
            population_number INTEGER NOT NULL,
            growth_rate DECIMAL(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create melbourne_population_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS melbourne_population_history (
            id SERIAL PRIMARY KEY,
            sa2_code VARCHAR(20),
            sa2_name VARCHAR(100) NOT NULL,
            sa3_name VARCHAR(100),
            sa4_name VARCHAR(100),
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
            id SERIAL PRIMARY KEY,
            kerbside_id INTEGER NOT NULL,
            zone_number INTEGER,
            status_description VARCHAR(20) NOT NULL,
            status_timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kerbside_id) REFERENCES parking_bays (kerbside_id)
        )
    ''')

    logger.info("✅ Database tables created")

def import_all_data(cursor):
    """Import data from all CSV files without any limits"""

    # Import Victoria population data
    victoria_csv = os.path.join('..', '..', 'Australian Bureau of Statistics (1).csv')
    import_victoria_population(cursor, victoria_csv)

    # Import Melbourne population data
    melbourne_csv = os.path.join('..', '..', 'only_melbourne_city_1_without_none.csv')
    import_melbourne_population(cursor, melbourne_csv)

    # Import parking bays data
    parking_bays_csv = os.path.join('..', '..', 'on-street-parking-bays.csv')
    import_parking_bays_from_csv(cursor, parking_bays_csv)

    # Import sensor status data
    sensor_csv = os.path.join('..', '..', 'on-street-parking-bay-sensors.csv')
    import_sensor_status_from_csv(cursor, sensor_csv)

def _safe_int(value):
    """Safely convert value to integer, return None for invalid values"""
    if value is None or value == '' or value == 'nan' or str(value).strip() == '':
        return None
    try:
        return int(float(str(value).replace(',', '')))
    except (ValueError, TypeError):
        return None

def _safe_float(value):
    """Safely convert value to float, return None for invalid values"""
    if value is None or value == '' or value == 'nan' or str(value).strip() == '':
        return None
    try:
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError):
        return None

def import_victoria_population(cursor, csv_file):
    """Import Victoria population growth data without limits"""

    logger.info(f"🏛️ Importing Victoria population from {csv_file}")

    if not os.path.exists(csv_file):
        logger.warning(f"Victoria population file not found: {csv_file}")
        return

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data_to_insert = []

            for row in reader:
                # Import ALL records without limits
                year_period = row.get('Time', '').strip()
                if year_period and 'Between' in year_period:
                    population_str = row.get('Value', '').strip()
                    if population_str and population_str != 'np':
                        try:
                            population = int(float(population_str))
                            data_to_insert.append((year_period, population, 2.5))
                        except (ValueError, TypeError):
                            continue

            # Bulk insert all data
            if data_to_insert:
                execute_values(
                    cursor,
                    "INSERT INTO victoria_population_growth (year_period, population_number, growth_rate) VALUES %s ON CONFLICT DO NOTHING",
                    data_to_insert
                )
                logger.info(f"✅ Victoria population data import completed - {len(data_to_insert)} records")
            else:
                logger.warning("⚠️  No Victoria population data found to import")

    except Exception as e:
        logger.error(f"❌ Error importing Victoria population: {e}")

def import_melbourne_population(cursor, csv_file):
    """Import Melbourne population history data without limits"""

    logger.info(f"🏙️ Importing Melbourne population from {csv_file}")

    if not os.path.exists(csv_file):
        logger.warning(f"Melbourne population file not found: {csv_file}")
        return

    imported_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data_to_insert = []

            for row in reader:
                # Import ALL records without limits
                try:
                    # Extract all required fields
                    data_row = (
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
                        _safe_int(row.get('Change (2011-2021)')),
                        _safe_float(row.get('Growth rate (2011-2021)')),
                        _safe_float(row.get('Area (km2)')),
                        _safe_float(row.get('Density (persons/km2) 2021'))
                    )

                    data_to_insert.append(data_row)
                    imported_count += 1

                    # Log progress for every 1000 records
                    if imported_count % 1000 == 0:
                        logger.info(f"   Processed {imported_count} Melbourne population records...")

                except Exception as e:
                    logger.warning(f"Skipped row: {e}")
                    continue

            # Bulk insert all data
            if data_to_insert:
                execute_values(
                    cursor,
                    """INSERT INTO melbourne_population_history (
                        sa2_code, sa2_name, sa3_name, sa4_name,
                        year_2001, year_2002, year_2003, year_2004, year_2005,
                        year_2006, year_2007, year_2008, year_2009, year_2010,
                        year_2011, year_2012, year_2013, year_2014, year_2015,
                        year_2016, year_2017, year_2018, year_2019, year_2020,
                        year_2021, population_change_2011_2021, growth_rate_2011_2021,
                        area_km2, population_density_2021
                    ) VALUES %s ON CONFLICT DO NOTHING""",
                    data_to_insert
                )
                logger.info(f"✅ Melbourne population import completed - {len(data_to_insert)} records")
            else:
                logger.warning("⚠️  No Melbourne population data found to import")

    except Exception as e:
        logger.error(f"❌ Error importing Melbourne population: {e}")

def import_parking_bays_from_csv(cursor, csv_file):
    """Import parking bays data from CSV file without limits"""

    logger.info(f"🅿️ Importing parking bays from {csv_file}")

    if not os.path.exists(csv_file):
        logger.warning(f"Parking bays file not found: {csv_file}")
        return

    imported_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data_to_insert = []

            for row in reader:
                # Import ALL records without limits
                try:
                    # Validate required fields
                    if not all([row.get('KerbsideID'), row.get('Latitude'), row.get('Longitude')]):
                        continue

                    kerbside_id = int(row['KerbsideID'])
                    latitude = float(row['Latitude'])
                    longitude = float(row['Longitude'])

                    # Parse optional fields
                    road_segment_id = None
                    if row.get('RoadSegmentID') and row['RoadSegmentID'].strip():
                        try:
                            road_segment_id = int(row['RoadSegmentID'])
                        except:
                            pass

                    # Prepare data for bulk insert
                    data_row = (
                        kerbside_id,
                        road_segment_id,
                        row.get('RoadSegment', ''),
                        latitude,
                        longitude,
                        datetime.now().date(),
                        f"{latitude},{longitude}"
                    )

                    data_to_insert.append(data_row)
                    imported_count += 1

                    # Log progress for every 1000 records
                    if imported_count % 1000 == 0:
                        logger.info(f"   Processed {imported_count} parking bay records...")

                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipped invalid parking bay row: {e}")
                    continue

            # Bulk insert all data
            if data_to_insert:
                execute_values(
                    cursor,
                    """INSERT INTO parking_bays (
                        kerbside_id, road_segment_id, road_segment_description,
                        latitude, longitude, last_updated, location_string
                    ) VALUES %s ON CONFLICT (kerbside_id) DO UPDATE SET
                        road_segment_id = EXCLUDED.road_segment_id,
                        road_segment_description = EXCLUDED.road_segment_description,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        last_updated = EXCLUDED.last_updated,
                        location_string = EXCLUDED.location_string,
                        updated_at = CURRENT_TIMESTAMP""",
                    data_to_insert
                )
                logger.info(f"✅ Parking bays import completed - {len(data_to_insert)} records")
            else:
                logger.warning("⚠️  No parking bays data found to import")

    except Exception as e:
        logger.error(f"❌ Error importing parking bays: {e}")

def import_sensor_status_from_csv(cursor, csv_file):
    """Import sensor status data from CSV file without limits"""

    logger.info(f"📡 Importing sensor status from {csv_file}")

    if not os.path.exists(csv_file):
        logger.warning(f"Sensor status file not found: {csv_file}")
        # Create mock status data for all parking bays
        create_mock_status_data(cursor)
        return

    imported_count = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            current_data = []
            history_data = []

            for row in reader:
                # Import ALL records without limits
                try:
                    kerbside_id_str = str(row.get('kerbside_id', '')).strip()
                    if kerbside_id_str and kerbside_id_str != 'nan':
                        kerbside_id = int(float(kerbside_id_str))

                        # Use actual status or generate realistic one
                        status = row.get('status', '').strip()
                        if not status:
                            status = 'Present' if imported_count % 3 == 0 else 'Unoccupied'

                        timestamp = datetime.now()

                        # Prepare data for bulk insert
                        current_data.append((
                            kerbside_id, 1, status, timestamp, timestamp
                        ))

                        history_data.append((
                            kerbside_id, 1, status, timestamp
                        ))

                        imported_count += 1

                        # Log progress for every 1000 records
                        if imported_count % 1000 == 0:
                            logger.info(f"   Processed {imported_count} sensor status records...")

                except (ValueError, TypeError):
                    continue

            # Bulk insert current status
            if current_data:
                execute_values(
                    cursor,
                    """INSERT INTO parking_status_current (
                        kerbside_id, zone_number, status_description, last_updated, status_timestamp
                    ) VALUES %s ON CONFLICT (kerbside_id) DO UPDATE SET
                        zone_number = EXCLUDED.zone_number,
                        status_description = EXCLUDED.status_description,
                        last_updated = EXCLUDED.last_updated,
                        status_timestamp = EXCLUDED.status_timestamp,
                        updated_at = CURRENT_TIMESTAMP""",
                    current_data
                )

            # Bulk insert history
            if history_data:
                execute_values(
                    cursor,
                    """INSERT INTO parking_status_history (
                        kerbside_id, zone_number, status_description, status_timestamp
                    ) VALUES %s""",
                    history_data
                )

            logger.info(f"✅ Sensor status import completed - {len(current_data)} current records, {len(history_data)} history records")

    except Exception as e:
        logger.error(f"❌ Error importing sensor status: {e}")
        create_mock_status_data(cursor)

def create_mock_status_data(cursor):
    """Create mock status data for all parking bays"""

    logger.info("🎭 Creating mock status data for parking bays...")

    try:
        # Get all parking bay IDs
        cursor.execute("SELECT kerbside_id FROM parking_bays")
        bay_ids = [row[0] for row in cursor.fetchall()]

        current_data = []
        history_data = []

        for i, bay_id in enumerate(bay_ids):
            # Realistic status distribution: 40% occupied, 60% available
            status = 'Present' if i % 5 < 2 else 'Unoccupied'
            timestamp = datetime.now()

            current_data.append((bay_id, 1, status, timestamp, timestamp))
            history_data.append((bay_id, 1, status, timestamp))

        # Bulk insert current status
        if current_data:
            execute_values(
                cursor,
                """INSERT INTO parking_status_current (
                    kerbside_id, zone_number, status_description, last_updated, status_timestamp
                ) VALUES %s ON CONFLICT (kerbside_id) DO NOTHING""",
                current_data
            )

        # Bulk insert history
        if history_data:
            execute_values(
                cursor,
                """INSERT INTO parking_status_history (
                    kerbside_id, zone_number, status_description, status_timestamp
                ) VALUES %s""",
                history_data
            )

        logger.info(f"✅ Mock status data created - {len(current_data)} records")

    except Exception as e:
        logger.error(f"❌ Error creating mock status data: {e}")

def verify_data_import(cursor):
    """Verify and report the results of data import"""

    logger.info("📊 Data verification:")

    try:
        # Check table record counts
        tables = [
            'victoria_population_growth',
            'melbourne_population_history',
            'parking_bays',
            'parking_status_current',
            'parking_status_history'
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"   - {table}: {count:,}")

        # Check available vs occupied parking
        cursor.execute("""
            SELECT 
                status_description,
                COUNT(*) as count
            FROM parking_status_current 
            GROUP BY status_description
        """)

        status_counts = cursor.fetchall()
        for status, count in status_counts:
            logger.info(f"   - {status} Spots: {count:,}")

        # Sample data check
        cursor.execute("SELECT * FROM parking_bays LIMIT 3")
        sample_bays = cursor.fetchall()
        logger.info("📋 Sample parking bays:")
        for bay in sample_bays:
            logger.info(f"   Bay {bay[0]} at ({bay[3]:.4f}, {bay[4]:.4f})")

    except Exception as e:
        logger.error(f"❌ Data verification failed: {e}")

if __name__ == '__main__':
    success = init_render_database()
    exit(0 if success else 1)
