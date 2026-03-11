import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html
import joblib
import numpy as np
import random
import os

st.set_page_config(
    page_title=" Flood Warning KZ",
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

RISK_COLORS = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "darkred"}
RISK_EMOJI  = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}

@st.cache_resource
def load_model():
    return joblib.load("model/flood_model.joblib")

model = load_model()

def predict(region, rainfall, temp, humidity, river, snow, prev):
    features = np.array([[rainfall, temp, humidity, river, snow, prev]])
    pred = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    labels = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
    return {
        "region": region,
        "risk_level": labels[pred],
        "risk_emoji": RISK_EMOJI[labels[pred]],
        "confidence": f"{max(proba):.1%}",
        "probabilities": {labels[i]: f"{proba[i]:.1%}" for i in range(4)}
    }

def simulate_weather(region):
    random.seed(hash(region) % 1000)
    profiles = {
        "Almaty":      (random.uniform(40,90), random.uniform(5,20), random.uniform(60,90), random.uniform(3,7), random.uniform(20,45), random.uniform(30,70)),
        "Astana":      (random.uniform(10,40), random.uniform(-5,15), random.uniform(40,70), random.uniform(1,4), random.uniform(10,30), random.uniform(10,40)),
        "Shymkent":    (random.uniform(30,70), random.uniform(10,30), random.uniform(50,80), random.uniform(2,5), random.uniform(5,20), random.uniform(20,50)),
        "Karaganda":   (random.uniform(15,50), random.uniform(-5,20), random.uniform(40,65), random.uniform(1,3), random.uniform(10,25), random.uniform(10,35)),
        "Aktobe":      (random.uniform(20,60), random.uniform(0,25), random.uniform(45,75), random.uniform(2,6), random.uniform(15,35), random.uniform(15,45)),
        "Pavlodar":    (random.uniform(50,100), random.uniform(0,20), random.uniform(65,90), random.uniform(4,8), random.uniform(25,50), random.uniform(40,75)),
        "Semey":       (random.uniform(20,55), random.uniform(-5,20), random.uniform(40,70), random.uniform(1,4), random.uniform(10,25), random.uniform(10,35)),
        "Taraz":       (random.uniform(25,65), random.uniform(5,28), random.uniform(50,80), random.uniform(2,5), random.uniform(10,30), random.uniform(20,50)),
        "Oskemen":     (random.uniform(60,110), random.uniform(0,18), random.uniform(70,95), random.uniform(5,8), random.uniform(30,50), random.uniform(50,80)),
        "Atyrau":      (random.uniform(5,30), random.uniform(5,30), random.uniform(30,60), random.uniform(1,3), random.uniform(0,10), random.uniform(5,25)),
        "Kostanay":    (random.uniform(20,55), random.uniform(-5,18), random.uniform(45,70), random.uniform(1,4), random.uniform(15,35), random.uniform(15,40)),
        "Kyzylorda":   (random.uniform(5,25), random.uniform(10,35), random.uniform(30,55), random.uniform(1,3), random.uniform(0,10), random.uniform(5,20)),
        "Aktau":       (random.uniform(5,20), random.uniform(8,32), random.uniform(35,60), random.uniform(0.5,2), random.uniform(0,5), random.uniform(5,15)),
        "Petropavl":   (random.uniform(25,65), random.uniform(-8,18), random.uniform(50,75), random.uniform(2,5), random.uniform(20,40), random.uniform(20,50)),
        "Taldykorgan": (random.uniform(45,95), random.uniform(5,22), random.uniform(60,88), random.uniform(3,7), random.uniform(20,45), random.uniform(35,70)),
    }
    return profiles.get(region, (30, 15, 60, 2, 10, 20))

# Header
st.title("🌊 Flood Early Warning System — Kazakhstan")
st.markdown("**AI-powered flood risk prediction for all regions of Kazakhstan**")
st.divider()

# Sidebar - single city check
st.sidebar.header("🔍 Check a City")
selected_city = st.sidebar.selectbox("📍 Select City", list(REGIONS.keys()))
rainfall  = st.sidebar.slider("🌧️ Rainfall (mm)", 0.0, 120.0, 30.0)
temperature = st.sidebar.slider("🌡️ Temperature (°C)", -10.0, 35.0, 15.0)
humidity  = st.sidebar.slider("💧 Humidity (%)", 20.0, 100.0, 60.0)
river_level = st.sidebar.slider("🌊 River Level (m)", 0.5, 8.0, 2.0)
snow_melt = st.sidebar.slider("❄️ Snow Melt (mm)", 0.0, 50.0, 10.0)
prev_rain = st.sidebar.slider("📅 Prev Day Rain (mm)", 0.0, 80.0, 20.0)

