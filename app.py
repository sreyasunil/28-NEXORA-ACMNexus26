<<<<<<< HEAD
﻿from datetime import date, timedelta
=======
from datetime import date, timedelta
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
from dataclasses import dataclass
from math import radians, sin, cos, atan2, sqrt

import pandas as pd
import pydeck as pdk
import streamlit as st

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Deforestation Detection & Carbon Impact Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #0f1c1a;
        --panel: #142422;
        --card: #1b2f2b;
        --accent: #8ae18f;
        --accent2: #ff6b6b;
        --text: #f2f7f4;
        --muted: #b6c7bf;
    }
    .main {
        background: radial-gradient(circle at 10% 10%, #16252b 0%, #0f1b20 55%, #0b1418 100%);
        color: var(--text);
        font-family: "Avenir Next", "Segoe UI", sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: var(--muted);
        margin-bottom: 1.5rem;
    }
<<<<<<< HEAD
    .panel {
        background: linear-gradient(180deg, rgba(22, 34, 41, 0.95), rgba(16, 24, 29, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
=======
    .card {
        background: linear-gradient(180deg, rgba(30, 44, 52, 0.92), rgba(20, 30, 36, 0.92));
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
    .panel {
        background: linear-gradient(180deg, rgba(22, 34, 41, 0.95), rgba(16, 24, 29, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
        padding: 0.8rem 1rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.35);
    }
    .panel-title {
        font-size: 1rem;
        font-weight: 700;
        color: #f5f7f8;
        margin-bottom: 0.6rem;
<<<<<<< HEAD
    }
    .card {
        background: linear-gradient(180deg, rgba(30, 44, 52, 0.92), rgba(20, 30, 36, 0.92));
        padding: 0.8rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
=======
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    }
    .metric-title {
        color: var(--muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
    }
    .badge {
        display: inline-block;
        padding: 0.12rem 0.45rem;
        border-radius: 999px;
        background: rgba(138, 225, 143, 0.15);
        color: var(--accent);
        font-size: 0.7rem;
        font-weight: 600;
    }
    .alert {
<<<<<<< HEAD
        padding: 0.75rem 0.9rem;
=======
        padding: 0.8rem 1rem;
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
        border-radius: 12px;
        margin-bottom: 0.6rem;
        color: #f8f2f2;
        font-weight: 600;
    }
    .alert-high {
        background: linear-gradient(120deg, rgba(255, 111, 97, 0.25), rgba(130, 38, 38, 0.25));
        border: 1px solid rgba(255, 107, 107, 0.45);
    }
    .alert-medium {
        background: linear-gradient(120deg, rgba(255, 193, 7, 0.2), rgba(109, 92, 38, 0.25));
        border: 1px solid rgba(255, 193, 7, 0.45);
    }
    .alert-low {
        background: linear-gradient(120deg, rgba(76, 175, 80, 0.18), rgba(33, 99, 45, 0.25));
        border: 1px solid rgba(76, 175, 80, 0.45);
    }
    .image-card {
        height: 210px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(138,225,143,0.2), rgba(255,107,107,0.2));
        border: 1px dashed rgba(255,255,255,0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.4rem;
    }
    .media-img img {
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 24px rgba(0,0,0,0.35);
    }
    .input-label {
        font-size: 0.78rem;
        color: var(--muted);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Mock Backend Logic (Embedded)
# -----------------------------

@dataclass
class BackendResult:
    landcover_geojson: dict
    protected_geojson: dict
    protected_distance_km: float
    metrics: dict
    alerts: list[dict]
    recommendations: list[str]
    trend: pd.DataFrame
    timezone: str
    risk_score: dict


def region_config(region: str) -> dict:
    if region == "Amazon":
        return {"center": [-3.4653, -62.2159], "zoom": 5}
    if region == "Kerala":
        return {"center": [10.1632, 76.6413], "zoom": 7}
    return {"center": [0.0, 0.0], "zoom": 2}


def mock_geojson(center: list[float]) -> dict:
    lat, lon = center
    deforested = {
        "type": "Feature",
        "properties": {"class": "Deforested", "color": [255, 107, 107, 160]},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon - 0.6, lat - 0.4],
                    [lon - 0.2, lat - 0.4],
                    [lon - 0.2, lat + 0.1],
                    [lon - 0.6, lat + 0.1],
                    [lon - 0.6, lat - 0.4],
                ]
            ],
        },
    }
    healthy = {
        "type": "Feature",
        "properties": {"class": "Healthy", "color": [138, 225, 143, 160]},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon + 0.1, lat - 0.2],
                    [lon + 0.7, lat - 0.2],
                    [lon + 0.7, lat + 0.4],
                    [lon + 0.1, lat + 0.4],
                    [lon + 0.1, lat - 0.2],
                ]
            ],
        },
    }
    return {"type": "FeatureCollection", "features": [deforested, healthy]}


