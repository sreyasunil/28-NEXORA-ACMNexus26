from datetime import date, timedelta
from dataclasses import dataclass
from math import radians, sin, cos, atan2, sqrt

import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
    /* Global App Background Override for Streamlit Native */
    [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background: radial-gradient(circle at 10% 10%, #16252b 0%, #0f1b20 55%, #0b1418 100%) !important;
        color: var(--text) !important;
        font-family: "Avenir Next", "Segoe UI", sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: #121e24 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        display: none !important;
    }
    .block-container {
        padding-top: 2rem !important;
        max-width: 95% !important;
    }
    
    .main {
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
    .panel {
        background: linear-gradient(180deg, rgba(22, 34, 41, 0.95), rgba(16, 24, 29, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 0.8rem 1rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.35);
    }
    .panel-title {
        font-size: 1rem;
        font-weight: 700;
        color: #f5f7f8;
        margin-bottom: 0.6rem;
    }
    .card {
        background: linear-gradient(180deg, rgba(30, 44, 52, 0.92), rgba(20, 30, 36, 0.92));
        padding: 0.8rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
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
        margin-left: 0.4rem;
    }
    .alert {
        padding: 0.75rem 0.9rem;
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
    .intervention-card {
        flex: 1;
        background: linear-gradient(180deg, rgba(38, 70, 53, 0.9), rgba(22, 43, 33, 0.9));
        border: 1px solid rgba(138, 225, 143, 0.3);
        border-radius: 8px;
        padding: 0.6rem 0.4rem;
        text-align: center;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f2f7f4;
    }
    .intervention-card:hover {
        background: linear-gradient(180deg, rgba(48, 85, 65, 0.9), rgba(28, 53, 41, 0.9));
        border-color: rgba(138, 225, 143, 0.8);
        transform: translateY(-2px);
    }
    .overlay-label {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(30, 44, 52, 0.85);
        padding: 0.2rem 1.2rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255,255,255,0.15);
        z-index: 10;
        pointer-events: none;
        color: #fff;
    }
    .app-footer {
        position: fixed;
        bottom: 0px;
        left: 0;
        width: 100%;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
        color: #a1b8ae;
        background: linear-gradient(to top, rgba(16, 28, 26, 1) 0%, rgba(16, 28, 26, 0.8) 40%, transparent 100%);
        z-index: 100;
    }
    /* Wrap native Streamlit containers to look like panels */
    [data-testid="stArrowVegaLiteChart"] {
        background: linear-gradient(180deg, rgba(22, 34, 41, 0.95), rgba(16, 24, 29, 0.95));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.35);
        margin-bottom: 1rem;
    }
    .css-1544g2n {
        padding-bottom: 5rem;
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


def mock_geojson(center: list[float], region: str) -> dict:
    import random
    lat, lon = center
    
    # Dynamic generation based on region
    def_offset = 0.5 if region == "Amazon" else 0.1
    hel_offset = 0.6 if region == "Amazon" else 0.2
    
    deforested = {
        "type": "Feature",
        "properties": {"class": "Deforested", "color": [255, 107, 107, 180]},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon - def_offset, lat - def_offset/2],
                    [lon - def_offset/3, lat - def_offset/2],
                    [lon - def_offset/3, lat + def_offset/4],
                    [lon - def_offset, lat + def_offset/4],
                    [lon - def_offset, lat - def_offset/2],
                ]
            ],
        },
    }
    healthy = {
        "type": "Feature",
        "properties": {"class": "Healthy", "color": [138, 225, 143, 140]},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon + 0.1, lat - hel_offset/2],
                    [lon + hel_offset, lat - hel_offset/2],
                    [lon + hel_offset, lat + hel_offset],
                    [lon + 0.1, lat + hel_offset],
                    [lon + 0.1, lat - hel_offset/2],
                ]
            ],
        },
    }
    return {"type": "FeatureCollection", "features": [deforested, healthy]}


