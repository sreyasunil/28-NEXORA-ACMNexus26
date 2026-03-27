from datetime import date, timedelta

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
        background: radial-gradient(circle at 10% 10%, #15312c 0%, #0f1c1a 55%, #0b1513 100%);
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
    .card {
        background: var(--card);
        padding: 1rem 1.2rem;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .metric-title {
        color: var(--muted);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
    }
    .badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        background: rgba(138, 225, 143, 0.15);
        color: var(--accent);
        font-size: 0.75rem;
        font-weight: 600;
    }
    .alert {
        background: rgba(255, 107, 107, 0.12);
        border: 1px solid rgba(255, 107, 107, 0.35);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.6rem;
        color: #ffd6d6;
        font-weight: 600;
    }
    .image-card {
        height: 240px;
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
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helper Functions
# -----------------------------

def region_config(region: str):
    if region == "Amazon":
        return {"center": [-3.4653, -62.2159], "zoom": 5}
    if region == "Kerala":
        return {"center": [10.1632, 76.6413], "zoom": 7}
    return {"center": [0.0, 0.0], "zoom": 2}


def mock_geojson(center):
    lat, lon = center
    # Two simple polygons for demo: deforested (red) and healthy (green)
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
    return {
        "type": "FeatureCollection",
        "features": [deforested, healthy],
    }


# -----------------------------
# Sidebar: Inputs & Metrics
# -----------------------------
with st.sidebar:
    st.markdown("### Inputs")
    region = st.selectbox("Select Region", ["Amazon", "Kerala", "Custom"])
    today = date.today()
    start_default = today - timedelta(days=30)
    start_date, end_date = st.date_input(
        "Date Range",
        value=(start_default, today),
        max_value=today,
    )
    analyze = st.button("Analyze")

    st.markdown("---")
    st.markdown("### Key Metrics")
    st.markdown(
        """
        <div class="card">
            <div class="metric-title">Forest Area Lost</div>
            <div class="metric-value">120 hectares</div>
            <div class="badge">Mock Data</div>
        </div>
        <div style="height: 0.6rem"></div>
        <div class="card">
            <div class="metric-title">Estimated CO₂ Emissions</div>
            <div class="metric-value">2,400 tons</div>
            <div class="badge">Mock Data</div>
        </div>
        <div style="height: 0.6rem"></div>
        <div class="card">
            <div class="metric-title">Vegetation Loss</div>
            <div class="metric-value">18.4%</div>
            <div class="badge">Mock Data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div class="title">AI-Based Deforestation Monitoring System</div>
    <div class="subtitle">Detect forest loss and estimate climate impact using satellite data</div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Analyze Action (Mock Processing)
# -----------------------------
if analyze:
    with st.spinner("Running satellite analysis and AI inference..."):
        st.session_state["analysis_ready"] = True
else:
    st.session_state.setdefault("analysis_ready", True)

# -----------------------------
# Main Layout
# -----------------------------
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.markdown("<div class=\"section-title\">Interactive Map</div>", unsafe_allow_html=True)
    config = region_config(region)
    geojson = mock_geojson(config["center"])

    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson,
        pickable=True,
        opacity=0.7,
        stroked=True,
        filled=True,
        get_fill_color="properties.color",
        get_line_color=[240, 240, 240],
        line_width_min_pixels=1,
    )

    view_state = pdk.ViewState(
        latitude=config["center"][0],
        longitude=config["center"][1],
        zoom=config["zoom"],
        pitch=30,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=None))

    st.markdown("<div class=\"section-title\">Deforestation Trend</div>", unsafe_allow_html=True)
    trend_data = pd.DataFrame(
        {
            "Date": pd.date_range(end=end_date, periods=10),
            "Hectares Lost": [8, 12, 9, 15, 18, 22, 19, 24, 28, 30],
        }
    )
    st.line_chart(trend_data, x="Date", y="Hectares Lost", height=220)

with col_right:
    st.markdown("<div class=\"section-title\">Suspicious Activity Alerts</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"alert\">⚠️ Large-scale clearing detected</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"alert\">⚠️ Rapid vegetation loss observed</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"alert\">⚠️ Clustered deforestation patterns found</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"section-title\">Before vs After</div>", unsafe_allow_html=True)
    view_mode = st.toggle("Side-by-side comparison", value=True)

    if view_mode:
        before_col, after_col = st.columns(2)
        with before_col:
            st.markdown("<div class=\"image-card\">Before</div>", unsafe_allow_html=True)
        with after_col:
            st.markdown("<div class=\"image-card\">After</div>", unsafe_allow_html=True)
    else:
        tab_before, tab_after = st.tabs(["Before", "After"])
        with tab_before:
            st.markdown("<div class=\"image-card\">Before</div>", unsafe_allow_html=True)
        with tab_after:
            st.markdown("<div class=\"image-card\">After</div>", unsafe_allow_html=True)

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
