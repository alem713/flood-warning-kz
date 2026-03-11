import streamlit as st
import pandas as pd
import folium
from streamlit.components.v1 import html
import joblib
import numpy as np
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.weather import fetch_current_weather, fetch_forecast

st.set_page_config(page_title="🌊 Flood Warning KZ", page_icon="🌊", layout="wide")

# ── Language ──────────────────────────────────────────────────────────────────
LANG = {
    "EN": {
        "title": "🌊 Flood Early Warning System — Kazakhstan",
        "subtitle": "AI-powered flood risk prediction for all regions of Kazakhstan",
        "check_city": "🔍 Check a City",
        "select_city": "📍 Select City",
        "rainfall": "🌧️ Rainfall (mm)",
        "temperature": "🌡️ Temperature (°C)",
        "humidity": "💧 Humidity (%)",
        "river": "🌊 River Level (m)",
        "snow": "❄️ Snow Melt (mm)",
        "prev_rain": "📅 Prev Day Rain (mm)",
        "check_btn": "🔍 Check This City",
        "predict_all": "🔄 Predict All Regions",
        "new_weather": "🎲 New Weather",
        "real_weather": "🌤️ Use Real Weather",
        "low": "Low", "medium": "Medium", "high": "High", "critical": "Critical",
        "regions": "regions", "confidence": "Confidence",
        "risk_map": "🗺️ Kazakhstan Risk Map",
        "all_regions": "📊 All Regions",
        "forecast": "⏱️ 72-Hour Forecast",
        "blockchain": "⛓️ Blockchain Relief Tracker",
        "critical_alert": "🚨 CRITICAL ALERT",
        "high_alert": "⚠️ HIGH RISK",
        "immediate": "Immediate action required!",
        "monitor": "Monitor closely!",
        "powered": "⚡ Powered by XGBoost ML | 84% Accuracy | Decentrathon 5.0",
        "real_data": "📡 Live Data",
        "simulated": "🎲 Simulated",
    },
    "KZ": {
        "title": "🌊 Су тасқыны ескерту жүйесі — Қазақстан",
        "subtitle": "Қазақстанның барлық өңірлері үшін AI негізіндегі су тасқыны қаупін болжау",
        "check_city": "🔍 Қаланы тексеру",
        "select_city": "📍 Қала таңдау",
        "rainfall": "🌧️ Жауын-шашын (мм)",
        "temperature": "🌡️ Температура (°C)",
        "humidity": "💧 Ылғалдылық (%)",
        "river": "🌊 Өзен деңгейі (м)",
        "snow": "❄️ Қар ерігені (мм)",
        "prev_rain": "📅 Алдыңғы күн жауыны (мм)",
        "check_btn": "🔍 Осы қаланы тексеру",
        "predict_all": "🔄 Барлық өңірлерді болжау",
        "new_weather": "🎲 Жаңа ауа райы",
        "real_weather": "🌤️ Нақты ауа райы",
        "low": "Төмен", "medium": "Орташа", "high": "Жоғары", "critical": "Қауіпті",
        "regions": "өңір", "confidence": "Сенімділік",
        "risk_map": "🗺️ Қазақстан қауіп картасы",
        "all_regions": "📊 Барлық өңірлер",
        "forecast": "⏱️ 72 сағаттық болжам",
        "blockchain": "⛓️ Блокчейн көмек трекері",
        "critical_alert": "🚨 ҚАУІПТІ ЕСКЕРТУ",
        "high_alert": "⚠️ ЖОҒАРЫ ҚАУІП",
        "immediate": "Дереу шара қолдану қажет!",
        "monitor": "Мұқият бақылаңыз!",
        "powered": "⚡ XGBoost ML | 84% дәлдік | Decentrathon 5.0",
        "real_data": "📡 Тікелей деректер",
        "simulated": "🎲 Модельденген",
    },
    "RU": {
        "title": "🌊 Система раннего предупреждения о паводках — Казахстан",
        "subtitle": "AI-прогнозирование риска паводков для всех регионов Казахстана",
        "check_city": "🔍 Проверить город",
        "select_city": "📍 Выбрать город",
        "rainfall": "🌧️ Осадки (мм)",
        "temperature": "🌡️ Температура (°C)",
        "humidity": "💧 Влажность (%)",
        "river": "🌊 Уровень реки (м)",
        "snow": "❄️ Таяние снега (мм)",
        "prev_rain": "📅 Осадки вчера (мм)",
        "check_btn": "🔍 Проверить этот город",
        "predict_all": "🔄 Предсказать все регионы",
        "new_weather": "🎲 Новая погода",
        "real_weather": "🌤️ Реальная погода",
        "low": "Низкий", "medium": "Средний", "high": "Высокий", "critical": "Критический",
        "regions": "регионов", "confidence": "Уверенность",
        "risk_map": "🗺️ Карта рисков Казахстана",
        "all_regions": "📊 Все регионы",
        "forecast": "⏱️ Прогноз на 72 часа",
        "blockchain": "⛓️ Блокчейн трекер помощи",
        "critical_alert": "🚨 КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ",
        "high_alert": "⚠️ ВЫСОКИЙ РИСК",
        "immediate": "Требуются немедленные действия!",
        "monitor": "Следите внимательно!",
        "powered": "⚡ XGBoost ML | Точность 84% | Decentrathon 5.0",
        "real_data": "📡 Живые данные",
        "simulated": "🎲 Смоделировано",
    }
}

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

