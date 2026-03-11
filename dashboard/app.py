import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html
import requests
import random

st.set_page_config(
    page_title="🌊 Flood Warning KZ",
    page_icon="🌊",
    layout="wide"
)

REGIONS = {
    "Almaty":       (43.2220, 76.8512),
    "Astana":       (51.1801, 71.4460),
    "Shymkent":     (42.3000, 69.6000),
    "Karaganda":    (49.8047, 73.1094),
    "Aktobe":       (50.2839, 57.1670),
    "Pavlodar":     (52.2873, 76.9674),
    "Semey":        (50.4111, 80.2275),
    "Taraz":        (42.9000, 71.3667),
    "Oskemen":      (49.9483, 82.6283),
    "Atyrau":       (47.1167, 51.8833),
    "Kostanay":     (53.2144, 63.6249),
    "Kyzylorda":    (44.8488, 65.5092),
    "Aktau":        (43.6500, 51.1667),
    "Petropavl":    (54.8647, 69.1536),
    "Taldykorgan":  (45.0153, 78.3729),
}

RISK_COLORS = {
    "Low": "green",
    "Medium": "orange",
    "High": "red",
    "Critical": "darkred"
}

RISK_EMOJI = {
    "Low": "🟢",
    "Medium": "🟡",
    "High": "🟠",
    "Critical": "🔴"
}

# Simulate realistic weather per region
def simulate_weather(region):
    random.seed(hash(region) % 1000)
    profiles = {
        "Almaty":      dict(rainfall=random.uniform(40, 90), temp=random.uniform(5, 20), humidity=random.uniform(60, 90), river=random.uniform(3, 7), snow=random.uniform(20, 45), prev=random.uniform(30, 70)),
        "Astana":      dict(rainfall=random.uniform(10, 40), temp=random.uniform(-5, 15), humidity=random.uniform(40, 70), river=random.uniform(1, 4), snow=random.uniform(10, 30), prev=random.uniform(10, 40)),
        "Shymkent":    dict(rainfall=random.uniform(30, 70), temp=random.uniform(10, 30), humidity=random.uniform(50, 80), river=random.uniform(2, 5), snow=random.uniform(5, 20), prev=random.uniform(20, 50)),
        "Karaganda":   dict(rainfall=random.uniform(15, 50), temp=random.uniform(-5, 20), humidity=random.uniform(40, 65), river=random.uniform(1, 3), snow=random.uniform(10, 25), prev=random.uniform(10, 35)),
        "Aktobe":      dict(rainfall=random.uniform(20, 60), temp=random.uniform(0, 25), humidity=random.uniform(45, 75), river=random.uniform(2, 6), snow=random.uniform(15, 35), prev=random.uniform(15, 45)),
        "Pavlodar":    dict(rainfall=random.uniform(50, 100), temp=random.uniform(0, 20), humidity=random.uniform(65, 90), river=random.uniform(4, 8), snow=random.uniform(25, 50), prev=random.uniform(40, 75)),
        "Semey":       dict(rainfall=random.uniform(20, 55), temp=random.uniform(-5, 20), humidity=random.uniform(40, 70), river=random.uniform(1, 4), snow=random.uniform(10, 25), prev=random.uniform(10, 35)),
        "Taraz":       dict(rainfall=random.uniform(25, 65), temp=random.uniform(5, 28), humidity=random.uniform(50, 80), river=random.uniform(2, 5), snow=random.uniform(10, 30), prev=random.uniform(20, 50)),
        "Oskemen":     dict(rainfall=random.uniform(60, 110), temp=random.uniform(0, 18), humidity=random.uniform(70, 95), river=random.uniform(5, 8), snow=random.uniform(30, 50), prev=random.uniform(50, 80)),
        "Atyrau":      dict(rainfall=random.uniform(5, 30), temp=random.uniform(5, 30), humidity=random.uniform(30, 60), river=random.uniform(1, 3), snow=random.uniform(0, 10), prev=random.uniform(5, 25)),
        "Kostanay":    dict(rainfall=random.uniform(20, 55), temp=random.uniform(-5, 18), humidity=random.uniform(45, 70), river=random.uniform(1, 4), snow=random.uniform(15, 35), prev=random.uniform(15, 40)),
        "Kyzylorda":   dict(rainfall=random.uniform(5, 25), temp=random.uniform(10, 35), humidity=random.uniform(30, 55), river=random.uniform(1, 3), snow=random.uniform(0, 10), prev=random.uniform(5, 20)),
        "Aktau":       dict(rainfall=random.uniform(5, 20), temp=random.uniform(8, 32), humidity=random.uniform(35, 60), river=random.uniform(0.5, 2), snow=random.uniform(0, 5), prev=random.uniform(5, 15)),
        "Petropavl":   dict(rainfall=random.uniform(25, 65), temp=random.uniform(-8, 18), humidity=random.uniform(50, 75), river=random.uniform(2, 5), snow=random.uniform(20, 40), prev=random.uniform(20, 50)),
        "Taldykorgan": dict(rainfall=random.uniform(45, 95), temp=random.uniform(5, 22), humidity=random.uniform(60, 88), river=random.uniform(3, 7), snow=random.uniform(20, 45), prev=random.uniform(35, 70)),
    }
    return profiles.get(region, dict(rainfall=30, temp=15, humidity=60, river=2, snow=10, prev=20))

