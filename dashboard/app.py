import os
import sys

import folium
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.model import RISK_COLORS, predict_risk
from utils.weather import (
    build_estimated_forecast,
    build_estimated_weather,
    fetch_current_weather,
    fetch_forecast,
)


st.set_page_config(
    page_title="Flood Monitor KZ",
    page_icon="FM",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 1.75rem;
        }
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1rem;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        [data-testid="stTabs"] button {
            border-radius: 999px;
        }
        .stButton > button {
            border-radius: 12px;
            height: 2.6rem;
        }
        section[data-testid="stSidebar"] {
            background: #0b0f14;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(40, 90, 160, 0.18), rgba(12, 18, 28, 0.85));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2.05rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .hero-subtitle {
            color: rgba(255,255,255,0.72);
            font-size: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


LANG = {
    "EN": {
        "title": "Flood Monitor — Kazakhstan",
        "subtitle": "Live-weather flood risk assessment for all major regions",
        "check_city": "Check a City",
        "select_city": "Select City",
        "rainfall": "Rainfall (mm)",
        "temperature": "Temperature (°C)",
        "humidity": "Humidity (%)",
        "river": "River Level (m)",
        "snow": "Snow Melt (mm)",
        "prev_rain": "Recent Rain (mm)",
        "check_btn": "Check City",
        "predict_all": "Refresh Live Data",
        "new_weather": "Rebuild Estimates",
        "real_weather": "Use Live Weather",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
        "regions": "regions",
        "confidence": "Confidence",
        "risk_map": "Kazakhstan Risk Map",
        "forecast": "72-Hour Forecast",
        "blockchain": "Relief Tracker",
        "critical_alert": "Critical alert",
        "high_alert": "High risk",
        "immediate": "Immediate action required!",
        "monitor": "Monitor closely!",
        "powered": "Powered by XGBoost ML | 84% Accuracy | Decentrathon 5.0",
        "real_data": "Live weather",
        "simulated": "Estimated weather",
    },
    "KZ": {
        "title": "Су тасқынын бақылау — Қазақстан",
        "subtitle": "Нақты ауа райы деректеріне негізделген қауіп бағалау",
        "check_city": "Қаланы тексеру",
        "select_city": "Қала таңдау",
        "rainfall": "Жауын-шашын (мм)",
        "temperature": "Температура (°C)",
        "humidity": "Ылғалдылық (%)",
        "river": "Өзен деңгейі (м)",
        "snow": "Қар ерігені (мм)",
        "prev_rain": "Соңғы жауын (мм)",
        "check_btn": "Қаланы тексеру",
        "predict_all": "Тікелей деректерді жаңарту",
        "new_weather": "Бағалауды қайта құру",
        "real_weather": "Тікелей ауа райы",
        "low": "Төмен",
        "medium": "Орташа",
        "high": "Жоғары",
        "critical": "Қауіпті",
        "regions": "өңір",
        "confidence": "Сенімділік",
        "risk_map": "Қазақстан қауіп картасы",
        "forecast": "72 сағаттық болжам",
        "blockchain": "Көмек трекері",
        "critical_alert": "Қауіпті ескерту",
        "high_alert": "Жоғары қауіп",
        "immediate": "Дереу шара қолдану қажет!",
        "monitor": "Мұқият бақылаңыз!",
        "powered": "XGBoost ML | 84% дәлдік | Decentrathon 5.0",
        "real_data": "Тікелей деректер",
        "simulated": "Бағаланған деректер",
    },
    "RU": {
        "title": "Монитор паводков — Казахстан",
        "subtitle": "Оценка риска на основе реальных погодных данных",
        "check_city": "Проверить город",
        "select_city": "Выбрать город",
        "rainfall": "Осадки (мм)",
        "temperature": "Температура (°C)",
        "humidity": "Влажность (%)",
        "river": "Уровень реки (м)",
        "snow": "Таяние снега (мм)",
        "prev_rain": "Последний дождь (мм)",
        "check_btn": "Проверить город",
        "predict_all": "Обновить живые данные",
        "new_weather": "Пересобрать оценки",
        "real_weather": "Живая погода",
        "low": "Низкий",
        "medium": "Средний",
        "high": "Высокий",
        "critical": "Критический",
        "regions": "регионов",
        "confidence": "Уверенность",
        "risk_map": "Карта рисков Казахстана",
        "forecast": "Прогноз на 72 часа",
        "blockchain": "Трекер помощи",
        "critical_alert": "Критическое предупреждение",
        "high_alert": "Высокий риск",
        "immediate": "Требуются немедленные действия!",
        "monitor": "Следите внимательно!",
        "powered": "XGBoost ML | Точность 84% | Decentrathon 5.0",
        "real_data": "Живые данные",
        "simulated": "Оценочные данные",
    },
}


REGIONS = {
    "Almaty": (43.2220, 76.8512),
    "Astana": (51.1801, 71.4460),
    "Shymkent": (42.3000, 69.6000),
    "Karaganda": (49.8047, 73.1094),
    "Aktobe": (50.2839, 57.1670),
    "Pavlodar": (52.2873, 76.9674),
    "Semey": (50.4111, 80.2275),
    "Taraz": (42.9000, 71.3667),
    "Oskemen": (49.9483, 82.6283),
    "Atyrau": (47.1167, 51.8833),
    "Kostanay": (53.2144, 63.6249),
    "Kyzylorda": (44.8488, 65.5092),
    "Aktau": (43.6500, 51.1667),
    "Petropavl": (54.8647, 69.1536),
    "Taldykorgan": (45.0153, 78.3729),
}

RELIEF_DATA = [
    {"tx": "0x3f9a...d12e", "region": "Pavlodar", "amount": "₸ 5,000,000", "status": "Delivered", "date": "2024-04-15"},
    {"tx": "0x7b2c...a89f", "region": "Oskemen", "amount": "₸ 3,200,000", "status": "Delivered", "date": "2024-04-16"},
    {"tx": "0x1d4e...c34a", "region": "Karaganda", "amount": "₸ 2,800,000", "status": "In transit", "date": "2024-04-17"},
    {"tx": "0x9e1b...f56d", "region": "Kostanay", "amount": "₸ 4,100,000", "status": "Delivered", "date": "2024-04-18"},
    {"tx": "0x5c8d...b23c", "region": "Atyrau", "amount": "₸ 1,900,000", "status": "Pending", "date": "2024-04-19"},
    {"tx": "0x2a7f...e78b", "region": "Petropavl", "amount": "₸ 3,600,000", "status": "In transit", "date": "2024-04-20"},
]


def get_weather_snapshot(region, prefer_live=True):
    if prefer_live:
        live = fetch_current_weather(region)
        if live:
            return live
    return build_estimated_weather(region)


def get_forecast_snapshot(region):
    forecast = fetch_forecast(region)
    if forecast:
        return forecast, "live"
    return build_estimated_forecast(region), "estimated"


lang_choice = st.sidebar.selectbox("Language / Тіл / Язык", ["EN", "KZ", "RU"])
T = LANG[lang_choice]

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">{T["title"]}</div>
        <div class="hero-subtitle">{T["subtitle"]}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header(T["check_city"])
selected_city = st.sidebar.selectbox(T["select_city"], list(REGIONS.keys()))
prefer_live = st.sidebar.toggle(T["real_weather"], value=True)

weather = get_weather_snapshot(selected_city, prefer_live=prefer_live)

st.sidebar.caption(f"{T['real_data'] if weather['source'] == 'live' else T['simulated']}: {weather['description']}")
if "wind_speed" in weather:
    st.sidebar.caption(f"Wind: {weather['wind_speed']} m/s")

rainfall = st.sidebar.slider(T["rainfall"], 0.0, 120.0, float(weather["rainfall_mm"]))
temperature = st.sidebar.slider(T["temperature"], -10.0, 35.0, float(weather["temperature_c"]))
humidity = st.sidebar.slider(T["humidity"], 20.0, 100.0, float(weather["humidity_pct"]))
river_level = st.sidebar.slider(T["river"], 0.5, 8.0, float(weather["river_level_m"]))
snow_melt = st.sidebar.slider(T["snow"], 0.0, 50.0, float(weather["snow_melt_mm"]))
prev_rain = st.sidebar.slider(T["prev_rain"], 0.0, 80.0, float(weather["prev_day_rain"]))

if st.sidebar.button(T["check_btn"], type="primary", use_container_width=True):
    st.session_state.city_result = predict_risk(
        selected_city,
        rainfall,
        temperature,
        humidity,
        river_level,
        snow_melt,
        prev_rain,
    )

if "city_result" in st.session_state:
    result = st.session_state.city_result
    st.sidebar.divider()
    if result["risk_level"] == "Critical":
        st.sidebar.error(f"{result['region']}\n\n{T['critical']} risk")
    elif result["risk_level"] == "High":
        st.sidebar.warning(f"{result['region']}\n\n{T['high']} risk")
    elif result["risk_level"] == "Medium":
        st.sidebar.info(f"{result['region']}\n\n{T['medium']} risk")
    else:
        st.sidebar.success(f"{result['region']}\n\n{T['low']} risk")
    st.sidebar.markdown(f"**{T['confidence']}:** {result['confidence']}")
    for level, prob in result["probabilities"].items():
        bar = "█" * int(float(prob.strip("%")) / 10)
        st.sidebar.markdown(f"{level}: `{prob}` {bar}")

preview = predict_risk(selected_city, rainfall, temperature, humidity, river_level, snow_melt, prev_rain)
summary_a, summary_b, summary_c, summary_d = st.columns(4)
summary_a.metric("City", selected_city)
summary_b.metric("Weather source", T["real_data"] if weather["source"] == "live" else T["simulated"])
summary_c.metric("Current risk", preview["risk_level"])
summary_d.metric("Confidence", preview["confidence"])
st.divider()

tab1, tab2, tab3 = st.tabs([T["risk_map"], T["forecast"], T["blockchain"]])

with tab1:
    mode_col_1, mode_col_2, mode_col_3, _ = st.columns([1, 1, 1, 3])
    if "map_mode" not in st.session_state:
        st.session_state.map_mode = "live" if prefer_live else "estimated"

    with mode_col_1:
        if st.button(T["predict_all"], type="primary", use_container_width=True):
            st.session_state.map_mode = "live"
    with mode_col_2:
        if st.button(T["new_weather"], use_container_width=True):
            st.session_state.map_mode = "estimated"
    with mode_col_3:
        if st.button("Use selected city source", use_container_width=True):
            st.session_state.map_mode = "live" if weather["source"] == "live" else "estimated"

    with st.spinner("Updating risk map..."):
        predictions = []
        for region in REGIONS:
            use_live = st.session_state.map_mode == "live"
            snapshot = get_weather_snapshot(region, prefer_live=use_live)
            values = (
                snapshot["rainfall_mm"],
                snapshot["temperature_c"],
                snapshot["humidity_pct"],
                snapshot["river_level_m"],
                snapshot["snow_melt_mm"],
                snapshot["prev_day_rain"],
            )
            result = predict_risk(region, *values)
            predictions.append(
                {
                    **result,
                    "rainfall_mm": round(values[0], 1),
                    "river_level_m": round(values[3], 1),
                    "humidity_pct": round(values[2], 1),
                    "source": T["real_data"] if snapshot["source"] == "live" else T["simulated"],
                }
            )

    counts = {level: 0 for level in ["Low", "Medium", "High", "Critical"]}
    for item in predictions:
        counts[item["risk_level"]] += 1

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["low"], f"{counts['Low']} {T['regions']}")
    c2.metric(T["medium"], f"{counts['Medium']} {T['regions']}")
    c3.metric(T["high"], f"{counts['High']} {T['regions']}")
    c4.metric(T["critical"], f"{counts['Critical']} {T['regions']}")
    st.divider()

    left, right = st.columns([2, 1])
    with left:
        map_view = folium.Map(location=[48.0, 66.0], zoom_start=6, tiles="CartoDB dark_matter")
        for item in predictions:
            coords = REGIONS[item["region"]]
            color = RISK_COLORS.get(item["risk_level"], "gray")
            folium.CircleMarker(
                location=coords,
                radius=22,
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=folium.Popup(
                    f"<b>{item['region']}</b><br>"
                    f"Risk: {item['risk_level']}<br>"
                    f"{T['confidence']}: {item['confidence']}<br>"
                    f"Rain: {item['rainfall_mm']} mm<br>"
                    f"River: {item['river_level_m']} m<br>"
                    f"Source: {item['source']}",
                    max_width=220,
                ),
                tooltip=f"{item['region']}: {item['risk_level']}",
            ).add_to(map_view)
        html(map_view._repr_html_(), height=480)

    with right:
        table = pd.DataFrame(
            [
                {
                    "Region": item["region"],
                    "Risk": item["risk_level"],
                    T["confidence"]: item["confidence"],
                    "Rain (mm)": item["rainfall_mm"],
                    "River (m)": item["river_level_m"],
                    "Source": item["source"],
                }
                for item in predictions
            ]
        )
        st.dataframe(table, use_container_width=True, height=480)

    critical = [item for item in predictions if item["risk_level"] == "Critical"]
    high = [item for item in predictions if item["risk_level"] == "High"]
    if critical:
        st.error(f"{T['critical_alert']}: {', '.join(item['region'] for item in critical)} — {T['immediate']}")
    if high:
        st.warning(f"{T['high_alert']}: {', '.join(item['region'] for item in high)} — {T['monitor']}")

