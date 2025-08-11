#!/usr/bin/env python3
"""
Melbourne Parking Website - Railway Data Import Script
Purpose: Import CSV data into Railway PostgreSQL database
Created: August 11, 2025
Note: This is a temporary script that can be deleted after successful import
"""

import psycopg2
import pandas as pd
import os
import sys
from datetime import datetime
import logging
from urllib.parse import urlparse

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayDataImporter:
    def __init__(self, database_url=None):
        """
        Initialize the Railway data importer

        Args:
            database_url (str): Railway DATABASE_URL environment variable
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Parse Railway DATABASE_URL format: postgresql://user:pass@host:port/dbname
        self.db_config = self._parse_database_url(self.database_url)

        # Set CSV path - try multiple possible locations
        possible_paths = [
            "/app",  # Railway deployment path
            "/app/melbourne-parking-website",  # If deployed from subdirectory
            ".",     # Current directory
            ".."     # Parent directory
        ]

        self.csv_path = None
        for path in possible_paths:
            test_file = os.path.join(path, "on-street-parking-bays.csv")
            if os.path.exists(test_file):
                self.csv_path = path
                break

        if not self.csv_path:
            # Default to /app and let individual methods handle file not found
            self.csv_path = "/app"

        logger.info(f"Using CSV path: {self.csv_path}")

    def _parse_database_url(self, url):
        """Parse PostgreSQL URL into connection parameters"""
        try:
            parsed = urlparse(url)
            return {
                'host': parsed.hostname,
                'port': parsed.port,
                'database': parsed.path[1:],  # Remove leading slash
                'user': parsed.username,
                'password': parsed.password
            }
        except Exception as e:
            logger.error(f"Failed to parse DATABASE_URL: {e}")
            raise

    def get_database_connection(self):
        """Create PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False  # Use transactions
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def safe_int_convert(self, value):
        """Safely convert value to integer, handling NaN and invalid data"""
        if pd.isna(value):
            return None
        try:
            # Handle string values that might be 'nan'
            if isinstance(value, str) and value.lower() == 'nan':
                return None
            return int(float(value))  # Convert to float first, then int
        except (ValueError, TypeError, OverflowError):
            return None

    def safe_float_convert(self, value):
        """Safely convert value to float, handling NaN and invalid data"""
        if pd.isna(value):
            return None
        try:
            if isinstance(value, str) and value.lower() == 'nan':
                return None
            result = float(value)
            # Check for overflow
            if abs(result) > 1e10:  # Reasonable limit
                return None
            return result
        except (ValueError, TypeError, OverflowError):
            return None

    def safe_string_convert(self, value):
        """Safely convert value to string, handling NaN"""
        if pd.isna(value):
            return None
        return str(value)

    def import_victoria_population_data(self):
        """Import Victoria population growth data from Australian Bureau of Statistics CSV"""
        logger.info("🏛️ Importing Victoria population growth data...")

        try:
            csv_file = os.path.join(self.csv_path, "Australian Bureau of Statistics (1).csv")

            if not os.path.exists(csv_file):
                logger.warning(f"CSV file not found: {csv_file}")
                return

            # Read CSV with specific parameters for this file format
            df = pd.read_csv(csv_file, skiprows=1)

            # Find Victoria row
            vic_row = df[df.iloc[:, 0].str.contains('Vic.', na=False)]

            if vic_row.empty:
                logger.warning("Victoria data not found in the CSV file")
                return

            conn = self.get_database_connection()
            cursor = conn.cursor()

            # Extract Victoria data for different periods
            vic_data = vic_row.iloc[0]

            # Parse the data structure - columns are paired (number, percentage)
            periods = [
                ("Between 2016 and 2017", 2, 3),
                ("Between 2017 and 2018", 4, 5),
                ("Between 2018 and 2019", 6, 7),
                ("Between 2019 and 2020", 8, 9),
                ("Between 2020 and 2021", 10, 11)
            ]

            success_count = 0
            for period, num_col, rate_col in periods:
                try:
                    # Clean and convert the data safely
                    pop_increase_raw = vic_data.iloc[num_col] if len(vic_data) > num_col else None
                    growth_rate_raw = vic_data.iloc[rate_col] if len(vic_data) > rate_col else None

                    # Safe conversion
                    pop_increase = None
                    if pd.notna(pop_increase_raw):
                        # Remove commas and convert
                        clean_value = str(pop_increase_raw).replace(',', '').strip()
                        pop_increase = self.safe_int_convert(clean_value)

                    growth_rate = self.safe_float_convert(growth_rate_raw)

                    cursor.execute("""
                        INSERT INTO victoria_population_growth 
                        (year_period, population_increase, growth_rate)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (period, pop_increase, growth_rate))

                    success_count += 1
                    logger.info(f"✅ Imported Victoria data for {period}")

                except Exception as e:
                    logger.error(f"Error processing period {period}: {e}")
                    continue

            conn.commit()
            logger.info(f"✅ Victoria population data import completed - {success_count} records")

        except Exception as e:
            logger.error(f"Failed to import Victoria population data: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def import_melbourne_population_history(self):
        """Import Melbourne area population history data"""
        logger.info("🏙️ Importing Melbourne population history data...")

        try:
            csv_file = os.path.join(self.csv_path, "only_melbourne_city_1_without_none.csv")

            if not os.path.exists(csv_file):
                logger.warning(f"CSV file not found: {csv_file}")
                return

            df = pd.read_csv(csv_file)
            logger.info(f"Found {len(df)} rows to process")

            conn = self.get_database_connection()
            cursor = conn.cursor()

            success_count = 0
            for index, row in df.iterrows():
                try:
                    # Safe conversion for all numeric fields
                    data = (
                        self.safe_string_convert(row.get('SA2 code')),
                        self.safe_string_convert(row.get('SA2 name')),
                        self.safe_string_convert(row.get('SA3 name')),
                        self.safe_string_convert(row.get('SA4 name')),
                        self.safe_int_convert(row.get('2001 no.')),
                        self.safe_int_convert(row.get('2002 no.')),
                        self.safe_int_convert(row.get('2003 no.')),
                        self.safe_int_convert(row.get('2004 no.')),
                        self.safe_int_convert(row.get('2005 no.')),
                        self.safe_int_convert(row.get('2006 no.')),
                        self.safe_int_convert(row.get('2007 no.')),
                        self.safe_int_convert(row.get('2008 no.')),
                        self.safe_int_convert(row.get('2009 no.')),
                        self.safe_int_convert(row.get('2010 no.')),
                        self.safe_int_convert(row.get('2011 no.')),
                        self.safe_int_convert(row.get('2012 no.')),
                        self.safe_int_convert(row.get('2013 no.')),
                        self.safe_int_convert(row.get('2014 no.')),
                        self.safe_int_convert(row.get('2015 no.')),
                        self.safe_int_convert(row.get('2016 no.')),
                        self.safe_int_convert(row.get('2017 no.')),
                        self.safe_int_convert(row.get('2018 no.')),
                        self.safe_int_convert(row.get('2019 no.')),
                        self.safe_int_convert(row.get('2020 no.')),
                        self.safe_int_convert(row.get('2021 no.')),
                        self.safe_int_convert(row.get('2011-2021 no.')),
                        self.safe_float_convert(row.get('2011-2021 %')),
                        self.safe_float_convert(row.get('Area km2')),
                        self.safe_float_convert(row.get('Population density 2021 persons/km2'))
                    )

                    cursor.execute("""
                        INSERT INTO melbourne_population_history (
                            sa2_code, sa2_name, sa3_name, sa4_name,
                            year_2001, year_2002, year_2003, year_2004, year_2005,
                            year_2006, year_2007, year_2008, year_2009, year_2010,
                            year_2011, year_2012, year_2013, year_2014, year_2015,
                            year_2016, year_2017, year_2018, year_2019, year_2020, year_2021,
                            population_change_2011_2021, growth_rate_2011_2021,
                            area_km2, population_density_2021
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT DO NOTHING
                    """, data)

                    success_count += 1

                    # Progress update every 10 records
                    if success_count % 10 == 0:
                        logger.info(f"   Processed {success_count} population records...")

                except Exception as e:
                    logger.error(f"Error importing row {index} for {row.get('SA2 name', 'Unknown')}: {e}")
                    continue

            conn.commit()
            logger.info(f"✅ Melbourne population history import completed - {success_count} records")

        except Exception as e:
            logger.error(f"Failed to import Melbourne population history: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def import_parking_bays_data(self):
        """Import parking bays static information"""
        logger.info("🅿️ Importing parking bays data...")

        try:
            csv_file = os.path.join(self.csv_path, "on-street-parking-bays.csv")

            if not os.path.exists(csv_file):
                logger.warning(f"CSV file not found: {csv_file}")
                return

            df = pd.read_csv(csv_file)
            logger.info(f"Found {len(df)} parking bay records to process")

            conn = self.get_database_connection()
            cursor = conn.cursor()

            success_count = 0
            for index, row in df.iterrows():
                try:
                    # Skip rows with missing essential data
                    kerbside_id = self.safe_int_convert(row.get('KerbsideID'))
                    latitude = self.safe_float_convert(row.get('Latitude'))
                    longitude = self.safe_float_convert(row.get('Longitude'))

                    if kerbside_id is None or latitude is None or longitude is None:
                        continue

                    # Convert last_updated to date if available
                    last_updated = None
                    if pd.notna(row.get('LastUpdated')):
                        try:
                            last_updated = datetime.strptime(str(row.get('LastUpdated')), '%Y-%m-%d').date()
                        except:
                            last_updated = None

                    # Safe conversion for other fields
                    road_segment_id = self.safe_int_convert(row.get('RoadSegmentID'))
                    road_segment_description = self.safe_string_convert(row.get('RoadSegmentDescription'))
                    location_string = self.safe_string_convert(row.get('Location'))

                    cursor.execute("""
                        INSERT INTO parking_bays (
                            kerbside_id, road_segment_id, road_segment_description,
                            latitude, longitude, last_updated, location_string
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (kerbside_id) DO UPDATE SET
                            road_segment_id = EXCLUDED.road_segment_id,
                            road_segment_description = EXCLUDED.road_segment_description,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            last_updated = EXCLUDED.last_updated,
                            location_string = EXCLUDED.location_string,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        kerbside_id, road_segment_id, road_segment_description,
                        latitude, longitude, last_updated, location_string
                    ))

                    success_count += 1
                    if success_count % 1000 == 0:
                        logger.info(f"   Imported {success_count} parking bays...")

                except Exception as e:
                    logger.error(f"Error importing parking bay at row {index}: {e}")
                    continue

            conn.commit()
            logger.info(f"✅ Parking bays import completed - {success_count} records imported")

        except Exception as e:
            logger.error(f"Failed to import parking bays data: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def import_parking_sensor_data(self):
        """Import current parking sensor status data"""
        logger.info("📡 Importing parking sensor data...")

        try:
            csv_file = os.path.join(self.csv_path, "on-street-parking-bay-sensors.csv")

            if not os.path.exists(csv_file):
                logger.warning(f"CSV file not found: {csv_file}")
                return

            df = pd.read_csv(csv_file)
            logger.info(f"Found {len(df)} sensor records to process")

            conn = self.get_database_connection()
            cursor = conn.cursor()

            # First, get all valid kerbside_ids from parking_bays table
            cursor.execute("SELECT kerbside_id FROM parking_bays")
            valid_kerbside_ids = set(row[0] for row in cursor.fetchall())
            logger.info(f"Found {len(valid_kerbside_ids)} valid parking bays in database")

            success_count = 0
            skipped_count = 0

            for index, row in df.iterrows():
                try:
                    # Skip rows with missing essential data
                    kerbside_id = self.safe_int_convert(row.get('KerbsideID'))
                    status_description = self.safe_string_convert(row.get('Status_Description'))

                    if kerbside_id is None or not status_description:
                        continue

                    # Skip if kerbside_id doesn't exist in parking_bays table
                    if kerbside_id not in valid_kerbside_ids:
                        skipped_count += 1
                        continue

                    # Parse timestamps safely
                    status_timestamp = None
                    last_updated = None

                    if pd.notna(row.get('Status_Timestamp')):
                        try:
                            status_timestamp = pd.to_datetime(row['Status_Timestamp'])
                        except:
                            pass

                    if pd.notna(row.get('Lastupdated')):
                        try:
                            last_updated = pd.to_datetime(row['Lastupdated'])
                        except:
                            pass

                    zone_number = self.safe_int_convert(row.get('Zone_Number'))

                    # Insert into current status table
                    cursor.execute("""
                        INSERT INTO parking_status_current (
                            kerbside_id, zone_number, status_description,
                            status_timestamp, last_updated
                        ) VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (kerbside_id) DO UPDATE SET
                            zone_number = EXCLUDED.zone_number,
                            status_description = EXCLUDED.status_description,
                            status_timestamp = EXCLUDED.status_timestamp,
                            last_updated = EXCLUDED.last_updated,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        kerbside_id, zone_number, status_description,
                        status_timestamp, last_updated
                    ))

                    # Also insert into history table for initial data
                    cursor.execute("""
                        INSERT INTO parking_status_history (
                            kerbside_id, zone_number, status_description,
                            status_timestamp, last_updated, data_collected_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        kerbside_id, zone_number, status_description,
                        status_timestamp, last_updated, datetime.now()
                    ))

                    success_count += 1
                    if success_count % 1000 == 0:
                        logger.info(f"   Imported {success_count} sensor records...")

                except Exception as e:
                    logger.error(f"Error importing sensor data at row {index}: {e}")
                    continue

            conn.commit()
            logger.info(f"✅ Parking sensor data import completed")
            logger.info(f"   Successfully imported: {success_count} records")
            logger.info(f"   Skipped (no matching parking bay): {skipped_count} records")

        except Exception as e:
            logger.error(f"Failed to import parking sensor data: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def verify_tables_exist(self):
        """Verify that all required tables exist in the database"""
        logger.info("🔍 Verifying database tables exist...")

        required_tables = [
            'victoria_population_growth',
            'melbourne_population_history',
            'parking_bays',
            'parking_status_current',
            'parking_status_history',
            'parking_hourly_stats',
            'api_collection_log'
        ]

        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            # Check which tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)

            existing_tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Found existing tables: {existing_tables}")

            missing_tables = [table for table in required_tables if table not in existing_tables]

            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                logger.info("💡 You may need to run the database initialization script first")
                return False
            else:
                logger.info("✅ All required tables exist")
                return True

        except Exception as e:
            logger.error(f"Failed to verify tables: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_table_counts(self):
        """Get the current record count for each table"""
        logger.info("📊 Checking current table record counts...")

        tables = [
            'victoria_population_growth',
            'melbourne_population_history',
            'parking_bays',
            'parking_status_current',
            'parking_status_history'
        ]

        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()

            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"   {table}: {count} records")
                except Exception as e:
                    logger.error(f"   {table}: Error - {e}")

        except Exception as e:
            logger.error(f"Failed to get table counts: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def run_full_import(self):
        """Execute complete data import process"""
        logger.info("🚀 Starting Railway Melbourne Parking System data import...")

        try:
            # Test database connection first
            conn = self.get_database_connection()
            conn.close()
            logger.info("✅ Database connection successful")

            # Verify all tables exist
            if not self.verify_tables_exist():
                logger.error("❌ Required tables are missing. Please run database initialization first.")
                return False

            # Show current table counts
            self.get_table_counts()

            # Import data in logical order - each with independent error handling
            logger.info("📊 Starting data import sequence...")

            try:
                self.import_victoria_population_data()
            except Exception as e:
                logger.error(f"Victoria population import failed: {e}")

            try:
                self.import_melbourne_population_history()
            except Exception as e:
                logger.error(f"Melbourne population history import failed: {e}")

            try:
                self.import_parking_bays_data()
            except Exception as e:
                logger.error(f"Parking bays import failed: {e}")

            try:
                self.import_parking_sensor_data()
            except Exception as e:
                logger.error(f"Parking sensor data import failed: {e}")

            # Show final table counts
            logger.info("📈 Final table counts after import:")
            self.get_table_counts()

            logger.info("🎉 Complete Railway data import finished!")
            logger.info("💡 This script can now be safely deleted from your project")
            return True

        except Exception as e:
            logger.error(f"Data import process failed: {e}")
            return False

def main():
    """Main function to run the Railway data import"""
    try:
        # Get DATABASE_URL from Railway environment
        database_url = os.getenv('DATABASE_URL')

        if not database_url:
            logger.error("DATABASE_URL environment variable not found")
            logger.info("Make sure you're running this in Railway environment with DATABASE_URL set")
            sys.exit(1)

        # Create importer and run
        importer = RailwayDataImporter(database_url)
        importer.run_full_import()

        logger.info("✨ Import completed successfully!")

    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