def mock_protected_zones(center: list[float], region: str) -> dict:
    lat, lon = center
    offset = 0.8 if region == "Amazon" else 0.3
    protected = {
        "type": "Feature",
        "properties": {"class": "Protected", "color": [86, 180, 255, 120]},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [lon - offset, lat + offset/4],
                    [lon - offset/4, lat + offset/4],
                    [lon - offset/4, lat + offset],
                    [lon - offset, lat + offset],
                    [lon - offset, lat + offset/4],
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


def mock_metrics(region: str, days: int) -> dict:
    import random
    
    if region == "Amazon":
        base_area = 1250
        base_co2 = 780000
    elif region == "Kerala":
        base_area = 340
        base_co2 = 125000
    else:
        base_area = 500
        base_co2 = 250000
    
    factor = max(1, days) / 30.0
    area = int(base_area * factor + random.randint(-50, 50))
    co2 = int(base_co2 * factor + random.randint(-10000, 10000))
    veg = int(area * 6.8)
    
    return {
        "area_lost": f"{max(0, area):,} ha",
        "co2": f"{max(0, co2):,} tons",
        "veg_loss": f"{max(0, veg):,} MT",
    }


def mock_alerts(region: str) -> list[dict]:
    import random
    opts = []
    if region == "Amazon":
        opts = [
            {"message": "Significant forest clearing detected!", "severity": "High", "confidence": round(random.uniform(0.85, 0.98), 2)},
            {"message": "Illegal logging activity identified.", "severity": "Critical", "confidence": round(random.uniform(0.8, 0.95), 2)},
            {"message": "Encroachment near indigenous reserve.", "severity": "Moderate", "confidence": round(random.uniform(0.7, 0.85), 2)},
        ]
    elif region == "Kerala":
        opts = [
            {"message": "Landslide vulnerabilities identified.", "severity": "Critical", "confidence": round(random.uniform(0.8, 0.92), 2)},
            {"message": "Unregulated plantation expansion.", "severity": "High", "confidence": round(random.uniform(0.75, 0.9), 2)},
            {"message": "Canopy degradation in buffer zone.", "severity": "Moderate", "confidence": round(random.uniform(0.65, 0.8), 2)},
        ]
    else:
        opts = [
            {"message": "Vegetation index anomaly detected.", "severity": "High", "confidence": round(random.uniform(0.75, 0.95), 2)},
            {"message": "Potential slash-and-burn activity.", "severity": "Critical", "confidence": round(random.uniform(0.8, 0.9), 2)},
            {"message": "Proximity alert to protected border.", "severity": "Moderate", "confidence": round(random.uniform(0.6, 0.8), 2)},
        ]
    
    random.shuffle(opts)
    return opts


def mock_recommendations(region: str) -> list[str]:
    import random
    core = [
        "Increase patrols<br>in affected zones",
        "Engage local<br>communities",
        "Implement<br>reforestation plans",
        "Deploy drone<br>surveillance",
        "Review land<br>use permits"
    ]
    random.shuffle(core)
    return core[:3]


def mock_trend(start_date: date, end_date: date) -> pd.DataFrame:
    import numpy as np
    days = (end_date - start_date).days
    if days < 1:
        days = 1
    periods = min(days + 1, 30)
    dates = pd.date_range(end=end_date, periods=periods)
    base = np.linspace(5, 40, periods)
    if "Amazon" not in start_date.strftime("%Y"): # trick to make it random but stable-ish
        noise = np.random.normal(0, 3, periods)
    else:
        noise = np.random.normal(0, 5, periods)
    hl = np.clip(base + noise, 0, None).round(1)
    
    # Scale total magnitude by duration
    hl = hl * (days / 15.0)
    return pd.DataFrame(
        {
            "Date": dates,
            "Hectares Lost": hl,
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


def generate_pdf_report(region: str, start_date: date, end_date: date, result: BackendResult) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center align
    title_style.textColor = colors.HexColor("#1b2f2b")
    
    h2_style = styles['Heading2']
    h2_style.textColor = colors.HexColor("#264635")
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    elements = []
    
    # Header
    elements.append(Paragraph(f"Environmental Compliance Report", title_style))
    elements.append(Paragraph(f"Impact Analysis: {region.upper()}", title_style))
    elements.append(Spacer(1, 20))
    
    # Metadata
    elements.append(Paragraph(f"<b>Report Generated:</b> {date.today()}", normal_style))
    elements.append(Paragraph(f"<b>Analysis Period:</b> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}", normal_style))
    elements.append(Paragraph(f"<b>Timezone:</b> {result.timezone}", normal_style))
    elements.append(Spacer(1, 25))
    
    # Key Metrics Table
    elements.append(Paragraph("Key Metrics Summary", h2_style))
    metrics_data = [
        ["Metric", "Estimated Value"],
        ["Forest Area Lost", result.metrics['area_lost']],
        ["Estimated CO2 Emissions", result.metrics['co2']],
        ["Vegetation Loss", result.metrics['veg_loss']],
        ["Distance to Protected Area", f"{result.protected_distance_km} km"],
        ["AI Risk Score", f"{result.risk_score['score']}/100 ({result.risk_score['label']})"]
    ]
    t = Table(metrics_data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#142422")),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f2f7f4")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#b6c7bf")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 25))
    
    # Priority Alerts
    elements.append(Paragraph("System Identified Priority Alerts", h2_style))
    for alert in result.alerts:
        sev_color = "red" if alert['severity'] in ["Critical", "High"] else "orange" if alert['severity'] == "Moderate" else "green"
        text = f"• <font color='{sev_color}'><b>[{alert['severity'].upper()}]</b></font> {alert['message']} (Confidence: {int(alert['confidence']*100)}%)"
        elements.append(Paragraph(text, normal_style))
    elements.append(Spacer(1, 25))
    
    # Recommendations
    elements.append(Paragraph("Recommended Interventions", h2_style))
    for rec in result.recommendations:
        clean_rec = str(rec).replace("<br>", " ")
        elements.append(Paragraph(f"• {clean_rec}", normal_style))
        
    # Footer Notice
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<i>This document was generated automatically by the AI-Based Deforestation Monitoring System.</i>", styles['Italic']))
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def analyze(region: str, start_date: date, end_date: date, focus_center: list[float], timezone: str) -> BackendResult:
    days = (end_date - start_date).days
    protected_geojson = mock_protected_zones(focus_center, region)
    protected_center = protected_geojson["features"][0]["geometry"]["coordinates"][0][0]
    distance_km = _haversine_km(
        focus_center[0],
        focus_center[1],
        protected_center[1],
        protected_center[0],
    )
    import random
    
    # Make risk score fully dynamic
    loss_rate = random.uniform(0.4, 0.9)
    clustering = random.uniform(0.3, 0.8)
    prox_score = max(0.0, 1.0 - (distance_km / 100))
    
    return BackendResult(
        landcover_geojson=mock_geojson(focus_center, region),
        protected_geojson=protected_geojson,
        protected_distance_km=round(abs(distance_km) + random.uniform(0.1, 5.0), 1),
        metrics=mock_metrics(region, days),
        alerts=mock_alerts(region),
        recommendations=mock_recommendations(region),
        trend=mock_trend(start_date, end_date),
        timezone=timezone,
        risk_score=climate_risk_score(loss_rate, clustering, prox_score),
    )

SIDEBAR_IMAGE_URL = "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80"
BEFORE_IMAGE_URL = "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80"
AFTER_IMAGE_URL = "https://images.unsplash.com/photo-1519451241324-20b4ea2c4220?auto=format&fit=crop&w=800&q=80"


def format_date_range(start: date, end: date) -> str:
    return f"{start.strftime('%b %d, %Y')} to {end.strftime('%b %d, %Y')}"

# -----------------------------
# Sidebar: Inputs
# -----------------------------
with st.sidebar:
    st.markdown("<div class=\"panel\"><div class=\"panel-title\">Inputs</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"input-label\">Region</div>", unsafe_allow_html=True)
    region = st.selectbox("Region", ["Amazon", "Kerala", "Custom"], label_visibility="collapsed")
    base_config = region_config(region)

    st.markdown("<div class=\"input-label\">Timezone</div>", unsafe_allow_html=True)
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
        label_visibility="collapsed",
    )

    st.markdown("<div class=\"input-label\">Show Protected Zones</div>", unsafe_allow_html=True)
    show_protected = st.toggle("Show Protected Zones", value=True, label_visibility="collapsed")

    if region == "Custom":
        st.markdown("<div class=\"input-label\">Focus Latitude</div>", unsafe_allow_html=True)
        focus_lat = st.number_input("Focus Latitude", value=base_config["center"][0], format="%.4f", label_visibility="collapsed")
        st.markdown("<div class=\"input-label\">Focus Longitude</div>", unsafe_allow_html=True)
        focus_lon = st.number_input("Focus Longitude", value=base_config["center"][1], format="%.4f", label_visibility="collapsed")
        focus_center = [focus_lat, focus_lon]
    else:
        focus_center = base_config["center"]

    st.markdown("<div class=\"input-label\">Date Range</div>", unsafe_allow_html=True)
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
# Analyze Action & Auto-Reactivity
# -----------------------------
# We auto-run analysis anytime inputs change so it feels "fully functional" and reactive
with st.spinner("Running satellite analysis and AI inference..."):
    st.session_state["result"] = analyze(region, start_date, end_date, focus_center, timezone)

result = st.session_state["result"]

# -----------------------------
# Sidebar: Key Metrics
# -----------------------------
with st.sidebar:
    # Wrap ALL key metrics in ONE single HTML string to keep styling intact

    def create_satellite_map(res, show_prot, center, zoom, is_before=False):
        m = folium.Map(location=[center[0], center[1]], zoom_start=zoom, tiles=None, control_scale=True)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="Esri Satellite",
            overlay=False,
            control=False
        ).add_to(m)

        def landcover_style(feature):
            c = feature["properties"]["color"]
            if is_before and feature["properties"].get("class") == "Deforested":
                # Hide the deforestation layer for the 'Before' view so it just shows native robust satellite trees
                return {'fillOpacity': 0, 'weight': 0, 'opacity': 0}
            
            return {
                'fillColor': '#%02x%02x%02x' % tuple(c[:3]),
                'color': '#f0f0f0',
                'weight': 1,
                'fillOpacity': c[3]/255.0
            }
        folium.GeoJson(res.landcover_geojson, style_function=landcover_style, name="Landcover").add_to(m)

        if show_prot:
            def protected_style(feature):
                c = feature["properties"]["color"]
                return {
                    'fillColor': '#%02x%02x%02x' % tuple(c[:3]),
                    'color': '#56b4ff',
                    'weight': 2,
                    'fillOpacity': c[3]/255.0
                }
            folium.GeoJson(res.protected_geojson, style_function=protected_style, name="Protected Zones").add_to(m)
        return m

    # Sidebar map instance
    sidebar_map = create_satellite_map(result, show_protected, focus_center, max(1, base_config["zoom"] - 1))
    st_folium(sidebar_map, height=180, use_container_width=True, key="sidebar_folium", returned_objects=[])

    metrics_html = f"""
        <div class="panel">
            <div class="panel-title" style="margin-top: 12px;">Key Metrics Summary</div>
            <div class="card" style="margin-top:0.6rem;">
                <div class="metric-title">Forest Area Lost</div>
                <div style="display: flex; align-items: baseline;">
                    <div class="metric-value">{result.metrics['area_lost']}</div>
                    <div class="badge">Mock Data</div>
                </div>
            </div>
            <div style="height: 0.4rem"></div>
            <div class="card">
                <div class="metric-title">Estimated CO₂ Emissions</div>
                <div style="display: flex; align-items: baseline;">
                    <div class="metric-value">{result.metrics['co2']}</div>
                    <div class="badge">Mock Data</div>
                </div>
            </div>
            <div style="height: 0.4rem"></div>
            <div class="card">
                <div class="metric-title">Vegetation Loss</div>
                <div style="display: flex; align-items: baseline;">
                    <div class="metric-value">{result.metrics['veg_loss']}</div>
                    <div class="badge">Mock Data</div>
                </div>
            </div>
            <div style="height: 0.4rem"></div>
            <div class="card">
                <div class="metric-title">Climate Risk</div>
                <div style="display: flex; align-items: baseline;">
                    <div class="metric-value">{result.risk_score['score']} / 100</div>
                    <div class="badge" style="background: {'rgba(255, 111, 97, 0.15)' if result.risk_score['label'] == 'High' else 'rgba(255, 193, 7, 0.2)'}; 
                                              color: {'#ff6b6b' if result.risk_score['label'] == 'High' else '#ffc107'};">
                        {result.risk_score['label']} Risk
                    </div>
                </div>
            </div>
        </div>
        """
    st.markdown(metrics_html, unsafe_allow_html=True)
    
    # Export Compliance Report Button
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div class=\"panel-title\">Official Agency Export</div>", unsafe_allow_html=True)
    pdf_bytes = generate_pdf_report(region, start_date, end_date, result)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name=f"compliance_report_{region.lower().replace(' ', '_')}_{date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

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
    st.markdown("<div style=\"font-weight: 700; color: #f5f7f8; margin-bottom: 0.6rem;\">Satellite Map (No Token)</div>", unsafe_allow_html=True)
    
    # Main wrapper to hold the panel styling for the folium map
    st.markdown("<div class=\"panel\" style=\"padding: 0.2rem; margin-bottom: 0.6rem;\">", unsafe_allow_html=True)
    main_map = create_satellite_map(result, show_protected, focus_center, base_config["zoom"])
    st_folium(main_map, height=360, use_container_width=True, key="main_folium", returned_objects=[])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style=\"margin-top: 1rem; font-weight: 700; color: #f5f7f8; margin-bottom: 0.6rem;\">Deforestation Trend</div>", unsafe_allow_html=True)
    try:
        st.line_chart(result.trend, x="Date", y="Hectares Lost", height=220, color="#ff6b6b")
    except TypeError:
        st.line_chart(result.trend, x="Date", y="Hectares Lost", height=220)