with tab2:
    st.subheader(f"{T['forecast']} — {selected_city}")
    forecast_data, forecast_source = get_forecast_snapshot(selected_city)
    if forecast_source == "estimated":
        st.info("Live forecast is unavailable, so estimated regional data is shown instead.")

    forecast_rows = []
    for row in forecast_data:
        result = predict_risk(
            selected_city,
            row["rainfall_mm"],
            row["temperature_c"],
            row["humidity_pct"],
            row["river_level_m"],
            row["snow_melt_mm"],
            row["prev_day_rain"],
        )
        forecast_rows.append(
            {
                "Time": row["datetime"],
                "Weather": row["description"],
                "Temp (°C)": row["temperature_c"],
                "Rain (mm)": row["rainfall_mm"],
                "Humidity": f"{row['humidity_pct']}%",
                "Risk": result["risk_level"],
                "Confidence": result["confidence"],
                "Source": T["real_data"] if row.get("source") == "live" else T["simulated"],
            }
        )

    forecast_df = pd.DataFrame(forecast_rows)
    st.dataframe(forecast_df, use_container_width=True, height=500)

    risk_map_num = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    chart_data = pd.DataFrame(
        {
            "Time": [item["Time"] for item in forecast_rows],
            "Risk Score": [risk_map_num[item["Risk"]] for item in forecast_rows],
            "Rainfall": [item["Rain (mm)"] for item in forecast_rows],
        }
    )

    import plotly.express as px

    fig = px.line(
        chart_data,
        x="Time",
        y=["Risk Score", "Rainfall"],
        title="72-Hour Risk and Rainfall Trend",
        template="plotly_dark",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader(T["blockchain"])
    st.markdown("Transparent record of disaster relief fund distribution")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total distributed", "₸ 20,600,000")
    m2.metric("Transactions", "6 verified")
    m3.metric("Regions helped", "6 regions")

    st.divider()
    st.markdown("### Transaction ledger")
    st.dataframe(pd.DataFrame(RELIEF_DATA), use_container_width=True)

    st.divider()
    st.markdown("### Submit new relief request")
    col_a, col_b = st.columns(2)
    with col_a:
        req_region = st.selectbox("Region", list(REGIONS.keys()))
        req_amount = st.number_input("Amount (₸)", min_value=100000, value=1000000, step=100000)
    with col_b:
        req_reason = st.text_area("Reason", placeholder="Describe the flood damage...")
        req_priority = st.selectbox("Priority", ["Critical", "High", "Medium"])

    if st.button("Submit request", type="primary"):
        import hashlib
        import time

        tx_hash = "0x" + hashlib.md5(f"{req_region}{req_amount}{time.time()}".encode()).hexdigest()[:8] + "..." + hashlib.md5(str(time.time()).encode()).hexdigest()[:4]
        st.success(
            f"Transaction submitted.\n\nTX Hash: `{tx_hash}`\n\nRegion: {req_region} | Amount: ₸ {req_amount:,} | Priority: {req_priority}"
        )

st.caption(T["powered"])
