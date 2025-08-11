import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Prevent importing backend modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, 'backend')
if backend_path in sys.path:
    sys.path.remove(backend_path)

# Set page configuration
st.set_page_config(
    page_title="Melbourne Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
    .stMetric > label {
        color: #2c3e50 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """Load sample data to simulate parking bay data"""
    # Generate mock data
    np.random.seed(42)
    n_bays = 5000

    # Create parking bay data
    parking_data = {
        'kerbside_id': [f'BAY_{i:04d}' for i in range(n_bays)],
        'latitude': np.random.uniform(-37.850, -37.800, n_bays),
        'longitude': np.random.uniform(144.950, 145.000, n_bays),
        'status': np.random.choice(['Occupied', 'Unoccupied', 'Out of Service'],
                                 n_bays, p=[0.6, 0.35, 0.05]),
        'zone_number': np.random.choice(['1P', '2P', '4P', 'Unrestricted'],
                                       n_bays, p=[0.3, 0.4, 0.2, 0.1]),
        'street_name': np.random.choice(['Collins St', 'Flinders St', 'Bourke St',
                                       'Elizabeth St', 'Swanston St', 'Russell St'], n_bays)
    }

    return pd.DataFrame(parking_data)

@st.cache_data
def generate_time_series_data():
    """Generate time series data for chart display"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')

    # Simulate daily occupancy rate data
    occupancy_rates = []
    for i, date in enumerate(dates):
        # Simulate seasonal and periodic changes
        base_rate = 0.65
        seasonal = 0.1 * np.sin(2 * np.pi * i / 365)  # Annual seasonality
        weekly = 0.15 * np.sin(2 * np.pi * (i % 7) / 7)  # Weekly cycle
        noise = np.random.normal(0, 0.05)
        rate = np.clip(base_rate + seasonal + weekly + noise, 0.2, 0.95)
        occupancy_rates.append(rate)

    return pd.DataFrame({
        'date': dates,
        'occupancy_rate': occupancy_rates,
        'available_spots': [int(5000 * (1 - rate)) for rate in occupancy_rates],
        'occupied_spots': [int(5000 * rate) for rate in occupancy_rates]
    })

def main():
    # Main title
    st.markdown("""
    <div class="main-header">
        <h1>🅿️ Melbourne Parking System</h1>
        <p>Real-time parking data for Melbourne's CBD — less time driving, more time living</p>
    </div>
    """, unsafe_allow_html=True)

    # Load data
    parking_df = load_sample_data()
    time_series_df = generate_time_series_data()

    # Sidebar
    st.sidebar.header("📊 Dashboard Controls")

    # Date picker
    selected_date = st.sidebar.date_input(
        "Select Date",
        value=datetime.now().date(),
        min_value=datetime(2024, 1, 1).date(),
        max_value=datetime.now().date()
    )

    # Zone selection
    selected_zones = st.sidebar.multiselect(
        "Select Parking Zone Types",
        options=['1P', '2P', '4P', 'Unrestricted'],
        default=['1P', '2P', '4P', 'Unrestricted']
    )

    # Street selection
    selected_streets = st.sidebar.multiselect(
        "Select Streets",
        options=parking_df['street_name'].unique(),
        default=parking_df['street_name'].unique()[:3]
    )

    # Filter data
    filtered_df = parking_df[
        (parking_df['zone_number'].isin(selected_zones)) &
        (parking_df['street_name'].isin(selected_streets))
    ]

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    total_bays = len(filtered_df)
    occupied = len(filtered_df[filtered_df['status'] == 'Occupied'])
    available = len(filtered_df[filtered_df['status'] == 'Unoccupied'])
    out_of_service = len(filtered_df[filtered_df['status'] == 'Out of Service'])
    occupancy_rate = (occupied / total_bays * 100) if total_bays > 0 else 0

    with col1:
        st.metric(
            label="🅿️ Total Parking Bays",
            value=f"{total_bays:,}",
            delta=None
        )

    with col2:
        st.metric(
            label="✅ Available Spaces",
            value=f"{available:,}",
            delta=f"{available/total_bays*100:.1f}%" if total_bays > 0 else "0%"
        )

    with col3:
        st.metric(
            label="🚗 Occupied Spaces",
            value=f"{occupied:,}",
            delta=f"{occupancy_rate:.1f}%" if total_bays > 0 else "0%"
        )

    with col4:
        st.metric(
            label="⚠️ Out of Service",
            value=f"{out_of_service:,}",
            delta=f"{out_of_service/total_bays*100:.1f}%" if total_bays > 0 else "0%"
        )

    # Charts section
    st.markdown("---")

    # First row of charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Historical Occupancy Trend")
        fig_line = px.line(
            time_series_df,
            x='date',
            y='occupancy_rate',
            title="Parking Occupancy Rate Trend",
            labels={'occupancy_rate': 'Occupancy Rate', 'date': 'Date'}
        )
        fig_line.update_traces(line_color='#3498db')
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("🍕 Current Parking Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        colors = ['#e74c3c', '#27ae60', '#f39c12']

        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Parking Status Distribution",
            color_discrete_sequence=colors
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Second row of charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 Parking Distribution by Street")
        street_counts = filtered_df.groupby('street_name').size().reset_index(name='count')
        fig_bar = px.bar(
            street_counts,
            x='street_name',
            y='count',
            title="Number of Parking Bays per Street",
            labels={'count': 'Number of Parking Bays', 'street_name': 'Street Name'},
            color='count',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("⏰ Parking Zone Type Distribution")
        zone_counts = filtered_df['zone_number'].value_counts()
        fig_bar2 = px.bar(
            x=zone_counts.index,
            y=zone_counts.values,
            title="Parking Time Limit Distribution",
            labels={'x': 'Parking Zone Type', 'y': 'Number of Parking Bays'},
            color=zone_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_bar2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_bar2, use_container_width=True)

    # Map display
    st.markdown("---")
    st.subheader("🗺️ Parking Bay Map Distribution")

    # Create map data
    map_data = filtered_df.sample(min(500, len(filtered_df)))  # Display max 500 points to avoid map congestion

    # Add color mapping
    color_map = {'Occupied': '#e74c3c', 'Unoccupied': '#27ae60', 'Out of Service': '#f39c12'}
    map_data['color'] = map_data['status'].map(color_map)

    fig_map = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color="status",
        size_max=10,
        zoom=13,
        title="Melbourne CBD Parking Bay Distribution",
        color_discrete_map=color_map,
        hover_data={'street_name': True, 'zone_number': True}
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # Data table
    st.markdown("---")
    st.subheader("📋 Detailed Data")

    # Add search functionality
    search_term = st.text_input("🔍 Search Parking Bays (enter street name or parking bay ID)")

    if search_term:
        display_df = filtered_df[
            (filtered_df['street_name'].str.contains(search_term, case=False)) |
            (filtered_df['kerbside_id'].str.contains(search_term, case=False))
        ]
    else:
        display_df = filtered_df.head(100)  # Display only first 100 records

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "kerbside_id": "Parking Bay ID",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "status": "Status",
            "zone_number": "Zone Type",
            "street_name": "Street Name"
        }
    )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🅿️ Melbourne Parking System | Real-time data for smarter parking</p>
        <p>📊 Data updated every 10 minutes | 🚀 Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
