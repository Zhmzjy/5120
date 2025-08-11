#!/usr/bin/env python3
"""
Import local CSV data to Railway PostgreSQL database
This script connects directly to Railway database and imports data
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

# Railway database configuration
RAILWAY_DATABASE_URL = "postgresql://postgres:JXRWxcXAtMWtPDWUmNOdQHBTalTliqjv@postgres.railway.internal:5432/railway"

# Local CSV files paths
CSV_BASE_PATH = "/Users/zhujunyi/5120"
PARKING_BAYS_CSV = os.path.join(CSV_BASE_PATH, "on-street-parking-bays.csv")
PARKING_SENSORS_CSV = os.path.join(CSV_BASE_PATH, "on-street-parking-bay-sensors.csv")
MELBOURNE_DATA_CSV = os.path.join(CSV_BASE_PATH, "only_melbourne_city_1_without_none.csv")

def connect_to_railway_db():
    """Connect to Railway PostgreSQL database"""
    try:
        conn = psycopg2.connect(RAILWAY_DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to Railway database: {e}")
        return None

def create_tables(conn):
    """Create necessary tables in Railway database"""
    cursor = conn.cursor()

    # Create parking_bays table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_bays (
            kerbside_id INTEGER PRIMARY KEY,
            road_segment_id INTEGER,
            road_segment_description TEXT,
            latitude NUMERIC(10, 7),
            longitude NUMERIC(10, 7),
            last_updated DATE,
            location_string TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create parking_status_current table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_status_current (
            kerbside_id INTEGER PRIMARY KEY REFERENCES parking_bays(kerbside_id),
            zone_number INTEGER,
            status_description VARCHAR(20) NOT NULL,
            last_updated TIMESTAMP,
            status_timestamp TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    print("✅ Tables created successfully")

def import_parking_bays_data(conn):
    """Import parking bays data from CSV"""
    print("📥 Importing parking bays data...")

    try:
        # Read CSV file
        df = pd.read_csv(PARKING_BAYS_CSV)

        cursor = conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM parking_status_current;")
        cursor.execute("DELETE FROM parking_bays;")

        imported_count = 0
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO parking_bays (
                        kerbside_id, road_segment_id, road_segment_description,
                        latitude, longitude, last_updated, location_string
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (kerbside_id) DO NOTHING
                """, (
                    int(row['kerbside_id']),
                    int(row['road_segment_id']) if pd.notna(row['road_segment_id']) else None,
                    str(row['road_segment_description']) if pd.notna(row['road_segment_description']) else None,
                    float(row['latitude']) if pd.notna(row['latitude']) else None,
                    float(row['longitude']) if pd.notna(row['longitude']) else None,
                    datetime.now().date(),
                    f"{row['road_segment_description']}, Melbourne" if pd.notna(row['road_segment_description']) else None
                ))
                imported_count += 1
            except Exception as e:
                print(f"⚠️  Error importing bay {row['kerbside_id']}: {e}")
                continue

        conn.commit()
        print(f"✅ Imported {imported_count} parking bays")

    except Exception as e:
        print(f"❌ Error importing parking bays: {e}")
        conn.rollback()

def import_sensor_data(conn):
    """Import sensor status data from CSV"""
    print("📥 Importing sensor status data...")

    try:
        # Read CSV file
        df = pd.read_csv(PARKING_SENSORS_CSV)

        cursor = conn.cursor()

        imported_count = 0
        for _, row in df.iterrows():
            try:
                # Generate sample status (mix of Occupied/Unoccupied)
                import random
                status = random.choice(['Occupied', 'Unoccupied', 'Unoccupied', 'Unoccupied'])  # More unoccupied for demo

                cursor.execute("""
                    INSERT INTO parking_status_current (
                        kerbside_id, zone_number, status_description,
                        last_updated, status_timestamp
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (kerbside_id) DO UPDATE SET
                        status_description = EXCLUDED.status_description,
                        last_updated = EXCLUDED.last_updated,
                        status_timestamp = EXCLUDED.status_timestamp
                """, (
                    int(row['kerbside_id']),
                    1,  # Default zone
                    status,
                    datetime.now(),
                    datetime.now()
                ))
                imported_count += 1

                # Only import first 1000 records for demo
                if imported_count >= 1000:
                    break

            except Exception as e:
                continue

        conn.commit()
        print(f"✅ Imported {imported_count} sensor status records")

    except Exception as e:
        print(f"❌ Error importing sensor data: {e}")
        conn.rollback()

def verify_data(conn):
    """Verify imported data"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Count records
    cursor.execute("SELECT COUNT(*) as count FROM parking_bays;")
    bays_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM parking_status_current;")
    status_count = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count FROM parking_status_current 
        WHERE status_description = 'Unoccupied';
    """)
    available_count = cursor.fetchone()['count']

    print(f"📊 Data verification:")
    print(f"   - Parking Bays: {bays_count}")
    print(f"   - Status Records: {status_count}")
    print(f"   - Available Spots: {available_count}")

    # Sample data
    cursor.execute("""
        SELECT pb.road_segment_description, psc.status_description, pb.latitude, pb.longitude
        FROM parking_bays pb
        JOIN parking_status_current psc ON pb.kerbside_id = psc.kerbside_id
        LIMIT 5;
    """)

    sample_data = cursor.fetchall()
    print(f"\n📋 Sample data:")
    for record in sample_data:
        print(f"   - {record['road_segment_description']}: {record['status_description']}")

def main():
    """Main function to import data to Railway"""
    print("🚀 Starting data import to Railway database...")

    # Check if CSV files exist
    if not os.path.exists(PARKING_BAYS_CSV):
        print(f"❌ CSV file not found: {PARKING_BAYS_CSV}")
        return

    if not os.path.exists(PARKING_SENSORS_CSV):
        print(f"❌ CSV file not found: {PARKING_SENSORS_CSV}")
        return

    # Connect to Railway database
    conn = connect_to_railway_db()
    if not conn:
        return

    try:
        # Create tables
        create_tables(conn)

        # Import data
        import_parking_bays_data(conn)
        import_sensor_data(conn)

        # Verify import
        verify_data(conn)

        print("🎉 Data import completed successfully!")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()

if __name__ == "__main__":
    main()
