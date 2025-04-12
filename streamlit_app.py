
# streamlit_app.py

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
import base64

st.set_page_config(page_title="Saudi AC Project Dashboard", layout="wide")
st.title("📊 Saudi AC Installation Dashboard")

# ---- Load Data ----
@st.cache_data
def load_data():
    project_url = "https://docs.google.com/spreadsheets/d/1pZBg_lf8HakI6o2W1v8u1lUN2FGJn1Jc/export?format=csv"
    form_url = "https://docs.google.com/spreadsheets/d/1IeZVNb01-AMRuXjj9SZQyELTVr6iw5Vq4JsiN7PdZEs/export?format=csv"

    df_sites = pd.read_csv(project_url)
    df_installed = pd.read_csv(form_url)

    df_sites['Site ID'] = df_sites['Site ID'].astype(str).str.strip().str.upper()
    df_installed['Site ID'] = df_installed['Site ID'].astype(str).str.strip().str.upper()

    installed_map = df_installed.set_index('Site ID')['Installation Date'].to_dict()
    df_sites['Status'] = df_sites['Site ID'].apply(lambda x: 'Installed' if x in installed_map else 'Open')
    df_sites['Installation Date'] = df_sites['Site ID'].apply(lambda x: installed_map.get(x, ''))

    df_sites['Latitude'] = pd.to_numeric(df_sites['Latitude'], errors='coerce')
    df_sites['Longitude'] = pd.to_numeric(df_sites['Longitude'], errors='coerce')
    df_sites.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    return df_sites

df = load_data()

# ---- KPIs ----
total_sites = len(df)
installed_count = (df['Status'] == 'Installed').sum()
open_count = (df['Status'] == 'Open').sum()
progress = round((installed_count / total_sites) * 100, 2) if total_sites else 0

# Daily rate calculation
installed_dates = pd.to_datetime(df[df['Status'] == 'Installed']['Installation Date'], errors='coerce')
if not installed_dates.empty:
    days_span = (installed_dates.max() - installed_dates.min()).days or 1
    daily_rate = round(installed_count / days_span, 2)
else:
    daily_rate = 0

# ---- Layout ----
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Sites", total_sites)
kpi2.metric("Installed", installed_count)
kpi3.metric("Open", open_count)
kpi4.metric("Progress %", f"{progress}%")
kpi5.metric("Daily Rate", f"{daily_rate} sites/day")

st.markdown("---")

# ---- Map ----
st.subheader("📍 Site Installation Map")
m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)
for _, row in df.iterrows():
    color = 'green' if row['Status'] == 'Installed' else 'red'
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=6,
        popup=f"Site ID: {row['Site ID']}<br>Status: {row['Status']}<br>Installation Date: {row['Installation Date']}",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8
    ).add_to(m)
folium_static(m)

# ---- Charts ----
st.subheader("📊 Installation Status Overview")
status_counts = df['Status'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', colors=['green', 'red'])
ax1.axis('equal')
st.pyplot(fig1)

st.subheader("📈 Daily Installation Trend")
trend_data = df[df['Status'] == 'Installed'].copy()
trend_data['Installation Date'] = pd.to_datetime(trend_data['Installation Date'], errors='coerce')
daily_trend = trend_data.groupby(trend_data['Installation Date'].dt.date).size()
fig2, ax2 = plt.subplots()
daily_trend.plot(kind='line', ax=ax2)
ax2.set_ylabel("Sites Installed")
ax2.set_xlabel("Date")
st.pyplot(fig2)

# ---- Download Buttons ----
st.markdown("### 📥 Download Data")
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False)
excel_data = excel_buffer.getvalue()

st.download_button("⬇️ Download Excel", data=excel_data, file_name="installation_status.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

df_sample = df[['Site ID', 'Status', 'Installation Date']].copy()
df_sample_html = df_sample.to_html(index=False)
pdf_html = f"""<html><head><style>table {{border-collapse: collapse; width: 100%;}} td, th {{border: 1px solid #ccc; padding: 8px;}}</style></head><body>{df_sample_html}</body></html>"""
b64_pdf = base64.b64encode(pdf_html.encode()).decode()
pdf_link = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="installation_report.html">⬇️ Download PDF Report</a>'
st.markdown(pdf_link, unsafe_allow_html=True)

st.markdown("---")
st.caption("Dashboard auto-updates daily from Google Sheets – English only interface.")