with col_right:
    # Compile Priority Alerts directly into ONE html block
    alerts_html = "<div class=\"panel\"><div class=\"panel-title\">Priority Alerts</div>"
    for alert in result.alerts:
        confidence = int(alert["confidence"] * 100)
        severity = alert["severity"].lower()
        severity_class = "alert-high" if severity in ["high", "critical"] else "alert-low" if severity == "moderate" else "alert-medium"
        alerts_html += f"<div class=\"alert {severity_class}\">⚠️ {alert['message']}<br/><span style='font-weight:400; font-size:0.85rem; color:#d1d1d1;'>Severity: {alert['severity']} &bull; Confidence: {confidence}%</span></div>"
    alerts_html += "</div>"
    st.markdown(alerts_html, unsafe_allow_html=True)

    # Compile Proximity Panel directly into ONE html block
    prox_html = "<div class=\"panel\"><div class=\"panel-title\">Protected Area Proximity</div>"
    prox_html += f"<div class=\"card\">Distance to protected land: <strong style='font-size: 1.1em; margin-left:8px; color:#8ae18f'>{result.protected_distance_km} km</strong></div>"
    prox_html += "</div>"
    st.markdown(prox_html, unsafe_allow_html=True)

    # Compile Interventions directly into ONE html block
    rec_html = "<div class=\"panel\"><div class=\"panel-title\">Intervention Recommendation</div>"
    rec_html += '<div style="display: flex; gap: 0.5rem;">'
    for rec in result.recommendations:
        rec_html += f'<div class="intervention-card">{rec}</div>'
    rec_html += '</div></div>'
    st.markdown(rec_html, unsafe_allow_html=True)

    # The Before vs After panel is moving to the bottom of the page!