def mock_protected_zones(center: list[float]) -> dict:
    lat, lon = center
    protected = {
        "type": "Feature",
        "properties": {"class": "Protected", "color": [86, 180, 255, 140]},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon - 1.0, lat + 0.2],
                    [lon - 0.2, lat + 0.2],
                    [lon - 0.2, lat + 0.8],
                    [lon - 1.0, lat + 0.8],
                    [lon - 1.0, lat + 0.2],
                ]
            ],
        },
    }
    return {"type": "FeatureCollection", "features": [protected]}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return radius_km * c


def mock_metrics() -> dict:
    return {
<<<<<<< HEAD
        "area_lost": "1,250 ha",
        "co2": "780,000 tons",
        "veg_loss": "8,500 MT",
=======
        "area_lost": "120 hectares",
        "co2": "2,400 tons",
        "veg_loss": "18.4%",
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    }


def mock_alerts() -> list[dict]:
    return [
        {"message": "Significant forest clearing detected", "severity": "High", "confidence": 0.92},
        {"message": "Illegal logging activity identified", "severity": "Critical", "confidence": 0.87},
        {"message": "Encroachment near protected zone", "severity": "Moderate", "confidence": 0.80},
    ]


def mock_recommendations() -> list[str]:
    return [
<<<<<<< HEAD
        "Increase patrols in affected zones",
        "Engage local communities",
        "Implement reforestation plans",
=======
        "Suggested Action: Increase patrols in affected zones",
        "Suggested Action: Engage local communities",
        "Suggested Action: Implement reforestation plans",
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    ]


def mock_trend(end_date: date) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.date_range(end=end_date, periods=10),
<<<<<<< HEAD
            "Hectares Lost": [6, 10, 14, 12, 20, 26, 24, 32, 36, 42],
=======
            "Hectares Lost": [8, 12, 14, 13, 18, 24, 22, 30, 34, 40],
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
        }
    )


def climate_risk_score(loss_rate: float, clustering: float, protected_proximity: float) -> dict:
    loss_rate = max(0.0, min(1.0, loss_rate))
    clustering = max(0.0, min(1.0, clustering))
    protected_proximity = max(0.0, min(1.0, protected_proximity))
    score = round((0.5 * loss_rate + 0.3 * clustering + 0.2 * protected_proximity) * 100)
    if score >= 75:
        label = "High"
    elif score >= 50:
        label = "Moderate"
    else:
        label = "Low"
    return {"score": score, "label": label}


