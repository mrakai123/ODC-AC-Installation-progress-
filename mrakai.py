
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>ODC-AC Installation Progress Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Prepared by: Mohammed Alfadhel</p>", unsafe_allow_html=True)

# Load data
sheet_url = 'https://docs.google.com/spreadsheets/d/1pZBg_lf8HakI6o2W1v8u1lUN2FGJn1Jc/export?format=csv&id=1pZBg_lf8HakI6o2W1v8u1lUN2FGJn1Jc&gid=622694975'
df = pd.read_csv(sheet_url)

# Convert dates
df['Installation Date'] = pd.to_datetime(df['Installation Date'], errors='coerce')

# Filters
regions = df['Region'].dropna().unique().tolist()
selected_region = st.selectbox("Select Region", ["All"] + regions)
date_range = st.date_input("Select Date Range", [df['Installation Date'].min(), df['Installation Date'].max()])

if selected_region != "All":
    df = df[df["Region"] == selected_region]

df = df[(df["Installation Date"] >= pd.to_datetime(date_range[0])) & (df["Installation Date"] <= pd.to_datetime(date_range[1]))]

# Map logic
m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)

for i, row in df.iterrows():
    color = "green" if pd.notnull(row["Installation Date"]) else "red"
    popup_info = f"Site ID: {row['Site ID']}<br>Region: {row['Region']}<br>Status: {'Installed' if color == 'green' else 'Open'}<br>Date: {row['Installation Date'].date() if pd.notnull(row['Installation Date']) else 'N/A'}"
    folium.CircleMarker(location=[row["Latitude"], row["Longitude"]],
                        radius=6,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        popup=popup_info).add_to(m)

st_folium(m, width=1200, height=500)

# KPIs
total_sites = len(df)
installed_sites = df['Installation Date'].notnull().sum()
progress = round((installed_sites / total_sites) * 100, 1) if total_sites else 0
daily_rate = installed_sites / max((df['Installation Date'].max() - df['Installation Date'].min()).days, 1)

st.markdown(f"### 📊 Total Sites: {total_sites} | ✅ Installed: {installed_sites} | 📈 Progress: {progress}% | 📅 Daily Rate: {daily_rate:.2f}/day")