if st.sidebar.button("🔍 Check This City", type="primary", use_container_width=True):
    result = predict(selected_city, rainfall, temperature, humidity, river_level, snow_melt, prev_rain)
    risk = result["risk_level"]
    st.session_state.city_result = result

if "city_result" in st.session_state:
    r = st.session_state.city_result
    risk = r["risk_level"]
    emoji = r["risk_emoji"]
    st.sidebar.divider()
    if risk == "Critical": st.sidebar.error(f"🚨 {r['region']}\n\n## {emoji} {risk} Risk")
    elif risk == "High":   st.sidebar.warning(f"⚠️ {r['region']}\n\n## {emoji} {risk} Risk")
    elif risk == "Medium": st.sidebar.info(f"📢 {r['region']}\n\n## {emoji} {risk} Risk")
    else:                  st.sidebar.success(f"✅ {r['region']}\n\n## {emoji} {risk} Risk")
    st.sidebar.markdown(f"**Confidence:** {r['confidence']}")
    st.sidebar.divider()
    for level, prob in r["probabilities"].items():
        bar = "█" * int(float(prob.strip("%")) / 10)
        st.sidebar.markdown(f"{RISK_EMOJI[level]} {level}: `{prob}` {bar}")

# Main buttons
col_btn1, col_btn2, _ = st.columns([1, 1, 4])
with col_btn1:
    predict_all = st.button("🔄 Predict All Regions", type="primary", use_container_width=True)
with col_btn2:
    simulate_new = st.button("🎲 New Weather", use_container_width=True)

if predict_all or simulate_new or "all_predictions" not in st.session_state:
    if simulate_new:
        random.seed()
    with st.spinner("🤖 Running AI for all 15 regions..."):
        preds = []
        for reg in REGIONS:
            w = simulate_weather(reg)
            r = predict(reg, *w)
            preds.append({**r, "rainfall_mm": round(w[0],1), "river_level_m": round(w[3],1), "humidity_pct": round(w[2],1)})
    st.session_state.all_predictions = preds

predictions = st.session_state.all_predictions
counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
for p in predictions:
    if p["risk_level"] in counts:
        counts[p["risk_level"]] += 1

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("🟢 Low Risk",    f"{counts['Low']} regions")
c2.metric("🟡 Medium Risk", f"{counts['Medium']} regions")
c3.metric("🟠 High Risk",   f"{counts['High']} regions")
c4.metric("🔴 Critical",    f"{counts['Critical']} regions")
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("🗺️ Kazakhstan Risk Map")
    m = folium.Map(location=[48.0, 66.0], zoom_start=6, tiles="CartoDB dark_matter")
    for p in predictions:
        coords = REGIONS[p["region"]]
        risk  = p["risk_level"]
        color = RISK_COLORS.get(risk, "gray")
        emoji = RISK_EMOJI.get(risk, "⚪")
        folium.CircleMarker(
            location=coords, radius=22, color=color, weight=2,
            fill=True, fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(
                f"<b>{p['region']}</b><br>Risk: {emoji} {risk}<br>"
                f"Confidence: {p['confidence']}<br>"
                f"Rainfall: {p['rainfall_mm']} mm<br>"
                f"River: {p['river_level_m']} m", max_width=200),
            tooltip=f"{p['region']}: {emoji} {risk}"
        ).add_to(m)
    html(m._repr_html_(), height=500)

with col2:
    st.subheader("📊 All Regions")
    df = pd.DataFrame([{
        "Region": p["region"],
        "Risk": f"{RISK_EMOJI.get(p['risk_level'],'⚪')} {p['risk_level']}",
        "Confidence": p["confidence"],
        "Rain (mm)": p["rainfall_mm"],
        "River (m)": p["river_level_m"],
    } for p in predictions])
    st.dataframe(df, use_container_width=True, height=500)

critical = [p for p in predictions if p["risk_level"] == "Critical"]
high     = [p for p in predictions if p["risk_level"] == "High"]
if critical:
    st.error(f"🚨 CRITICAL ALERT: {', '.join([p['region'] for p in critical])} — Immediate action required!")
if high:
    st.warning(f"⚠️ HIGH RISK: {', '.join([p['region'] for p in high])} — Monitor closely!")

st.caption("⚡ Powered by XGBoost ML | 84% Accuracy | Decentrathon 5.0")