def analyze(region: str, start_date: date, end_date: date, focus_center: list[float], timezone: str) -> BackendResult:
    _ = (region, start_date, end_date)
    protected_geojson = mock_protected_zones(focus_center)
    protected_center = protected_geojson["features"][0]["geometry"]["coordinates"][0][0]
    distance_km = _haversine_km(
        focus_center[0],
        focus_center[1],
        protected_center[1],
        protected_center[0],
    )
    return BackendResult(
        landcover_geojson=mock_geojson(focus_center),
        protected_geojson=protected_geojson,
        protected_distance_km=round(distance_km, 1),
        metrics=mock_metrics(),
        alerts=mock_alerts(),
        recommendations=mock_recommendations(),
        trend=mock_trend(end_date),
        timezone=timezone,
        risk_score=climate_risk_score(0.78, 0.62, 0.55),
    )

<<<<<<< HEAD
SIDEBAR_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Amazon_rainforest_DSC01978.jpg/640px-Amazon_rainforest_DSC01978.jpg"
BEFORE_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Forest_in_Borneo.jpg/800px-Forest_in_Borneo.jpg"
AFTER_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Deforestation_in_Brazil.jpg/800px-Deforestation_in_Brazil.jpg"


def format_date_range(start: date, end: date) -> str:
    return f"{start.strftime('%b %d, %Y')} to {end.strftime('%b %d, %Y')}"

=======
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
# -----------------------------
# Sidebar: Inputs
# -----------------------------
with st.sidebar:
<<<<<<< HEAD
    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Inputs</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"input-label\">Region</div>", unsafe_allow_html=True)
    region = st.selectbox("Region", ["Amazon", "Kerala", "Custom"], label_visibility="collapsed")
    base_config = region_config(region)

    st.markdown("<div class=\"input-label\">Timezone</div>", unsafe_allow_html=True)
=======
    st.markdown("### Inputs")
    region = st.selectbox("Select Region", ["Amazon", "Kerala", "Custom"])
    base_config = region_config(region)
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    timezone = st.selectbox(
        "Timezone",
        [
            "UTC",
            "Asia/Kolkata",
            "Asia/Dubai",
            "Europe/London",
            "Europe/Berlin",
            "America/New_York",
            "America/Chicago",
            "America/Denver",
            "America/Los_Angeles",
            "Australia/Sydney",
        ],
<<<<<<< HEAD
        label_visibility="collapsed",
    )

    st.markdown("<div class=\"input-label\">Show Protected Zones</div>", unsafe_allow_html=True)
    show_protected = st.toggle("Show Protected Zones", value=True, label_visibility="collapsed")

    if region == "Custom":
        st.markdown("<div class=\"input-label\">Focus Latitude</div>", unsafe_allow_html=True)
        focus_lat = st.number_input("Focus Latitude", value=base_config["center"][0], format="%.4f", label_visibility="collapsed")
        st.markdown("<div class=\"input-label\">Focus Longitude</div>", unsafe_allow_html=True)
        focus_lon = st.number_input("Focus Longitude", value=base_config["center"][1], format="%.4f", label_visibility="collapsed")
=======
    )
    show_protected = st.toggle("Show Protected Zones", value=True)
    if region == "Custom":
        focus_lat = st.number_input("Focus Latitude", value=base_config["center"][0], format="%.4f")
        focus_lon = st.number_input("Focus Longitude", value=base_config["center"][1], format="%.4f")
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
        focus_center = [focus_lat, focus_lon]
    else:
        focus_center = base_config["center"]

<<<<<<< HEAD
    st.markdown("<div class=\"input-label\">Date Range</div>", unsafe_allow_html=True)
=======
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    today = date.today()
    start_default = today - timedelta(days=30)
    start_date, end_date = st.date_input(
        "Date Range",
        value=(start_default, today),
        max_value=today,
        label_visibility="collapsed",
    )
    analyze_clicked = st.button("Analyze")
    st.caption(format_date_range(start_date, end_date))
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Analyze Action
# -----------------------------
if analyze_clicked:
    with st.spinner("Running satellite analysis and AI inference..."):
        st.session_state["result"] = analyze(region, start_date, end_date, focus_center, timezone)

if "result" not in st.session_state:
    st.session_state["result"] = analyze(region, start_date, end_date, focus_center, timezone)