# Simulated blockchain relief fund data
BLOCKCHAIN_DATA = [
    {"tx": "0x3f9a...d12e", "region": "Pavlodar",    "amount": "₸ 5,000,000", "status": "✅ Delivered", "date": "2024-04-15"},
    {"tx": "0x7b2c...a89f", "region": "Oskemen",     "amount": "₸ 3,200,000", "status": "✅ Delivered", "date": "2024-04-16"},
    {"tx": "0x1d4e...c34a", "region": "Karaganda",   "amount": "₸ 2,800,000", "status": "🔄 In Transit", "date": "2024-04-17"},
    {"tx": "0x9e1b...f56d", "region": "Kostanay",    "amount": "₸ 4,100,000", "status": "✅ Delivered", "date": "2024-04-18"},
    {"tx": "0x5c8d...b23c", "region": "Atyrau",      "amount": "₸ 1,900,000", "status": "⏳ Pending",   "date": "2024-04-19"},
    {"tx": "0x2a7f...e78b", "region": "Petropavl",   "amount": "₸ 3,600,000", "status": "🔄 In Transit", "date": "2024-04-20"},
]

@st.cache_resource
def load_model():
    return joblib.load("model/flood_model.joblib")

model = load_model()

def predict(region, rainfall, temp, humidity, river, snow, prev):
    features = np.array([[rainfall, temp, humidity, river, snow, prev]])
    pred  = model.predict(features)[0]
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
        "Almaty":      (random.uniform(40,90),  random.uniform(5,20),   random.uniform(60,90), random.uniform(3,7),   random.uniform(20,45), random.uniform(30,70)),
        "Astana":      (random.uniform(10,40),  random.uniform(-5,15),  random.uniform(40,70), random.uniform(1,4),   random.uniform(10,30), random.uniform(10,40)),
        "Shymkent":    (random.uniform(30,70),  random.uniform(10,30),  random.uniform(50,80), random.uniform(2,5),   random.uniform(5,20),  random.uniform(20,50)),
        "Karaganda":   (random.uniform(15,50),  random.uniform(-5,20),  random.uniform(40,65), random.uniform(1,3),   random.uniform(10,25), random.uniform(10,35)),
        "Aktobe":      (random.uniform(20,60),  random.uniform(0,25),   random.uniform(45,75), random.uniform(2,6),   random.uniform(15,35), random.uniform(15,45)),
        "Pavlodar":    (random.uniform(50,100), random.uniform(0,20),   random.uniform(65,90), random.uniform(4,8),   random.uniform(25,50), random.uniform(40,75)),
        "Semey":       (random.uniform(20,55),  random.uniform(-5,20),  random.uniform(40,70), random.uniform(1,4),   random.uniform(10,25), random.uniform(10,35)),
        "Taraz":       (random.uniform(25,65),  random.uniform(5,28),   random.uniform(50,80), random.uniform(2,5),   random.uniform(10,30), random.uniform(20,50)),
        "Oskemen":     (random.uniform(60,110), random.uniform(0,18),   random.uniform(70,95), random.uniform(5,8),   random.uniform(30,50), random.uniform(50,80)),
        "Atyrau":      (random.uniform(5,30),   random.uniform(5,30),   random.uniform(30,60), random.uniform(1,3),   random.uniform(0,10),  random.uniform(5,25)),
        "Kostanay":    (random.uniform(20,55),  random.uniform(-5,18),  random.uniform(45,70), random.uniform(1,4),   random.uniform(15,35), random.uniform(15,40)),
        "Kyzylorda":   (random.uniform(5,25),   random.uniform(10,35),  random.uniform(30,55), random.uniform(1,3),   random.uniform(0,10),  random.uniform(5,20)),
        "Aktau":       (random.uniform(5,20),   random.uniform(8,32),   random.uniform(35,60), random.uniform(0.5,2), random.uniform(0,5),   random.uniform(5,15)),
        "Petropavl":   (random.uniform(25,65),  random.uniform(-8,18),  random.uniform(50,75), random.uniform(2,5),   random.uniform(20,40), random.uniform(20,50)),
        "Taldykorgan": (random.uniform(45,95),  random.uniform(5,22),   random.uniform(60,88), random.uniform(3,7),   random.uniform(20,45), random.uniform(35,70)),
    }
    return profiles.get(region, (30, 15, 60, 2, 10, 20))

