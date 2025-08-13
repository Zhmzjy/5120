#!/usr/bin/env python3
"""
Melbourne Parking Website - CSV Data Import Script
Purpose: Import data from CSV files into PostgreSQL database
Created: August 8, 2025
"""

import psycopg2
import pandas as pd
import os
import sys
from datetime import datetime
import logging

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MelbourneDataImporter:
    def __init__(self, db_config):
        """
        Initialize the data importer with database configuration

        Args:
            db_config (dict): Database connection parameters
        """
        self.db_config = db_config
        self.csv_path = r"C:\Users\23651\Desktop\5120\5120"

    def get_database_connection(self):
        """Create PostgreSQL database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def import_victoria_population_data(self):
        """Import Victoria population growth data from Australian Bureau of Statistics CSV"""
        logger.info("🏛️ Importing Victoria population growth data...")

        try:
            # Read the CSV file
            csv_file = os.path.join(self.csv_path, "Australian Bureau of Statistics (1).csv")

            # Read CSV with specific parameters for this file format
            df = pd.read_csv(csv_file, skiprows=1)  # Skip the first row with period headers

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
                ("Between 2016 and 2017", 2, 3),  # columns for number and %
                ("Between 2017 and 2018", 4, 5),
                ("Between 2018 and 2019", 6, 7),
                ("Between 2019 and 2020", 8, 9),
                ("Between 2020 and 2021", 10, 11)
            ]

            for period, num_col, rate_col in periods:
                try:
                    # Clean and convert the data
                    pop_increase = str(vic_data.iloc[num_col]).replace(',', '') if pd.notna(vic_data.iloc[num_col]) else None
                    growth_rate = vic_data.iloc[rate_col] if pd.notna(vic_data.iloc[rate_col]) else None

                    pop_increase = int(pop_increase) if pop_increase and pop_increase != 'nan' else None
                    growth_rate = float(growth_rate) if growth_rate and str(growth_rate) != 'nan' else None

                    cursor.execute("""
                        INSERT INTO victoria_population_growth 
                        (year_period, population_increase, growth_rate)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (period, pop_increase, growth_rate))

                    logger.info(f"✅ Imported Victoria data for {period}")

                except Exception as e:
                    logger.error(f"Error processing period {period}: {e}")
                    continue

            conn.commit()
            logger.info("✅ Victoria population data import completed")

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
            df = pd.read_csv(csv_file)
            
            conn = self.get_database_connection()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                try:
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
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT DO NOTHING
                    """, (
                        row.get('SA2 code'), row.get('SA2 name'),
                        row.get('SA3 name'), row.get('SA4 name'),
                        row.get('2001 no.'), row.get('2002 no.'), row.get('2003 no.'),
                        row.get('2004 no.'), row.get('2005 no.'), row.get('2006 no.'),
                        row.get('2007 no.'), row.get('2008 no.'), row.get('2009 no.'),
                        row.get('2010 no.'), row.get('2011 no.'), row.get('2012 no.'),
                        row.get('2013 no.'), row.get('2014 no.'), row.get('2015 no.'),
                        row.get('2016 no.'), row.get('2017 no.'), row.get('2018 no.'),
                        row.get('2019 no.'), row.get('2020 no.'), row.get('2021 no.'),
                        row.get('2011-2021 no.'), row.get('2011-2021 %'),
                        row.get('Area km2'), row.get('Population density 2021 persons/km2')
                    ))

                except Exception as e:
                    logger.error(f"Error importing row for {row.get('SA2 name', 'Unknown')}: {e}")
                    continue

            conn.commit()
            logger.info("✅ Melbourne population history import completed")

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
            df = pd.read_csv(csv_file)

            conn = self.get_database_connection()
            cursor = conn.cursor()

            imported_count = 0
            for _, row in df.iterrows():
                try:
                    # Skip rows with missing essential data
                    if pd.isna(row.get('KerbsideID')) or pd.isna(row.get('Latitude')) or pd.isna(row.get('Longitude')):
                        continue

                    # Convert last_updated to date if available
                    last_updated = None
                    if pd.notna(row.get('LastUpdated')):
                        try:
                            last_updated = datetime.strptime(str(row.get('LastUpdated')), '%Y-%m-%d').date()
                        except:
                            last_updated = None

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
                        int(row['KerbsideID']),
                        row.get('RoadSegmentID') if pd.notna(row.get('RoadSegmentID')) else None,
                        row.get('RoadSegmentDescription'),
                        float(row['Latitude']),
                        float(row['Longitude']),
                        last_updated,
                        row.get('Location')
                    ))

                    imported_count += 1
                    if imported_count % 1000 == 0:
                        logger.info(f"   Imported {imported_count} parking bays...")

                except Exception as e:
                    logger.error(f"Error importing parking bay {row.get('KerbsideID', 'Unknown')}: {e}")
                    continue

            conn.commit()
            logger.info(f"✅ Parking bays import completed - {imported_count} records imported")

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
            df = pd.read_csv(csv_file)

            conn = self.get_database_connection()
            cursor = conn.cursor()

            # First, get all valid kerbside_ids from parking_bays table
            cursor.execute("SELECT kerbside_id FROM parking_bays")
            valid_kerbside_ids = set(row[0] for row in cursor.fetchall())
            logger.info(f"Found {len(valid_kerbside_ids)} valid parking bays in database")

            imported_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                try:
                    # Skip rows with missing essential data
                    if pd.isna(row.get('KerbsideID')) or pd.isna(row.get('Status_Description')):
                        continue

                    kerbside_id = int(row['KerbsideID'])

                    # Skip if kerbside_id doesn't exist in parking_bays table
                    if kerbside_id not in valid_kerbside_ids:
                        skipped_count += 1
                        continue

                    # Parse timestamps
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
                        kerbside_id,
                        row.get('Zone_Number') if pd.notna(row.get('Zone_Number')) else None,
                        row['Status_Description'],
                        status_timestamp,
                        last_updated
                    ))

                    # Also insert into history table for initial data
                    cursor.execute("""
                        INSERT INTO parking_status_history (
                            kerbside_id, zone_number, status_description,
                            status_timestamp, last_updated, data_collected_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        kerbside_id,
                        row.get('Zone_Number') if pd.notna(row.get('Zone_Number')) else None,
                        row['Status_Description'],
                        status_timestamp,
                        last_updated,
                        datetime.now()
                    ))

                    imported_count += 1
                    if imported_count % 1000 == 0:
                        logger.info(f"   Imported {imported_count} sensor records...")

                except Exception as e:
                    logger.error(f"Error importing sensor data for {row.get('KerbsideID', 'Unknown')}: {e}")
                    continue

            conn.commit()
            logger.info(f"✅ Parking sensor data import completed")
            logger.info(f"   Successfully imported: {imported_count} records")
            logger.info(f"   Skipped (no matching parking bay): {skipped_count} records")

        except Exception as e:
            logger.error(f"Failed to import parking sensor data: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def run_full_import(self):
        """Execute complete data import process"""
        logger.info("🚀 Starting Melbourne Parking System data import...")

        try:
            # Import data in logical order
            self.import_victoria_population_data()
            self.import_melbourne_population_history()
            self.import_parking_bays_data()
            self.import_parking_sensor_data()

            logger.info("🎉 Complete data import finished successfully!")

        except Exception as e:
            logger.error(f"Data import process failed: {e}")
            raise

def main():
    """Main function to run the data import"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'melbourne_parking_system',
        'user': 'melbourne_parking',
        'password': 'zjy0312!',
        'port': 5432
    }

    # Create importer and run
    importer = MelbourneDataImporter(db_config)
    importer.run_full_import()

if __name__ == "__main__":
    main()