result = st.session_state["result"]

# -----------------------------
# Sidebar: Key Metrics
# -----------------------------
with st.sidebar:
    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Key Metrics</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"media-img\">", unsafe_allow_html=True)
    st.image(SIDEBAR_IMAGE_URL, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    satellite_layer = pdk.Layer(
        "TileLayer",
        data="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        min_zoom=0,
        max_zoom=19,
        tile_size=256,
    )
    geo_layer = pdk.Layer(
        "GeoJsonLayer",
        result.landcover_geojson,
        pickable=True,
        opacity=0.6,
        stroked=True,
        filled=True,
        get_fill_color="properties.color",
        get_line_color=[240, 240, 240],
        line_width_min_pixels=1,
    )
    protected_layer = pdk.Layer(
        "GeoJsonLayer",
        result.protected_geojson,
        pickable=True,
        opacity=0.5,
        stroked=True,
        filled=True,
        get_fill_color="properties.color",
        get_line_color=[86, 180, 255],
        line_width_min_pixels=2,
    )
    view_state = pdk.ViewState(
        latitude=focus_center[0],
        longitude=focus_center[1],
        zoom=base_config["zoom"],
        pitch=25,
    )
    layers = [satellite_layer, geo_layer, protected_layer] if show_protected else [satellite_layer, geo_layer]
    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style=None,
        ),
        height=180,
    )
<<<<<<< HEAD

    st.markdown(
        f"""
        <div class="card" style="margin-top:0.6rem;">
=======
    analyze_clicked = st.button("Analyze")

# -----------------------------
# Analyze Action
# -----------------------------
if analyze_clicked:
    with st.spinner("Running satellite analysis and AI inference..."):
        st.session_state["result"] = analyze(region, start_date, end_date, focus_center, timezone)

if "result" not in st.session_state:
    st.session_state["result"] = analyze(region, start_date, end_date, focus_center, timezone)

result = st.session_state["result"]

# -----------------------------
# Sidebar: Metrics
# -----------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("### Key Metrics")
    st.markdown(
        f"""
        <div class="card">
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
            <div class="metric-title">Forest Area Lost</div>
            <div class="metric-value">{result.metrics['area_lost']}</div>
            <div class="badge">Mock Data</div>
        </div>
        <div style="height: 0.4rem"></div>
        <div class="card">
            <div class="metric-title">Estimated CO₂ Emissions</div>
            <div class="metric-value">{result.metrics['co2']}</div>
            <div class="badge">Mock Data</div>
        </div>
        <div style="height: 0.4rem"></div>
        <div class="card">
            <div class="metric-title">Vegetation Loss</div>
            <div class="metric-value">{result.metrics['veg_loss']}</div>
            <div class="badge">Mock Data</div>
        </div>
        <div style="height: 0.4rem"></div>
        <div class="card">
            <div class="metric-title">Climate Risk</div>
            <div class="metric-value">{result.risk_score['score']} / 100</div>
            <div class="badge">{result.risk_score['label']} Risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
<<<<<<< HEAD
    st.markdown("</div>", unsafe_allow_html=True)
=======
    st.markdown("<div style=\"height: 0.6rem\"></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-title">Climate Risk Score</div>
            <div class="metric-value">{result.risk_score['score']} / 100</div>
            <div class="badge">{result.risk_score['label']} Risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="title" style="text-align:center;">AI-Based Deforestation Monitoring System</div>
    <div class="subtitle" style="text-align:center;">Detect forest loss and estimate climate impact using satellite data</div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Main Layout
# -----------------------------
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Satellite Map (No Token)</div>", unsafe_allow_html=True)
<<<<<<< HEAD
    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style=None,
        )
    )
    st.caption("Tip: Use Custom region to set the focus with lat/lon.")
    st.caption("Satellite tiles powered by Esri World Imagery (no token required).")
    st.markdown("</div>", unsafe_allow_html=True)

