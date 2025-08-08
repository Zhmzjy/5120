#!/bin/bash
# Melbourne Parking Website - Quick Setup Script
# Purpose: Execute all database setup steps in the correct order
# Created: August 8, 2025

echo "🚀 Melbourne Parking System - Complete Database Setup"
echo "====================================================="

# Check if we're in the correct directory
if [[ ! -f "init_database.sql" ]]; then
    echo "❌ Please run this script from the database directory"
    echo "   cd /Users/zhujunyi/5120/melbourne-parking-website/backend/database/"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Step 1: Install PostgreSQL
echo "Step 1: Installing PostgreSQL..."
echo "--------------------------------"
chmod +x install_postgresql.sh
./install_postgresql.sh

echo ""
echo "Step 2: Creating database schema..."
echo "-----------------------------------"
psql -U melbourne_parking -d melbourne_parking_system -f init_database.sql

echo ""
echo "Step 3: Installing Python dependencies..."
echo "-----------------------------------------"
pip3 install psycopg2-binary pandas

echo ""
echo "Step 4: Importing CSV data..."
echo "-----------------------------"
cd seeds
python3 import_csv_data.py
cd ..

echo ""
echo "Step 5: Testing database connection..."
echo "--------------------------------------"
python3 test_connection.py

echo ""
echo "🎉 Melbourne Parking System database setup completed!"
echo ""
echo "📋 What's been set up:"
echo "   ✅ PostgreSQL installed and configured"
echo "   ✅ Database 'melbourne_parking_system' created"
echo "   ✅ User 'melbourne_parking' with appropriate permissions"
echo "   ✅ All 7 tables created with indexes and constraints"
echo "   ✅ CSV data imported from all 4 files"
echo "   ✅ Database connection tested and verified"
echo ""
echo "🔗 Connection Details:"
echo "   Database: melbourne_parking_system"
echo "   User: melbourne_parking"
echo "   Password: zjy0312!"
echo "   URL: postgresql://melbourne_parking:zjy0312!@localhost:5432/melbourne_parking_system"
echo ""
echo "🎯 Next Steps:"
echo "   • Start developing the Flask backend API"
echo "   • Set up the Vue.js frontend"
echo "   • Configure API data collection scripts"
