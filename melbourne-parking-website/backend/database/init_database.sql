-- Melbourne Parking System Database Schema
-- PostgreSQL Database Initialization Script
-- Created: August 8, 2025

-- Create database (run this separately as superuser)
-- CREATE DATABASE melbourne_parking_system;

-- Connect to the database before running the following scripts
-- \c melbourne_parking_system;

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- TABLE 1: Victoria Population Growth
-- Purpose: Store Victoria state population growth trends
-- ================================================================
CREATE TABLE IF NOT EXISTS victoria_population_growth (
    id SERIAL PRIMARY KEY,
    year_period VARCHAR(30) NOT NULL,           -- Period like "Between 2016 and 2017"
    population_increase INTEGER,                -- Population increase number
    growth_rate DECIMAL(4,2),                  -- Growth rate percentage (e.g., 4.20%)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for efficient querying
CREATE INDEX IF NOT EXISTS idx_victoria_year_period ON victoria_population_growth(year_period);

-- Add comments
COMMENT ON TABLE victoria_population_growth IS 'Victoria state population growth data by year periods';
COMMENT ON COLUMN victoria_population_growth.year_period IS 'Time period for population measurement';
COMMENT ON COLUMN victoria_population_growth.population_increase IS 'Number of people added during the period';
COMMENT ON COLUMN victoria_population_growth.growth_rate IS 'Population growth rate as percentage';

-- ================================================================
-- TABLE 2: Melbourne Area Population History
-- Purpose: Store detailed population data by SA2 regions (2001-2021)
-- ================================================================
CREATE TABLE IF NOT EXISTS melbourne_population_history (
    id SERIAL PRIMARY KEY,
    sa2_code VARCHAR(20) NOT NULL,             -- Statistical Area Level 2 code
    sa2_name VARCHAR(100) NOT NULL,            -- Area name (Carlton, Docklands, etc.)
    sa3_name VARCHAR(100),                     -- Statistical Area Level 3 name
    sa4_name VARCHAR(100),                     -- Statistical Area Level 4 name

    -- Population data by year (2001-2021)
    year_2001 INTEGER,
    year_2002 INTEGER,
    year_2003 INTEGER,
    year_2004 INTEGER,
    year_2005 INTEGER,
    year_2006 INTEGER,
    year_2007 INTEGER,
    year_2008 INTEGER,
    year_2009 INTEGER,
    year_2010 INTEGER,
    year_2011 INTEGER,
    year_2012 INTEGER,
    year_2013 INTEGER,
    year_2014 INTEGER,
    year_2015 INTEGER,
    year_2016 INTEGER,
    year_2017 INTEGER,
    year_2018 INTEGER,
    year_2019 INTEGER,
    year_2020 INTEGER,
    year_2021 INTEGER,

    -- Analysis fields
    population_change_2011_2021 INTEGER,       -- Population change between 2011-2021
    growth_rate_2011_2021 DECIMAL(6,2),       -- Growth rate percentage for 2011-2021
    area_km2 DECIMAL(10,2),                    -- Area in square kilometers
    population_density_2021 DECIMAL(10,2),    -- Population density in 2021 (persons/km2)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient searching and filtering
CREATE INDEX IF NOT EXISTS idx_melbourne_sa2_name ON melbourne_population_history(sa2_name);
CREATE INDEX IF NOT EXISTS idx_melbourne_sa3_name ON melbourne_population_history(sa3_name);
CREATE INDEX IF NOT EXISTS idx_melbourne_sa2_code ON melbourne_population_history(sa2_code);

-- Add comments
COMMENT ON TABLE melbourne_population_history IS 'Historical population data for Melbourne areas by SA2 regions (2001-2021)';
COMMENT ON COLUMN melbourne_population_history.sa2_code IS 'Statistical Area Level 2 identifier code';
COMMENT ON COLUMN melbourne_population_history.sa2_name IS 'Name of the statistical area (e.g., Carlton, Docklands)';
COMMENT ON COLUMN melbourne_population_history.population_change_2011_2021 IS 'Net population change from 2011 to 2021';
COMMENT ON COLUMN melbourne_population_history.area_km2 IS 'Geographic area in square kilometers';

-- ================================================================
-- TABLE 3: Parking Bays Information
-- Purpose: Store static information about each parking bay
-- ================================================================
CREATE TABLE IF NOT EXISTS parking_bays (
    kerbside_id INTEGER PRIMARY KEY,           -- Unique parking bay identifier
    road_segment_id INTEGER,                   -- Road segment identifier
    road_segment_description TEXT,             -- Description like "King Street between..."
    latitude DECIMAL(10,7) NOT NULL,           -- Latitude coordinate
    longitude DECIMAL(10,7) NOT NULL,          -- Longitude coordinate
    last_updated DATE,                         -- Last update date from source
    location_string TEXT,                      -- Location coordinate as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for geographic and road segment queries
CREATE INDEX IF NOT EXISTS idx_parking_bays_location ON parking_bays(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_parking_bays_road_segment ON parking_bays(road_segment_id);
CREATE INDEX IF NOT EXISTS idx_parking_bays_road_desc ON parking_bays USING gin(to_tsvector('english', road_segment_description));

-- Add comments
COMMENT ON TABLE parking_bays IS 'Static information about parking bays including location and road details';
COMMENT ON COLUMN parking_bays.kerbside_id IS 'Unique identifier for each parking bay';
COMMENT ON COLUMN parking_bays.road_segment_description IS 'Human-readable description of the road segment';
COMMENT ON COLUMN parking_bays.latitude IS 'Geographic latitude coordinate';
COMMENT ON COLUMN parking_bays.longitude IS 'Geographic longitude coordinate';

-- ================================================================
-- TABLE 4: Current Parking Status
-- Purpose: Store the most recent status of each parking bay
-- ================================================================
CREATE TABLE IF NOT EXISTS parking_status_current (
    kerbside_id INTEGER PRIMARY KEY REFERENCES parking_bays(kerbside_id) ON DELETE CASCADE,
    zone_number INTEGER,                       -- Parking zone number
    status_description VARCHAR(20) NOT NULL CHECK (status_description IN ('Present', 'Unoccupied')),
    last_updated TIMESTAMP,                    -- When the data was last updated
    status_timestamp TIMESTAMP,                -- When the status was recorded
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for status queries
CREATE INDEX IF NOT EXISTS idx_current_status_zone ON parking_status_current(zone_number);
CREATE INDEX IF NOT EXISTS idx_current_status_desc ON parking_status_current(status_description);
CREATE INDEX IF NOT EXISTS idx_current_status_timestamp ON parking_status_current(status_timestamp DESC);

-- Add comments
COMMENT ON TABLE parking_status_current IS 'Current parking status for real-time display and queries';
COMMENT ON COLUMN parking_status_current.status_description IS 'Current occupancy status: Present (occupied) or Unoccupied (vacant)';
COMMENT ON COLUMN parking_status_current.zone_number IS 'Parking zone identifier';
COMMENT ON COLUMN parking_status_current.status_timestamp IS 'Timestamp when the status was recorded';

-- ================================================================
-- TABLE 5: Parking Status History
-- Purpose: Store historical parking status data for trend analysis
-- ================================================================
CREATE TABLE IF NOT EXISTS parking_status_history (
    id SERIAL PRIMARY KEY,
    kerbside_id INTEGER NOT NULL REFERENCES parking_bays(kerbside_id) ON DELETE CASCADE,
    zone_number INTEGER,                       -- Parking zone number
    status_description VARCHAR(20) NOT NULL CHECK (status_description IN ('Present', 'Unoccupied')),
    status_timestamp TIMESTAMP NOT NULL,       -- When the status was recorded
    last_updated TIMESTAMP,                    -- When the data was last updated
    batch_id UUID DEFAULT uuid_generate_v4(), -- Batch identifier for data collection
    api_call_sequence INTEGER,                 -- Sequence number within API batch
    data_collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraint to automatically delete old data (1 month retention)
    CONSTRAINT check_data_retention CHECK (data_collected_at > CURRENT_TIMESTAMP - INTERVAL '35 days')
);

-- Create indexes for efficient time-based and analytical queries
CREATE INDEX IF NOT EXISTS idx_history_kerbside_time ON parking_status_history(kerbside_id, status_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_history_status_timestamp ON parking_status_history(status_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_history_zone_time ON parking_status_history(zone_number, status_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_history_batch_id ON parking_status_history(batch_id);
CREATE INDEX IF NOT EXISTS idx_history_collection_time ON parking_status_history(data_collected_at DESC);

-- Add comments
COMMENT ON TABLE parking_status_history IS 'Historical parking status data for trend analysis and statistics';
COMMENT ON COLUMN parking_status_history.batch_id IS 'UUID identifying the data collection batch';
COMMENT ON COLUMN parking_status_history.api_call_sequence IS 'Sequence number within the API call batch';
COMMENT ON COLUMN parking_status_history.data_collected_at IS 'Timestamp when data was collected from API';

-- ================================================================
-- TABLE 6: Hourly Parking Statistics
-- Purpose: Pre-calculated hourly statistics for performance
-- ================================================================
CREATE TABLE IF NOT EXISTS parking_hourly_stats (
    id SERIAL PRIMARY KEY,
    stat_hour TIMESTAMP NOT NULL,              -- Hour being analyzed (truncated to hour)
    zone_number INTEGER,                       -- Parking zone number
    kerbside_id INTEGER REFERENCES parking_bays(kerbside_id) ON DELETE CASCADE,
    total_records INTEGER DEFAULT 0,           -- Total status records in this hour
    occupied_minutes INTEGER DEFAULT 0,        -- Minutes marked as occupied
    vacant_minutes INTEGER DEFAULT 0,          -- Minutes marked as vacant
    occupancy_rate DECIMAL(5,2),              -- Occupancy rate as percentage
    status_changes INTEGER DEFAULT 0,          -- Number of status changes in the hour
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique stats per hour per parking bay
    UNIQUE(stat_hour, kerbside_id),

    -- Automatic data retention (1 month)
    CONSTRAINT check_stats_retention CHECK (stat_hour > CURRENT_TIMESTAMP - INTERVAL '35 days')
);

-- Create indexes for statistical queries
CREATE INDEX IF NOT EXISTS idx_hourly_stats_hour ON parking_hourly_stats(stat_hour DESC);
CREATE INDEX IF NOT EXISTS idx_hourly_stats_zone_hour ON parking_hourly_stats(zone_number, stat_hour DESC);
CREATE INDEX IF NOT EXISTS idx_hourly_stats_occupancy ON parking_hourly_stats(stat_hour DESC, occupancy_rate DESC);
CREATE INDEX IF NOT EXISTS idx_hourly_stats_kerbside ON parking_hourly_stats(kerbside_id, stat_hour DESC);

-- Add comments
COMMENT ON TABLE parking_hourly_stats IS 'Pre-calculated hourly parking statistics for performance optimization';
COMMENT ON COLUMN parking_hourly_stats.stat_hour IS 'Hour being analyzed (truncated to hour boundary)';
COMMENT ON COLUMN parking_hourly_stats.occupancy_rate IS 'Percentage of time the bay was occupied during the hour';
COMMENT ON COLUMN parking_hourly_stats.status_changes IS 'Number of times status changed during the hour';

-- ================================================================
-- TABLE 7: API Collection Log
-- Purpose: Log data collection activities and monitor system health
-- ================================================================
CREATE TABLE IF NOT EXISTS api_collection_log (
    id SERIAL PRIMARY KEY,
    collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_fetched INTEGER,                   -- Number of records successfully fetched
    api_call_count INTEGER,                    -- Number of API calls made
    total_parking_bays INTEGER,                -- Total parking bays processed
    success_status BOOLEAN DEFAULT TRUE,       -- Whether collection was successful
    error_message TEXT,                        -- Error message if collection failed
    processing_time_seconds DECIMAL(8,2),     -- Time taken for collection process
    batch_id UUID,                            -- Reference to the data batch

    -- Automatic log retention (2 months)
    CONSTRAINT check_log_retention CHECK (collection_time > CURRENT_TIMESTAMP - INTERVAL '60 days')
);

-- Create indexes for monitoring and reporting
CREATE INDEX IF NOT EXISTS idx_collection_log_time ON api_collection_log(collection_time DESC);
CREATE INDEX IF NOT EXISTS idx_collection_log_status ON api_collection_log(success_status, collection_time DESC);
CREATE INDEX IF NOT EXISTS idx_collection_log_batch ON api_collection_log(batch_id);

-- Add comments
COMMENT ON TABLE api_collection_log IS 'Log of data collection activities for monitoring and debugging';
COMMENT ON COLUMN api_collection_log.records_fetched IS 'Number of parking records successfully retrieved';
COMMENT ON COLUMN api_collection_log.api_call_count IS 'Number of API calls made during collection';
COMMENT ON COLUMN api_collection_log.processing_time_seconds IS 'Total time spent on data collection and processing';

-- ================================================================
-- CREATE VIEWS FOR COMMON QUERIES
-- ================================================================

-- View: Current parking status with location details
CREATE OR REPLACE VIEW parking_status_with_location AS
SELECT
    psc.kerbside_id,
    psc.zone_number,
    psc.status_description,
    psc.status_timestamp,
    psc.last_updated,
    pb.road_segment_description,
    pb.latitude,
    pb.longitude,
    pb.location_string
FROM parking_status_current psc
JOIN parking_bays pb ON psc.kerbside_id = pb.kerbside_id;

COMMENT ON VIEW parking_status_with_location IS 'Current parking status combined with location information for map display';

-- View: Zone statistics summary
CREATE OR REPLACE VIEW zone_statistics AS
SELECT
    zone_number,
    COUNT(*) as total_bays,
    SUM(CASE WHEN status_description = 'Present' THEN 1 ELSE 0 END) as occupied_bays,
    SUM(CASE WHEN status_description = 'Unoccupied' THEN 1 ELSE 0 END) as vacant_bays,
    ROUND(
        (SUM(CASE WHEN status_description = 'Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2
    ) as occupancy_rate
FROM parking_status_current
WHERE zone_number IS NOT NULL
GROUP BY zone_number
ORDER BY zone_number;

COMMENT ON VIEW zone_statistics IS 'Summary statistics for each parking zone';

-- ================================================================
-- FUNCTIONS AND TRIGGERS
-- ================================================================

-- Function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_victoria_population_growth_updated_at
    BEFORE UPDATE ON victoria_population_growth
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_melbourne_population_history_updated_at
    BEFORE UPDATE ON melbourne_population_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parking_bays_updated_at
    BEFORE UPDATE ON parking_bays
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parking_status_current_updated_at
    BEFORE UPDATE ON parking_status_current
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up old data automatically
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Clean up parking status history older than 30 days
    DELETE FROM parking_status_history
    WHERE data_collected_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

    -- Clean up hourly stats older than 30 days
    DELETE FROM parking_hourly_stats
    WHERE stat_hour < CURRENT_TIMESTAMP - INTERVAL '30 days';

    -- Clean up API logs older than 60 days
    DELETE FROM api_collection_log
    WHERE collection_time < CURRENT_TIMESTAMP - INTERVAL '60 days';

    -- Log the cleanup operation
    INSERT INTO api_collection_log (records_fetched, api_call_count, error_message)
    VALUES (0, 0, 'Automated data cleanup completed');

END;
$$ LANGUAGE plpgsql;

-- Comment on cleanup function
COMMENT ON FUNCTION cleanup_old_data() IS 'Automatically removes old data based on retention policies';

-- ================================================================
-- INITIAL DATA VALIDATION
-- ================================================================

-- Add check constraints for data quality
ALTER TABLE parking_status_current
ADD CONSTRAINT check_status_timestamp_not_future
CHECK (status_timestamp <= CURRENT_TIMESTAMP + INTERVAL '1 hour');

ALTER TABLE parking_status_history
ADD CONSTRAINT check_status_timestamp_not_future_history
CHECK (status_timestamp <= CURRENT_TIMESTAMP + INTERVAL '1 hour');

-- Add check for coordinate validity (Melbourne area roughly)
ALTER TABLE parking_bays
ADD CONSTRAINT check_latitude_melbourne
CHECK (latitude BETWEEN -38.5 AND -37.0);

ALTER TABLE parking_bays
ADD CONSTRAINT check_longitude_melbourne
CHECK (longitude BETWEEN 144.0 AND 145.5);

-- ================================================================
-- GRANT PERMISSIONS (uncomment and modify as needed)
-- ================================================================

-- Create application user (run as superuser)
-- CREATE USER melbourne_parking WITH PASSWORD 'zjy0312!';

-- Grant necessary permissions
-- GRANT CONNECT ON DATABASE melbourne_parking_system TO melbourne_parking;
-- GRANT USAGE ON SCHEMA public TO melbourne_parking;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO melbourne_parking;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO melbourne_parking;

-- ================================================================
-- END OF DATABASE SCHEMA
-- ================================================================

-- Display completion message
DO $$
BEGIN
    RAISE NOTICE 'Melbourne Parking System database schema created successfully!';
    RAISE NOTICE 'Tables created: 7';
    RAISE NOTICE 'Views created: 2';
    RAISE NOTICE 'Functions created: 2';
    RAISE NOTICE 'Ready for data import and application connection.';
END $$;
