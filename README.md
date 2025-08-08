# Melbourne Parking Website

A comprehensive web application for visualizing and analyzing parking data in Melbourne City. This system provides real-time parking information, interactive heatmaps, and detailed analytics to help drivers find available parking spots efficiently.

## 🌟 Features

### Core Functionality
- **Real-time Parking Status**: Live parking bay availability across Melbourne CBD
- **Interactive Heatmap**: Visual density maps showing parking availability hotspots
- **Street-level Analysis**: Detailed parking information organized by street
- **Advanced Analytics**: Population growth trends and historical parking data analysis
- **Responsive Design**: Optimized for desktop and mobile devices

### Key Components
- **Smart Search**: Find parking by street name with autocomplete suggestions
- **Visual Analytics**: Charts and graphs for data analysis using Chart.js
- **Map Integration**: Interactive maps powered by Leaflet.js with custom markers
- **Statistical Dashboard**: Overview statistics and trends

## 🛠 Technology Stack

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Vite**: Fast build tool and development server
- **Leaflet.js**: Interactive mapping library
- **Chart.js**: Data visualization and charting
- **Axios**: HTTP client for API requests

### Backend
- **Flask**: Python web framework
- **PostgreSQL**: Relational database for data storage
- **SQLAlchemy**: Database ORM
- **Flask-CORS**: Cross-Origin Resource Sharing support

### Data Sources
- On-street parking bay sensors data
- Melbourne parking bay locations
- Australian Bureau of Statistics population data
- Melbourne city demographic information

## 📁 Project Structure

```
melbourne-parking-website/
├── frontend/                 # Vue.js frontend application
│   ├── src/
│   │   ├── components/      # Vue components
│   │   │   ├── ParkingMap.vue
│   │   │   ├── SearchPanel.vue
│   │   │   ├── AnalyticsPanel.vue
│   │   │   └── StreetsPanel.vue
│   │   ├── services/        # API service layers
│   │   └── assets/          # Static assets
│   ├── package.json
│   └── vite.config.js
├── backend/                  # Flask backend application
│   ├── api/                 # API route handlers
│   │   ├── parking_routes.py
│   │   ├── analytics_routes.py
│   │   └── statistics_routes.py
│   ├── models/              # Database models
│   ├── database/            # Database setup and migrations
│   │   ├── init_database.sql
│   │   └── seeds/
│   └── website.py           # Flask application factory
├── config/                  # Configuration files
├── docs/                    # Documentation
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- PostgreSQL 12+
- Git

### Database Setup

1. **Install PostgreSQL** (if not already installed):
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

2. **Create Database and User**:
```bash
psql -U postgres
CREATE DATABASE melbourne_parking_system;
CREATE USER melbourne_parking WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE melbourne_parking_system TO melbourne_parking;
\q
```

3. **Initialize Database Schema**:
```bash
cd backend/database
psql -d melbourne_parking_system -f init_database.sql
```

4. **Import CSV Data**:
```bash
cd backend/database/seeds
python import_csv_data.py
```

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install flask flask-cors sqlalchemy psycopg2-binary
```

4. **Configure database connection**:
   - Update the database URI in `website.py` with your credentials
   - Default: `postgresql://melbourne_parking:password@localhost:5432/melbourne_parking_system`

5. **Run the backend server**:
```bash
python run.py
```
The Flask API will be available at `http://localhost:5002`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```
The frontend will be available at `http://localhost:3000`

## 🎯 Usage

### Getting Started
1. Ensure both backend and frontend servers are running
2. Open your browser to `http://localhost:3000`
3. The application will load with the default parking view

### Main Features

#### 1. **Parking Mode**
- View individual parking spots as pins on the map
- Search for specific streets using the search bar
- Click on pins to see detailed parking bay information
- Available spots are shown in green, occupied spots in red

#### 2. **Heatmap Mode**
- Visualize parking density across Melbourne CBD
- Hot zones (red/orange) indicate high parking availability
- Cold zones (blue) indicate low availability or high occupancy
- Select specific streets to focus the heatmap on particular areas

#### 3. **Analytics Mode**
- **Population Analysis**: View Victoria's population growth trends (2016-2021)
- **Historical Trends**: Analyze parking usage patterns over time
- Interactive charts with detailed statistics and insights

#### 4. **Street Statistics**
- Browse parking data organized by street
- View occupancy rates and availability statistics
- Click any street to filter map data to that specific location
- Use "All Streets" to reset and view citywide data

### Navigation Tips
- Use the three mode buttons to switch between Parking, Heatmap, and Analytics views
- The Street Statistics panel on the right works with all modes
- Click anywhere on the map in Parking mode to find nearby parking
- In Heatmap mode, clicking areas will show specific parking spot details

## 🔧 API Endpoints

### Parking Data
- `GET /api/parking/current-status` - Get current parking bay status
- `GET /api/parking/streets` - List all streets with parking data
- `GET /api/parking/nearby` - Find parking near coordinates

### Analytics
- `GET /api/analytics/population-data` - Population growth statistics
- `GET /api/analytics/historical-trends` - Historical parking trends

### Statistics  
- `GET /api/statistics/overview` - General parking statistics

## 🗂 Data Sources

The application uses several CSV data files:
- **on-street-parking-bay-sensors.csv**: Real-time parking sensor data
- **on-street-parking-bays.csv**: Static parking bay location information  
- **Australian Bureau of Statistics (1).csv**: Population growth data
- **only_melbourne_city_1_without_none.csv**: Melbourne city demographic data

## 🚀 Deployment

### Production Build

**Frontend**:
```bash
cd frontend
npm run build
```

**Backend**:
Update database credentials and set Flask environment:
```bash
export FLASK_ENV=production
python run.py
```

### Deployment Options
- **Local Server**: Run on local machine or server
- **Cloud Platforms**: Deploy to Heroku, AWS, Google Cloud, etc.
- **Containerization**: Docker support can be added for easier deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is developed for educational and research purposes. Please ensure you have appropriate permissions for the data sources used.

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**:
- Verify PostgreSQL is running
- Check database credentials in `website.py`
- Ensure database and user exist

**Frontend Not Loading**:
- Check if backend API is running on port 5002
- Verify CORS settings in Flask configuration
- Check browser console for JavaScript errors

**Map Not Displaying**:
- Ensure Leaflet.js dependencies are properly installed
- Check for console errors related to map tiles
- Verify parking data is being loaded from API

**Charts Not Rendering**:
- Confirm Chart.js is properly installed
- Check for data loading issues in analytics service
- Verify chart canvas elements are present in DOM

## 📞 Support

For issues, questions, or contributions, please:
- Check existing documentation
- Review troubleshooting section
- Open an issue in the project repository

---

**Built with ❤️ for Melbourne drivers**