def predict_all_regions():
    results = []
    for region in REGIONS:
        w = simulate_weather(region)
        try:
            response = requests.post("http://127.0.0.1:8000/predict", json={
                "region": region,
                "rainfall_mm": w["rainfall"],
                "temperature_c": w["temp"],
                "humidity_pct": w["humidity"],
                "river_level_m": w["river"],
                "snow_melt_mm": w["snow"],
                "prev_day_rain": w["prev"]
            }, timeout=3)
            result = response.json()
            results.append({
                "region": region,
                "risk_level": result["risk_level"],
                "confidence": result["confidence"],
                "rainfall_mm": round(w["rainfall"], 1),
                "river_level_m": round(w["river"], 1),
                "humidity_pct": round(w["humidity"], 1),
            })
        except:
            results.append({
                "region": region,
                "risk_level": "Unknown",
                "confidence": "N/A",
                "rainfall_mm": round(w["rainfall"], 1),
                "river_level_m": round(w["river"], 1),
                "humidity_pct": round(w["humidity"], 1),
            })
    return results

# Header
st.title("🌊 Flood Early Warning System — Kazakhstan")
st.markdown("**AI-powered flood risk prediction for all regions of Kazakhstan**")
st.divider()

# Auto predict on load
if "all_predictions" not in st.session_state:
    st.session_state.all_predictions = None

col_btn1, col_btn2, _ = st.columns([1, 1, 4])
with col_btn1:
    if st.button("🔄 Predict All Regions", type="primary", use_container_width=True):
        with st.spinner("🤖 Running AI predictions for all 15 regions..."):
            st.session_state.all_predictions = predict_all_regions()
        st.success("✅ Predictions complete!")

with col_btn2:
    if st.button("🎲 Simulate New Weather", use_container_width=True):
        random.seed()
        with st.spinner("🌦️ Simulating new weather conditions..."):
            st.session_state.all_predictions = predict_all_regions()
        st.success("✅ New weather simulated!")

st.divider()

# Show results
if st.session_state.all_predictions:
    predictions = st.session_state.all_predictions

    # Stats row
    counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for p in predictions:
        if p["risk_level"] in counts:
            counts[p["risk_level"]] += 1

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🟢 Low Risk", f"{counts['Low']} regions")
    c2.metric("🟡 Medium Risk", f"{counts['Medium']} regions")
    c3.metric("🟠 High Risk", f"{counts['High']} regions")
    c4.metric("🔴 Critical", f"{counts['Critical']} regions")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🗺️ Kazakhstan Risk Map")
        m = folium.Map(location=[48.0, 66.0], zoom_start=6,
                       tiles="CartoDB dark_matter")

        for p in predictions:
            coords = REGIONS[p["region"]]
            risk = p["risk_level"]
            color = RISK_COLORS.get(risk, "gray")
            emoji = RISK_EMOJI.get(risk, "⚪")

            folium.CircleMarker(
                location=coords,
                radius=22,
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b>{p['region']}</b><br>"
                    f"Risk: {emoji} {risk}<br>"
                    f"Confidence: {p['confidence']}<br>"
                    f"Rainfall: {p['rainfall_mm']} mm<br>"
                    f"River: {p['river_level_m']} m",
                    max_width=200
                ),
                tooltip=f"{p['region']}: {emoji} {risk}"
            ).add_to(m)

        map_html = m._repr_html_()
        html(map_html, height=500)

    with col2:
        st.subheader("📊 All Regions")
        df = pd.DataFrame([{
            "Region": p["region"],
            "Risk": f"{RISK_EMOJI.get(p['risk_level'], '⚪')} {p['risk_level']}",
            "Confidence": p["confidence"],
            "Rain (mm)": p["rainfall_mm"],
            "River (m)": p["river_level_m"],
        } for p in predictions])
        st.dataframe(df, use_container_width=True, height=500)

    # Critical alerts
    critical = [p for p in predictions if p["risk_level"] == "Critical"]
    high = [p for p in predictions if p["risk_level"] == "High"]

    if critical:
        st.divider()
        st.error(f"🚨 CRITICAL ALERT: {', '.join([p['region'] for p in critical])} — Immediate action required!")
    if high:
        st.warning(f"⚠️ HIGH RISK: {', '.join([p['region'] for p in high])} — Monitor closely!")

else:
    st.info("👆 Click **'Predict All Regions'** to run AI predictions for all of Kazakhstan!")

st.caption("⚡ Powered by XGBoost ML | 84% Accuracy | Decentrathon 5.0")