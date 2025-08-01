
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
from io import BytesIO
import base64

st.set_page_config(page_title="ODC-AC Installation Dashboard", layout="wide")

# Show logos and title
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image("latis_logo.png", width=150)
with col3:
    st.image("wiconnect_logo.png", width=150)
with col2:
    st.markdown("<h1 style='text-align: center;'>ODC-AC Installation Progress Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Prepared by: Mohammed Alfadhel</p>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    project_url = "https://docs.google.com/spreadsheets/d/1pZBg_lf8HakI6o2W1v8u1lUN2FGJn1Jc/export?format=csv&gid=622694975"
    form_url = "hhttps://docs.google.com/spreadsheets/d/1GClN4fCfP8aAUoUO3ayHOdUP6eiuL1wmrSaxiR4CxK8/edit?gid=1294784605#gid=1294784605"

    df_sites = pd.read_csv(project_url)
    df_sites.columns = df_sites.columns.str.strip()

    if "Site ID" in df_sites.columns:
        df_sites["Site ID"] = df_sites["Site ID"].astype(str).str.strip().str.upper()
    else:
        st.error("❌ Column 'Site ID' not found in Project Sheet.")
        return pd.DataFrame()

    df_form = pd.read_csv(form_url)
    df_form.columns = df_form.columns.str.strip()
    df_form["Site ID"] = df_form["Site ID"].astype(str).str.strip().str.upper()

    df_installed = df_form[df_form["Site ID"].isin(df_sites["Site ID"])]

    df_sites = df_sites.merge(
        df_installed[["Site ID", "Latitude", "Longitude", "Timestamp"]],
        on="Site ID",
        how="left",
        suffixes=("", "_form"),
    )

    df_sites["Status"] = df_sites["Timestamp"].apply(lambda x: "Installed" if pd.notnull(x) else "Open")
    df_sites["Latitude"] = df_sites["Latitude"].fillna(df_sites["Latitude_form"])
    df_sites["Longitude"] = df_sites["Longitude"].fillna(df_sites["Longitude_form"])
    df_sites["Installation Date"] = df_sites["Timestamp"].fillna("")

    df_sites["Latitude"] = pd.to_numeric(df_sites["Latitude"], errors="coerce")
    df_sites["Longitude"] = pd.to_numeric(df_sites["Longitude"], errors="coerce")
    df_sites.dropna(subset=["Latitude", "Longitude"], inplace=True)

    return df_sites

df = load_data()

if df.empty:
    st.warning("⚠️ No data loaded. Please check the Google Sheets links.")
    st.stop()

total_sites = len(df)
installed_count = (df["Status"] == "Installed").sum()
open_count = (df["Status"] == "Open").sum()
progress = round((installed_count / total_sites) * 100, 2) if total_sites else 0

installed_dates = pd.to_datetime(df[df["Status"] == "Installed"]["Installation Date"], errors="coerce")
days_span = (installed_dates.max() - installed_dates.min()).days or 1 if not installed_dates.empty else 0
daily_rate = round(installed_count / days_span, 2) if days_span else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Sites", total_sites)
kpi2.metric("Installed", installed_count)
kpi3.metric("Open", open_count)
kpi4.metric("Progress %", f"{progress}%")
kpi5.metric("Daily Rate", f"{daily_rate} sites/day")

st.markdown("---")

st.subheader("📍 Site Installation Map")
m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)
for _, row in df.iterrows():
    color = "green" if row["Status"] == "Installed" else "red"
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=6,
        popup=f"Site ID: {row['Site ID']}<br>Status: {row['Status']}<br>Installation Date: {row['Installation Date']}",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
    ).add_to(m)
folium_static(m)

st.subheader("📊 Installation Status Distribution")
fig1, ax1 = plt.subplots()
df["Status"].value_counts().plot.pie(autopct="%1.1f%%", colors=["green", "red"], ax=ax1)
ax1.set_ylabel("")
st.pyplot(fig1)

st.subheader("📈 Daily Installation Trend")
trend_df = df[df["Status"] == "Installed"].copy()
trend_df["Installation Date"] = pd.to_datetime(trend_df["Installation Date"], errors="coerce")
trend = trend_df.groupby(trend_df["Installation Date"].dt.date).size()
fig2, ax2 = plt.subplots()
trend.plot(ax=ax2)
ax2.set_ylabel("Sites Installed")
ax2.set_xlabel("Date")
st.pyplot(fig2)

st.markdown("### 📥 Export Data")
excel_buffer = BytesIO()
df.to_excel(excel_buffer, index=False)
excel_data = excel_buffer.getvalue()

st.download_button("⬇️ Download Excel", data=excel_data, file_name="installation_status.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

df_sample_html = df[["Site ID", "Status", "Installation Date"]].to_html(index=False)
pdf_html = f"<html><body>{df_sample_html}</body></html>"
b64 = base64.b64encode(pdf_html.encode()).decode()
st.markdown(f'<a href="data:text/html;base64,{b64}" download="installation_report.html">⬇️ Download PDF Report</a>', unsafe_allow_html=True)
