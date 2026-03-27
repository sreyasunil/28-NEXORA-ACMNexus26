from datetime import date, timedelta
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Deforestation Detection & Carbon Impact Dashboard",
    layout="wide",
)

# -----------------------------
# Helper (replace backend)
# -----------------------------
def region_config(region):
    if region == "Amazon":
        return {"center": [-3.4, -62.2], "zoom": 5}
    if region == "Kerala":
        return {"center": [10.16, 76.64], "zoom": 7}
    return {"center": [0, 0], "zoom": 2}

def generate_mock_result():
    return {
        "area_lost": "120 hectares",
        "co2": "2400 tons",
        "veg_loss": "18%",
        "risk_score": {"score": 78, "label": "High"},
        "trend": pd.DataFrame({
            "Date": pd.date_range(end=date.today(), periods=10),
            "Hectares Lost": [5,10,8,15,20,18,22,25,28,30]
        }),
        "alerts": [
            {"message": "Large-scale clearing detected", "severity": "High", "confidence": 0.9},
            {"message": "Rapid vegetation loss", "severity": "Medium", "confidence": 0.75}
        ]
    }

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("### Inputs")
    region = st.selectbox("Select Region", ["Amazon", "Kerala", "Custom"])
    config = region_config(region)

    today = date.today()
    start_date, end_date = st.date_input(
        "Date Range",
        value=(today - timedelta(days=30), today),
    )

    analyze = st.button("Analyze")

# -----------------------------
# DATA
# -----------------------------
result = generate_mock_result()

# -----------------------------
# Sidebar Metrics
# -----------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### Key Metrics")

    st.metric("Forest Area Lost", result["area_lost"])
    st.metric("CO₂ Emissions", result["co2"])
    st.metric("Vegetation Loss", result["veg_loss"])
    st.metric("Risk Score", f"{result['risk_score']['score']} ({result['risk_score']['label']})")

# -----------------------------
# Header
# -----------------------------
st.title("🌍 AI-Based Deforestation Monitoring System")
st.caption("Uses NDVI + satellite data (GEE-ready architecture)")

# -----------------------------
# Layout
# -----------------------------
col1, col2 = st.columns([2,1])

# -----------------------------
# MAP
# -----------------------------
with col1:
    st.subheader("Satellite Map")

    m = folium.Map(
        location=[config["center"][0], config["center"][1]],
        zoom_start=config["zoom"]
    )

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Esri Satellite",
        max_zoom=18
    ).add_to(m)

    st_folium(m, height=400, use_container_width=True)

    st.subheader("Deforestation Trend")
    st.line_chart(result["trend"], x="Date", y="Hectares Lost")

# -----------------------------
# RIGHT PANEL
# -----------------------------
with col2:
    st.subheader("Alerts")
    for alert in result["alerts"]:
        st.warning(f"{alert['message']} ({int(alert['confidence']*100)}%)")

    st.subheader("Before vs After")
    colA, colB = st.columns(2)
    colA.info("Before Image")
    colB.info("After Image")

# -----------------------------
# Footer
# -----------------------------
st.success("System running: AI + Satellite Ready")