=======
    satellite_layer = pdk.Layer(
        "TileLayer",
        data="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        min_zoom=0,
        max_zoom=19,
        tile_size=256,
    )
    geo_layer = pdk.Layer(
        "GeoJsonLayer",
        result.landcover_geojson,
        pickable=True,
        opacity=0.6,
        stroked=True,
        filled=True,
        get_fill_color="properties.color",
        get_line_color=[240, 240, 240],
        line_width_min_pixels=1,
    )
    protected_layer = pdk.Layer(
        "GeoJsonLayer",
        result.protected_geojson,
        pickable=True,
        opacity=0.5,
        stroked=True,
        filled=True,
        get_fill_color="properties.color",
        get_line_color=[86, 180, 255],
        line_width_min_pixels=2,
    )

    view_state = pdk.ViewState(
        latitude=focus_center[0],
        longitude=focus_center[1],
        zoom=base_config["zoom"],
        pitch=30,
    )

    layers = [satellite_layer, geo_layer, protected_layer] if show_protected else [satellite_layer, geo_layer]

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            map_style=None,
        )
    )
    st.caption("Tip: Use Custom region to set the focus with lat/lon.")
    st.caption("Satellite tiles powered by Esri World Imagery (no token required).")
    st.markdown("</div>", unsafe_allow_html=True)

>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Deforestation Trend</div>", unsafe_allow_html=True)
    st.line_chart(result.trend, x="Date", y="Hectares Lost", height=220)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Priority Alerts</div>", unsafe_allow_html=True)
    for alert in result.alerts:
        confidence = int(alert["confidence"] * 100)
        severity = alert["severity"].lower()
<<<<<<< HEAD
        severity_class = "alert-high" if severity in ["high", "critical"] else "alert-low" if severity == "moderate" else "alert-medium"
=======
        severity_class = "alert-high" if severity in ["high", "critical"] else "alert-medium" if severity == "moderate" else "alert-low"
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
        st.markdown(
            f"<div class=\"alert {severity_class}\">⚠️ {alert['message']}<br/>Severity: {alert['severity']} · Confidence: {confidence}%</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Protected Area Proximity</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class=\"card\">Distance to protected land: <strong>{result.protected_distance_km} km</strong></div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Intervention Recommendation</div>", unsafe_allow_html=True)
    for rec in result.recommendations:
        st.markdown(
            f"<div class=\"card\" style=\"margin-bottom: 0.4rem;\">{rec}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Before vs After</div>", unsafe_allow_html=True)
    view_mode = st.toggle("Side-by-side comparison", value=True)

    if view_mode:
        before_col, after_col = st.columns(2)
        with before_col:
            st.markdown("<div class=\"media-img\">", unsafe_allow_html=True)
            st.image(BEFORE_IMAGE_URL, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with after_col:
            st.markdown("<div class=\"media-img\">", unsafe_allow_html=True)
            st.image(AFTER_IMAGE_URL, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        tab_before, tab_after = st.tabs(["Before", "After"])
        with tab_before:
            st.markdown("<div class=\"media-img\">", unsafe_allow_html=True)
            st.image(BEFORE_IMAGE_URL, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with tab_after:
<<<<<<< HEAD
            st.markdown("<div class=\"media-img\">", unsafe_allow_html=True)
            st.image(AFTER_IMAGE_URL, use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
=======
            st.markdown("<div class=\"image-card\">After</div>", unsafe_allow_html=True)
>>>>>>> f89a30473ff0144d2c3f0388ed0b78b6dc16fef7
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer Notes
# -----------------------------
st.markdown(
    """
    <div class="card" style="margin-top: 1rem;">
        <div class="metric-title">System Status</div>
        <div>✅ AI model: Online · ✅ Satellite feed: Active · ✅ Alerts: Enabled</div>
    </div>
    """,
    unsafe_allow_html=True,
)
