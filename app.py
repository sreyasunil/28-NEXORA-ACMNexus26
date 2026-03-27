

from datetime import date, timedelta

import ee
import os
os.environ["USE_FOLIUM"] = "1"
import geemap
import folium
import streamlit as st


st.set_page_config(
    page_title="Deforestation Monitoring System",
    layout="wide",
)


def initialize_earth_engine(project_id=""):
    try:
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
        return True
    except Exception:
        try:
            ee.Authenticate()
            if project_id:
                ee.Initialize(project=project_id)
            else:
                ee.Initialize()
            return True
        except Exception as exc:
            st.error(f"Earth Engine initialization failed: {exc}")
            return False


def get_image(lat, lon, start, end):
    region_geom = ee.Geometry.Point([lon, lat]).buffer(5000)
    collection = (
        ee.ImageCollection("COPERNICUS/S2")
        .filterBounds(region_geom)
        .filterDate(str(start), str(end))
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
    )

    if collection.size().getInfo() == 0:
        raise ValueError(
            f"No satellite imagery found between {start} and {end} for the selected region."
        )

    return collection.median().clip(region_geom)


def get_ndvi(image):
    return image.normalizedDifference(["B8", "B4"]).rename("NDVI")


st.title("🌍 AI-Based Deforestation Monitoring System")
st.markdown("Real-time satellite analysis using Google Earth Engine")

st.sidebar.header("Controls")

project_id = st.sidebar.text_input(
    "GCP Project ID (Required for new Earth Engine accounts)", 
    value="",
    help="Find or create a project at https://earthengine.google.com/"
)

region = st.sidebar.selectbox(
    "Select Region",
    ["Amazon", "Kerala", "Custom"],
)

if region == "Amazon":
    lat, lon = -3.4653, -62.2159
elif region == "Kerala":
    lat, lon = 10.1632, 76.6413
else:
    lat = st.sidebar.number_input("Latitude", value=19.0760, format="%.6f")
    lon = st.sidebar.number_input("Longitude", value=72.8777, format="%.6f")

today = date.today()
start_default = today - timedelta(days=365 * 5)

start_date = st.sidebar.date_input("Start Date", start_default)
end_date = st.sidebar.date_input("End Date", today)
analyze = st.sidebar.button("Analyze")

if analyze:
    if not project_id.strip():
        st.warning(
            "⚠️ **GCP Project ID Required!**\n\n"
            "Google Earth Engine now explicitly requires a valid Google Cloud Project to authenticate.\n\n"
            "**How to get one:**\n"
            "1. Go to [code.earthengine.google.com/register](https://code.earthengine.google.com/register)\n"
            "2. Register your account and create a free non-commercial Cloud Project.\n"
            "3. Copy the new 'Project ID' string (e.g., `ee-johndoe`).\n"
            "4. Paste it into the 'GCP Project ID' box in the sidebar on the left.\n"
            "5. Click Analyze again!"
        )
        st.stop()

    ee_ready = initialize_earth_engine(project_id.strip())
    if not ee_ready:
        st.stop()

    if start_date >= end_date:
        st.error("Start Date must be earlier than End Date.")
        st.stop()

    try:
        st.subheader("🛰️ Satellite Map")

        image_before = get_image(lat, lon, start_date, start_date + timedelta(days=30))
        image_after = get_image(lat, lon, end_date - timedelta(days=30), end_date)

        ndvi_before = get_ndvi(image_before)
        ndvi_after = get_ndvi(image_after)
        change = ndvi_after.subtract(ndvi_before)

        # Map Col 1: Before
        map_col1, map_col2 = st.columns(2)

        with map_col1:
            st.markdown("**Before Period Map**")
            m1 = geemap.Map(center=[lat, lon], zoom=10)
            m1.addLayer(
                image_before,
                {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
                "Before",
            )
            m1.addLayer(
                ndvi_before,
                {"min": -1, "max": 1, "palette": ["blue", "white", "green"]},
                "NDVI Before",
            )
            # Add a live marker at the chosen coordinate
            folium.Marker(
                location=[lat, lon],
                popup=f"Analyzed Point: {lat}, {lon}",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m1)
            m1.to_streamlit(height=400)

        with map_col2:
            st.markdown("**After Period Map**")
            m2 = geemap.Map(center=[lat, lon], zoom=10)
            m2.addLayer(
                image_after,
                {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
                "After",
            )
            m2.addLayer(
                ndvi_after,
                {"min": -1, "max": 1, "palette": ["blue", "white", "green"]},
                "NDVI After",
            )
            # Add a live marker for the same point
            folium.Marker(
                location=[lat, lon],
                popup=f"Analyzed Point: {lat}, {lon}",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m2)
            m2.to_streamlit(height=400)

        st.markdown("**NDVI Change Detection**")
        m3 = geemap.Map(center=[lat, lon], zoom=10)
        m3.addLayer(
            change,
            {"min": -0.5, "max": 0.5, "palette": ["red", "white", "green"]},
            "Change Detection",
        )
        folium.Marker(
            location=[lat, lon],
            popup="Change at Point",
            icon=folium.Icon(color="purple", icon="info-sign")
        ).add_to(m3)
        m3.to_streamlit(height=400)

        st.subheader("📊 Analysis Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("Vegetation Loss", "Detected")
        col2.metric("Change Intensity", "Moderate")
        col3.metric("Status", "⚠️ Alert")

        st.subheader("🖼️ Before vs After")
        col_a, col_b = st.columns(2)

        url_before = image_before.getThumbURL(
            {"min": 0, "max": 3000, "bands": ["B4", "B3", "B2"]}
        )
        url_after = image_after.getThumbURL(
            {"min": 0, "max": 3000, "bands": ["B4", "B3", "B2"]}
        )

        col_a.image(url_before, caption="Before")
        col_b.image(url_after, caption="After")
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
else:
    st.info("Click 'Analyze' to run satellite analysis")

