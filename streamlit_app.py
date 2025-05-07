# streamlit_app.py

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from datetime import datetime

# AQI 색상 매핑 (카테고리 기준)
category_colors = {
    "Good": "#00E400", "Moderate": "#FFFF00",
    "Unhealthy for Sensitive Groups": "#FF7E00",
    "Unhealthy": "#FF0000", "Very Unhealthy": "#8F3F97",
    "Hazardous": "#7E0023", "Unknown": "gray"
}

# --- 데이터 로드 ---
@st.cache_data
def load_data():
    df = pd.read_csv("fresno_pm25_hourly_with_aqi_and_category.csv")
    df["datetime"] = pd.to_datetime(df["date_local"] + " " + df["time_local"], errors="coerce")
    return df.dropna(subset=["datetime", "latitude", "longitude"])

df = load_data()

# --- UI ---
st.set_page_config(layout="wide")
st.title("📍 Fresno PM2.5 AQI - Time Slider Map")
st.caption("Explore AQI by hour from 1999 to 2025")

# 날짜 슬라이더
min_date = df["datetime"].dt.date.min()
max_date = df["datetime"].dt.date.max()
selected_date = st.slider("📅 Date", min_value=min_date, max_value=max_date, value=datetime(2017, 6, 15).date())

# 시간 슬라이더
selected_hour = st.slider("🕒 Hour", 0, 23, 14)

# 필터링
filtered = df[
    (df["datetime"].dt.date == selected_date) &
    (df["datetime"].dt.hour == selected_hour)
]

# 지도 시각화
st.markdown(f"🧭 {len(filtered)} monitors found for {selected_date} @ {selected_hour}:00")
m = folium.Map(location=[filtered["latitude"].mean(), filtered["longitude"].mean()],
               zoom_start=10, tiles="CartoDB dark_matter")
cluster = MarkerCluster().add_to(m)

for _, row in filtered.iterrows():
    color = category_colors.get(row["aqi_category"], "gray")
    popup = f"Site: {row['site_number']}<br>AQI: {row['aqi']}<br>PM2.5: {row['sample_measurement']} µg/m³"
    folium.CircleMarker(
        location=(row["latitude"], row["longitude"]),
        radius=7,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=popup
    ).add_to(cluster)

folium_static(m)