# -----------------------------
# Before vs After (Full Width Bottom Section)
# -----------------------------
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

head1, head2 = st.columns([3, 1])
with head1:
    st.markdown("<div class=\"title\" style=\"font-size: 1.6rem;\">Terrain Impact Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"subtitle\">High-resolution comparison of local forest cover changes over the selected date range.</div>", unsafe_allow_html=True)
with head2:
    view_mode = st.toggle("Side-by-side comparison", value=True)

st.markdown("<div class=\"panel\" style=\"padding: 0.8rem; background: linear-gradient(180deg, rgba(16,24,29,0.9), rgba(11,18,22,0.9));\">", unsafe_allow_html=True)

if view_mode:
    img1, img2 = st.columns(2, gap="small")
    with img1:
        st.markdown(f"""
        <div style="position: relative; width: 100%; margin-bottom: 0.4rem;">
            <div class="overlay-label" style="top: 15px; background: rgba(0,0,0,0.85); font-size: 0.95rem; letter-spacing: 0.05em; padding: 0.3rem 1.5rem; border: 1px solid rgba(255,255,255,0.3);">Baseline Setup (Healthy Forest)</div>
        </div>
        """, unsafe_allow_html=True)
        # Create map with no deforestation overlay (is_before=True)
        before_map = create_satellite_map(result, show_prot=False, center=focus_center, zoom=base_config["zoom"] + 1, is_before=True)
        st_folium(before_map, height=340, use_container_width=True, key="bottom_before_map", returned_objects=[])

    with img2:
        st.markdown(f"""
        <div style="position: relative; width: 100%; margin-bottom: 0.4rem;">
            <div class="overlay-label" style="top: 15px; background: rgba(220,53,69,0.9); font-size: 0.95rem; letter-spacing: 0.05em; padding: 0.3rem 1.5rem; border: 1px solid rgba(255,255,255,0.3);">Current Impact (Deforested)</div>
        </div>
        """, unsafe_allow_html=True)
        # Create map with deforestation shown (is_before=False)
        after_map = create_satellite_map(result, show_prot=False, center=focus_center, zoom=base_config["zoom"] + 1, is_before=False)
        st_folium(after_map, height=340, use_container_width=True, key="bottom_after_map", returned_objects=[])
