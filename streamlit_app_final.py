
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from io import BytesIO

st.set_page_config(layout="wide")
st.title("ODC-AC Installation Progress Dashboard")
st.markdown("**Prepared by: Mohammed Alfadhel**")

# Load site database from GitHub
excel_url = "https://raw.githubusercontent.com/mrakai123/ODC-AC-Installation-progress-/main/ODC-AC%20Installation%20progress%2002-March-25%20_.xlsx"
df_sites = pd.read_excel(excel_url, sheet_name="Tracking Sheet")

# Simulated Installed Site Names from Google Form sheet (to be replaced by live fetch)
installed_sites = [
    "RIY0001", "RIY0005", "RIY0020"
]

# Add status column
df_sites["Status"] = df_sites["Site Name"].apply(
    lambda x: "Installed" if str(x).strip() in installed_sites else "Open"
)

# Function to determine marker color
def get_marker_color(status):
    return "green" if status == "Installed" else "red"

# Create map
m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)
for i in range(len(df_sites)):
    site_name = df_sites.loc[i, "Site Name"]
    lat = df_sites.loc[i, "Latitude"]
    lon = df_sites.loc[i, "Longitude"]
    status = df_sites.loc[i, "Status"]
    folium.Marker(
        location=[lat, lon],
        popup=f"{site_name} - {status}",
        icon=folium.Icon(color=get_marker_color(status))
    ).add_to(m)

# Show map
st_data = st_folium(m, width=1100)

# Download buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Download Excel"):
        excel_io = BytesIO()
        df_sites.to_excel(excel_io, index=False)
        st.download_button("Download Excel File", data=excel_io.getvalue(), file_name="site_status.xlsx")

with col2:
    if st.button("📥 Download PDF"):
        st.info("🔧 PDF Export will be enabled in final deployment.")