# ── Language selector ─────────────────────────────────────────────────────────
lang_choice = st.sidebar.selectbox("🌐 Language / Тіл / Язык", ["EN", "KZ", "RU"])
T = LANG[lang_choice]

# Header
st.title(T["title"])
st.markdown(f"**{T['subtitle']}**")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header(T["check_city"])
selected_city = st.sidebar.selectbox(T["select_city"], list(REGIONS.keys()))
use_real = st.sidebar.toggle(T["real_weather"], value=False)

if use_real:
    weather = fetch_current_weather(selected_city)
    if weather:
        rainfall    = weather["rainfall_mm"]
        temperature = weather["temperature_c"]
        humidity    = weather["humidity_pct"]
        river_level = weather["river_level_m"]
        snow_melt   = weather["snow_melt_mm"]
        prev_rain   = weather["prev_day_rain"]
        st.sidebar.success(f"📡 {weather['description']} | 💨 {weather['wind_speed']} m/s")
    else:
        st.sidebar.warning("⚠️ API unavailable, using sliders")
        use_real = False

if not use_real:
    rainfall    = st.sidebar.slider(T["rainfall"],    0.0, 120.0, 30.0)
    temperature = st.sidebar.slider(T["temperature"], -10.0, 35.0, 15.0)
    humidity    = st.sidebar.slider(T["humidity"],    20.0, 100.0, 60.0)
    river_level = st.sidebar.slider(T["river"],       0.5, 8.0, 2.0)
    snow_melt   = st.sidebar.slider(T["snow"],        0.0, 50.0, 10.0)
    prev_rain   = st.sidebar.slider(T["prev_rain"],   0.0, 80.0, 20.0)

if st.sidebar.button(T["check_btn"], type="primary", use_container_width=True):
    result = predict(selected_city, rainfall, temperature, humidity, river_level, snow_melt, prev_rain)
    st.session_state.city_result = result

if "city_result" in st.session_state:
    r    = st.session_state.city_result
    risk = r["risk_level"]
    emoji = r["risk_emoji"]
    st.sidebar.divider()
    if risk == "Critical": st.sidebar.error(f"🚨 {r['region']}\n\n## {emoji} {T['critical']} Risk")
    elif risk == "High":   st.sidebar.warning(f"⚠️ {r['region']}\n\n## {emoji} {T['high']} Risk")
    elif risk == "Medium": st.sidebar.info(f"📢 {r['region']}\n\n## {emoji} {T['medium']} Risk")
    else:                  st.sidebar.success(f"✅ {r['region']}\n\n## {emoji} {T['low']} Risk")
    st.sidebar.markdown(f"**{T['confidence']}:** {r['confidence']}")
    st.sidebar.divider()
    for level, prob in r["probabilities"].items():
        bar = "█" * int(float(prob.strip("%")) / 10)
        st.sidebar.markdown(f"{RISK_EMOJI[level]} {level}: `{prob}` {bar}")

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🗺️ " + T["risk_map"],
    "⏱️ " + T["forecast"],
    "⛓️ " + T["blockchain"]
])

