
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from io import BytesIO

st.set_page_config(layout="wide")
st.title("ODC-AC Installation Progress Dashboard")
st.markdown("**Prepared by: Mohammed Alfadhel**")

# Load site database from Excel
excel_path = "ODC-AC Installation progress   02-March-25  _.xlsx"
df_sites = pd.read_excel(excel_path, sheet_name="Tracking Sheet")

# Load installed sites from Google Sheet manually exported (simulate)
installed_sites = [
    # Mocked list for demonstration
    "RIY0001", "RIY0005", "RIY0020"
]

# Status logic
df_sites["Status"] = df_sites["Site Name"].apply(
    lambda x: "Installed" if str(x).strip() in installed_sites else "Open"
)

# Colors for status
def get_marker_color(status):
    return "green" if status == "Installed" else "red"

# Create folium map
m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)
for _, row in df_sites.iterrows():
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=f"{row['Site Name']} - {row['Status']}",
        icon=folium.Icon(color=get_marker_color(row["Status"]))
    ).add_to(m)

# Display map
st_data = st_folium(m, width=1100)

# Export options
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Download Excel"):
        excel_io = BytesIO()
        df_sites.to_excel(excel_io, index=False)
        st.download_button("Download Excel File", data=excel_io.getvalue(), file_name="site_status.xlsx")

with col2:
    if st.button("📥 Download PDF"):
        st.info("🔧 PDF Export will be enabled in final deployment.")