else:
    st.markdown(f"""
    <div style="position: relative; width: 100%; margin-bottom: 0.4rem;">
        <div class="overlay-label" style="top: 15px; background: rgba(220,53,69,0.9); font-size: 0.95rem; letter-spacing: 0.05em; padding: 0.3rem 1.5rem;">Overlay View</div>
    </div>
    """, unsafe_allow_html=True)
    overlay_map = create_satellite_map(result, show_prot=True, center=focus_center, zoom=base_config["zoom"] + 1, is_before=False)
    st_folium(overlay_map, height=450, use_container_width=True, key="bottom_overlay_map", returned_objects=[])

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Footer Notes and Background 
# -----------------------------
st.markdown(
    """
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; height: 260px; 
                background: url('https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&q=80&w=2000') center bottom / cover; 
                z-index: -2; opacity: 0.15; pointer-events: none;
                mask-image: linear-gradient(to top, black 20%, transparent 100%);
                -webkit-mask-image: linear-gradient(to top, black 20%, transparent 100%);"></div>
    <div class="app-footer">
        <label style="background: rgba(16,28,26,0.6); padding: 5px 15px; border-radius: 9px;">
            <span style="color: #8ae18f">✅ AI model:</span> Online &bull; 
            <span style="color: #8ae18f">✅ Satellite feed:</span> Active &bull; 
            <span style="color: #8ae18f">✅ Alerts:</span> Enabled
        </label>
    </div>
    <div style="height: 4rem;"></div>
    """,
    unsafe_allow_html=True,
)