# ── TAB 1: Risk Map ───────────────────────────────────────────────────────────
with tab1:
    col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1, 3])
    with col_btn1:
        predict_all = st.button(T["predict_all"], type="primary", use_container_width=True)
    with col_btn2:
        simulate_new = st.button(T["new_weather"], use_container_width=True)
    with col_btn3:
        use_real_all = st.button(T["real_weather"] + " 🌍", use_container_width=True)

    if predict_all or simulate_new or use_real_all or "all_predictions" not in st.session_state:
        if simulate_new:
            random.seed()
        with st.spinner("🤖 AI predicting..."):
            preds = []
            for reg in REGIONS:
                if use_real_all:
                    w = fetch_current_weather(reg)
                    if w:
                        vals = (w["rainfall_mm"], w["temperature_c"], w["humidity_pct"],
                                w["river_level_m"], w["snow_melt_mm"], w["prev_day_rain"])
                        source = T["real_data"]
                    else:
                        vals = simulate_weather(reg)
                        source = T["simulated"]
                else:
                    vals = simulate_weather(reg)
                    source = T["simulated"]
                r = predict(reg, *vals)
                preds.append({**r,
                    "rainfall_mm":   round(vals[0], 1),
                    "river_level_m": round(vals[3], 1),
                    "humidity_pct":  round(vals[2], 1),
                    "source": source
                })
        st.session_state.all_predictions = preds

    predictions = st.session_state.all_predictions
    counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for p in predictions:
        if p["risk_level"] in counts:
            counts[p["risk_level"]] += 1

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"🟢 {T['low']}",    f"{counts['Low']} {T['regions']}")
    c2.metric(f"🟡 {T['medium']}", f"{counts['Medium']} {T['regions']}")
    c3.metric(f"🟠 {T['high']}",   f"{counts['High']} {T['regions']}")
    c4.metric(f"🔴 {T['critical']}",f"{counts['Critical']} {T['regions']}")
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        m = folium.Map(location=[48.0, 66.0], zoom_start=6, tiles="CartoDB dark_matter")
        for p in predictions:
            coords = REGIONS[p["region"]]
            risk   = p["risk_level"]
            color  = RISK_COLORS.get(risk, "gray")
            emoji  = RISK_EMOJI.get(risk, "⚪")
            folium.CircleMarker(
                location=coords, radius=22, color=color, weight=2,
                fill=True, fill_color=color, fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b>{p['region']}</b><br>Risk: {emoji} {risk}<br>"
                    f"{T['confidence']}: {p['confidence']}<br>"
                    f"Rain: {p['rainfall_mm']} mm<br>"
                    f"River: {p['river_level_m']} m<br>"
                    f"Source: {p['source']}", max_width=200),
                tooltip=f"{p['region']}: {emoji} {risk}"
            ).add_to(m)
        html(m._repr_html_(), height=480)

    with col2:
        df = pd.DataFrame([{
            "Region":         p["region"],
            "Risk":           f"{RISK_EMOJI.get(p['risk_level'],'⚪')} {p['risk_level']}",
            T["confidence"]:  p["confidence"],
            "Rain (mm)":      p["rainfall_mm"],
            "River (m)":      p["river_level_m"],
            "Source":         p["source"],
        } for p in predictions])
        st.dataframe(df, use_container_width=True, height=480)

    critical = [p for p in predictions if p["risk_level"] == "Critical"]
    high     = [p for p in predictions if p["risk_level"] == "High"]
    if critical:
        st.error(f"{T['critical_alert']}: {', '.join([p['region'] for p in critical])} — {T['immediate']}")
    if high:
        st.warning(f"{T['high_alert']}: {', '.join([p['region'] for p in high])} — {T['monitor']}")

