import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# 设置页面配置
st.set_page_config(
    page_title="Melbourne Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加自定义CSS
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
    """加载示例数据，模拟停车位数据"""
    # 生成模拟数据
    np.random.seed(42)
    n_bays = 5000

    # 创建停车位数据
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
    """生成时间序列数据用于图表展示"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')

    # 模拟每日占用率数据
    occupancy_rates = []
    for i, date in enumerate(dates):
        # 模拟季节性和周期性变化
        base_rate = 0.65
        seasonal = 0.1 * np.sin(2 * np.pi * i / 365)  # 年度季节性
        weekly = 0.15 * np.sin(2 * np.pi * (i % 7) / 7)  # 周循环
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
    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🅿️ Melbourne Parking System</h1>
        <p>Real-time parking data for Melbourne's CBD — less time driving, more time living</p>
    </div>
    """, unsafe_allow_html=True)

    # 加载数据
    parking_df = load_sample_data()
    time_series_df = generate_time_series_data()

    # 边栏
    st.sidebar.header("📊 Dashboard Controls")

    # 日期选择器
    selected_date = st.sidebar.date_input(
        "选择日期",
        value=datetime.now().date(),
        min_value=datetime(2024, 1, 1).date(),
        max_value=datetime.now().date()
    )

    # 区域选择
    selected_zones = st.sidebar.multiselect(
        "选择停车区域类型",
        options=['1P', '2P', '4P', 'Unrestricted'],
        default=['1P', '2P', '4P', 'Unrestricted']
    )

    # 街道选择
    selected_streets = st.sidebar.multiselect(
        "选择街道",
        options=parking_df['street_name'].unique(),
        default=parking_df['street_name'].unique()[:3]
    )

    # 筛选数据
    filtered_df = parking_df[
        (parking_df['zone_number'].isin(selected_zones)) &
        (parking_df['street_name'].isin(selected_streets))
    ]

    # 主要指标
    col1, col2, col3, col4 = st.columns(4)

    total_bays = len(filtered_df)
    occupied = len(filtered_df[filtered_df['status'] == 'Occupied'])
    available = len(filtered_df[filtered_df['status'] == 'Unoccupied'])
    out_of_service = len(filtered_df[filtered_df['status'] == 'Out of Service'])
    occupancy_rate = (occupied / total_bays * 100) if total_bays > 0 else 0

    with col1:
        st.metric(
            label="🅿️ 总停车位",
            value=f"{total_bays:,}",
            delta=None
        )

    with col2:
        st.metric(
            label="✅ 可用停车位",
            value=f"{available:,}",
            delta=f"{available/total_bays*100:.1f}%" if total_bays > 0 else "0%"
        )

    with col3:
        st.metric(
            label="🚗 占用停车位",
            value=f"{occupied:,}",
            delta=f"{occupancy_rate:.1f}%" if total_bays > 0 else "0%"
        )

    with col4:
        st.metric(
            label="⚠️ 停用停车位",
            value=f"{out_of_service:,}",
            delta=f"{out_of_service/total_bays*100:.1f}%" if total_bays > 0 else "0%"
        )

    # 图表区域
    st.markdown("---")

    # 第一行图表
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 历史占用率趋势")
        fig_line = px.line(
            time_series_df,
            x='date',
            y='occupancy_rate',
            title="停车位占用率变化趋势",
            labels={'occupancy_rate': '占用率', 'date': '日期'}
        )
        fig_line.update_traces(line_color='#3498db')
        fig_line.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("🍕 当前停车状态分布")
        status_counts = filtered_df['status'].value_counts()
        colors = ['#e74c3c', '#27ae60', '#f39c12']

        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="停车位状态分布",
            color_discrete_sequence=colors
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # 第二行图表
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 各街道停车位分布")
        street_counts = filtered_df.groupby('street_name').size().reset_index(name='count')
        fig_bar = px.bar(
            street_counts,
            x='street_name',
            y='count',
            title="各街道停车位数量",
            labels={'count': '停车位数量', 'street_name': '街道名称'},
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
        st.subheader("⏰ 停车区域类型分布")
        zone_counts = filtered_df['zone_number'].value_counts()
        fig_bar2 = px.bar(
            x=zone_counts.index,
            y=zone_counts.values,
            title="停车时长限制分布",
            labels={'x': '停车区域类型', 'y': '停车位数量'},
            color=zone_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_bar2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_bar2, use_container_width=True)

    # 地图展示
    st.markdown("---")
    st.subheader("🗺️ 停车位地图分布")

    # 创建地图数据
    map_data = filtered_df.sample(min(500, len(filtered_df)))  # 最多显示500个点，避免地图过于拥挤

    # 添加颜色映射
    color_map = {'Occupied': '#e74c3c', 'Unoccupied': '#27ae60', 'Out of Service': '#f39c12'}
    map_data['color'] = map_data['status'].map(color_map)

    fig_map = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color="status",
        size_max=10,
        zoom=13,
        title="Melbourne CBD 停车位分布",
        color_discrete_map=color_map,
        hover_data={'street_name': True, 'zone_number': True}
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # 数据表格
    st.markdown("---")
    st.subheader("📋 详细数据")

    # 添加搜索功能
    search_term = st.text_input("🔍 搜索停车位 (输入街道名或停车位ID)")

    if search_term:
        display_df = filtered_df[
            (filtered_df['street_name'].str.contains(search_term, case=False)) |
            (filtered_df['kerbside_id'].str.contains(search_term, case=False))
        ]
    else:
        display_df = filtered_df.head(100)  # 只显示前100条记录

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "kerbside_id": "停车位ID",
            "latitude": "纬度",
            "longitude": "经度",
            "status": "状态",
            "zone_number": "区域类型",
            "street_name": "街道名称"
        }
    )

    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🅿️ Melbourne Parking System | Real-time data for smarter parking</p>
        <p>📊 Data updated every 10 minutes | 🚀 Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