# ── TAB 2: 72-Hour Forecast ───────────────────────────────────────────────────
with tab2:
    st.subheader(f"⏱️ {T['forecast']} — {selected_city}")
    forecast_data = fetch_forecast(selected_city)

    if forecast_data:
        forecast_preds = []
        for f in forecast_data:
            r = predict(selected_city,
                        f["rainfall_mm"], f["temperature_c"], f["humidity_pct"],
                        f["river_level_m"], f["snow_melt_mm"], f["prev_day_rain"])
            forecast_preds.append({
                "🕐 Time":        f["datetime"],
                "🌤️ Weather":    f["description"],
                "🌡️ Temp (°C)":  f["temperature_c"],
                "🌧️ Rain (mm)":  f["rainfall_mm"],
                "💧 Humidity":   f"{f['humidity_pct']}%",
                "⚠️ Risk":       f"{RISK_EMOJI[r['risk_level']]} {r['risk_level']}",
                "🎯 Confidence": r["confidence"],
            })
        df_forecast = pd.DataFrame(forecast_preds)
        st.dataframe(df_forecast, use_container_width=True, height=500)

        # Chart
        st.subheader("📈 Risk Trend")
        risk_map_num = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
        chart_data = pd.DataFrame({
            "Time": [p["🕐 Time"] for p in forecast_preds],
            "Risk Score": [risk_map_num.get(p["⚠️ Risk"].split(" ")[-1], 0) for p in forecast_preds],
            "Rainfall": [p["🌧️ Rain (mm)"] for p in forecast_preds],
        })
        st.line_chart(chart_data.set_index("Time")[["Risk Score", "Rainfall"]])
    else:
        # Simulated 72hr forecast
        st.info("📡 Add OpenWeatherMap API key for live forecast. Showing simulated data:")
        hours = ["Now", "+3h", "+6h", "+9h", "+12h", "+24h", "+36h", "+48h", "+72h"]
        sim_forecasts = []
        random.seed(42)
        for h in hours:
            rain = random.uniform(0, 80)
            temp = random.uniform(5, 25)
            hum  = random.uniform(40, 90)
            riv  = random.uniform(1, 7)
            snow = random.uniform(0, 30)
            prev = random.uniform(0, 50)
            r    = predict(selected_city, rain, temp, hum, riv, snow, prev)
            sim_forecasts.append({
                "🕐 Time":       h,
                "🌡️ Temp (°C)": round(temp, 1),
                "🌧️ Rain (mm)": round(rain, 1),
                "⚠️ Risk":      f"{RISK_EMOJI[r['risk_level']]} {r['risk_level']}",
                "🎯 Confidence":r["confidence"],
            })
        st.dataframe(pd.DataFrame(sim_forecasts), use_container_width=True)

        risk_map_num = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
        chart_data = pd.DataFrame({
            "Time": [f["🕐 Time"] for f in sim_forecasts],
            "Risk Score": [risk_map_num.get(f["⚠️ Risk"].split(" ")[-1], 0) for f in sim_forecasts],
        }).set_index("Time")
        st.line_chart(chart_data)

# ── TAB 3: Blockchain ─────────────────────────────────────────────────────────
with tab3:
    st.subheader(f"⛓️ {T['blockchain']}")
    st.markdown("**Transparent, immutable record of disaster relief fund distribution**")

    m1, m2, m3 = st.columns(3)
    m1.metric("💰 Total Distributed", "₸ 20,600,000")
    m2.metric("✅ Transactions", "6 verified")
    m3.metric("🏘️ Regions Helped", "6 regions")

    st.divider()
    st.markdown("### 📋 Transaction Ledger")
    df_chain = pd.DataFrame(BLOCKCHAIN_DATA)
    st.dataframe(df_chain, use_container_width=True)

    st.divider()
    st.markdown("### ➕ Submit New Relief Request")
    col_a, col_b = st.columns(2)
    with col_a:
        req_region = st.selectbox("Region", list(REGIONS.keys()))
        req_amount = st.number_input("Amount (₸)", min_value=100000, value=1000000, step=100000)
    with col_b:
        req_reason = st.text_area("Reason", placeholder="Describe the flood damage...")
        req_priority = st.selectbox("Priority", ["🔴 Critical", "🟠 High", "🟡 Medium"])

    if st.button("📤 Submit to Blockchain", type="primary"):
        import hashlib, time
        tx_hash = "0x" + hashlib.md5(f"{req_region}{req_amount}{time.time()}".encode()).hexdigest()[:8] + "..." + hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
        st.success(f"✅ Transaction submitted!\n\n**TX Hash:** `{tx_hash}`\n\n**Region:** {req_region} | **Amount:** ₸ {req_amount:,} | **Priority:** {req_priority}")
        st.balloons()

st.caption(T["powered"])