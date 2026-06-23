import os
import sys

import folium
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.model import RISK_COLORS, predict_risk
from utils.weather import build_estimated_weather, fetch_current_weather


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
        .hero-card {
            background: linear-gradient(135deg, rgba(40, 90, 160, 0.18), rgba(12, 18, 28, 0.85));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .hero-subtitle {
            color: rgba(255,255,255,0.72);
            font-size: 1rem;
        }
        .hint-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.75rem;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 650;
            margin-bottom: 0.35rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


LANG = {
    "EN": {
        "title": "Flood Monitor — Kazakhstan",
        "subtitle": "A simple flood warning screen with automatic risk results.",
        "language": "Language",
        "quick_start": "Quick start",
        "step_1": "Pick your language.",
        "step_2": "Read the risk status shown on the page.",
        "step_3": "If the alert is High or Critical, check the top regions below.",
        "overall": "Overall risk",
        "attention": "Regions needing attention",
        "source": "Data source",
        "confidence": "Average confidence",
        "live": "Live weather",
        "estimated": "Estimated weather",
        "no_risk": "No major flood risk detected right now.",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
        "high_alert": "High risk detected",
        "critical_alert": "Critical risk detected",
        "monitor": "Please monitor these regions closely.",
        "immediate": "Immediate action is recommended.",
        "top_regions": "Top risk regions",
        "map_title": "Risk map",
        "how_to_read": "How to read this screen",
        "how_to_read_text": "Green means low risk. Orange means medium. Red means high. Dark red means critical.",
        "source_note": "Live data is used first. If it is unavailable, the app shows a stable estimated fallback.",
        "results_note": "This page updates automatically from weather data.",
        "risk_region": "Risk region",
        "risk_level": "Risk level",
        "rainfall": "Rainfall",
        "river": "River",
        "weather_source": "Weather source",
    },
    "KZ": {
        "title": "Су тасқыны мониторы — Қазақстан",
        "subtitle": "Қауіпті автоматты түрде көрсететін қарапайым экран.",
        "language": "Тіл",
        "quick_start": "Жылдам бастау",
        "step_1": "Тілді таңдаңыз.",
        "step_2": "Беттегі қауіп күйін оқыңыз.",
        "step_3": "Егер ескерту Жоғары немесе Қауіпті болса, төмендегі өңірлерді қараңыз.",
        "overall": "Жалпы қауіп",
        "attention": "Назар қажет өңірлер",
        "source": "Дерек көзі",
        "confidence": "Орташа сенімділік",
        "live": "Тікелей ауа райы",
        "estimated": "Бағаланған ауа райы",
        "no_risk": "Қазір айқын су тасқыны қаупі байқалмайды.",
        "low": "Төмен",
        "medium": "Орташа",
        "high": "Жоғары",
        "critical": "Қауіпті",
        "high_alert": "Жоғары қауіп анықталды",
        "critical_alert": "Қауіпті жағдай анықталды",
        "monitor": "Бұл өңірлерді мұқият бақылаңыз.",
        "immediate": "Дереу шара қабылдау ұсынылады.",
        "top_regions": "Ең қауіпті өңірлер",
        "map_title": "Қауіп картасы",
        "how_to_read": "Экранды қалай оқу керек",
        "how_to_read_text": "Жасыл — төмен қауіп. Қызғылт сары — орташа. Қызыл — жоғары. Қою қызыл — қауіпті.",
        "source_note": "Алдымен тікелей дерек қолданылады. Қолжетімсіз болса, тұрақты бағаланған дерек көрсетіледі.",
        "results_note": "Бұл бет ауа райы дерегімен автоматты түрде жаңарады.",
        "risk_region": "Өңір",
        "risk_level": "Қауіп деңгейі",
        "rainfall": "Жауын-шашын",
        "river": "Өзен",
        "weather_source": "Ауа райы көзі",
    },
    "RU": {
        "title": "Монитор паводков — Казахстан",
        "subtitle": "Простой экран с автоматическим показом риска.",
        "language": "Язык",
        "quick_start": "Быстрый старт",
        "step_1": "Выберите язык.",
        "step_2": "Посмотрите статус риска на странице.",
        "step_3": "Если предупреждение Высокое или Критическое, проверьте список регионов ниже.",
        "overall": "Общий риск",
        "attention": "Регионы, требующие внимания",
        "source": "Источник данных",
        "confidence": "Средняя уверенность",
        "live": "Живая погода",
        "estimated": "Оценочная погода",
        "no_risk": "Сейчас серьёзного паводкового риска не обнаружено.",
        "low": "Низкий",
        "medium": "Средний",
        "high": "Высокий",
        "critical": "Критический",
        "high_alert": "Обнаружен высокий риск",
        "critical_alert": "Обнаружен критический риск",
        "monitor": "Пожалуйста, следите за этими регионами.",
        "immediate": "Рекомендуются немедленные действия.",
        "top_regions": "Самые рискованные регионы",
        "map_title": "Карта риска",
        "how_to_read": "Как читать экран",
        "how_to_read_text": "Зелёный — низкий риск. Оранжевый — средний. Красный — высокий. Тёмно-красный — критический.",
        "source_note": "Сначала используется живая погода. Если она недоступна, показывается стабильная оценка.",
        "results_note": "Страница обновляется автоматически по погодным данным.",
        "risk_region": "Регион",
        "risk_level": "Уровень риска",
        "rainfall": "Осадки",
        "river": "Река",
        "weather_source": "Источник погоды",
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


def get_weather(region):
    live = fetch_current_weather(region)
    if live:
        return live
    return build_estimated_weather(region)


def risk_order(level):
    return {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}.get(level, 0)


def localized_risk(level, text):
    return {
        "Low": text["low"],
        "Medium": text["medium"],
        "High": text["high"],
        "Critical": text["critical"],
    }.get(level, level)


language_choices = [("English", "EN"), ("Қазақша", "KZ"), ("Русский", "RU")]
selected_language_name = st.sidebar.selectbox(
    "Language", [label for label, _ in language_choices]
)
lang_choice = next(code for label, code in language_choices if label == selected_language_name)
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

hint_1, hint_2, hint_3 = st.columns(3)
for column, step, text in [
    (hint_1, "1", T["step_1"]),
    (hint_2, "2", T["step_2"]),
    (hint_3, "3", T["step_3"]),
]:
    with column:
        st.markdown(
            f"<div class='hint-card'><div class='section-title'>{T['quick_start']} {step}</div><div>{text}</div></div>",
            unsafe_allow_html=True,
        )

snapshots = []
for region in REGIONS:
    weather = get_weather(region)
    result = predict_risk(
        region,
        weather["rainfall_mm"],
        weather["temperature_c"],
        weather["humidity_pct"],
        weather["river_level_m"],
        weather["snow_melt_mm"],
        weather["prev_day_rain"],
    )
    snapshots.append(
        {
            **result,
            "rainfall_mm": round(weather["rainfall_mm"], 1),
            "river_level_m": round(weather["river_level_m"], 1),
            "humidity_pct": round(weather["humidity_pct"], 1),
            "source": T["live"] if weather.get("source") == "live" else T["estimated"],
        }
    )

worst = max(snapshots, key=lambda item: risk_order(item["risk_level"]))
attention = [item for item in snapshots if item["risk_level"] in {"High", "Critical"}]
live_count = sum(1 for item in snapshots if item["source"] == T["live"])
avg_confidence = sum(float(item["confidence"].strip("%")) for item in snapshots) / len(snapshots)

summary_a, summary_b, summary_c, summary_d = st.columns(4)
summary_a.metric(T["overall"], localized_risk(worst["risk_level"], T))
summary_b.metric(T["attention"], f"{len(attention)} {T['top_regions'].lower()}")
summary_c.metric(T["source"], f"{live_count} / {len(snapshots)}")
summary_d.metric(T["confidence"], f"{avg_confidence:.1f}%")
st.caption(T["source_note"])
st.caption(T["results_note"])
st.divider()

localized_attention = ", ".join(item["region"] for item in attention[:5])
if worst["risk_level"] == "Critical":
    st.error(
        f"{T['critical_alert']}: {localized_risk(worst['risk_level'], T)} — {localized_attention} — {T['immediate']}"
    )
elif worst["risk_level"] == "High":
    st.warning(
        f"{T['high_alert']}: {localized_risk(worst['risk_level'], T)} — {localized_attention} — {T['monitor']}"
    )
elif worst["risk_level"] == "Medium":
    st.info(T["no_risk"])
else:
    st.success(T["no_risk"])

st.markdown(f"### {T['top_regions']}")
top_rows = pd.DataFrame(
        [
            {
                T["risk_region"]: item["region"],
                T["risk_level"]: localized_risk(item["risk_level"], T),
                T["confidence"]: item["confidence"],
                T["rainfall"]: item["rainfall_mm"],
                T["river"]: item["river_level_m"],
                T["weather_source"]: item["source"],
            }
        for item in sorted(snapshots, key=lambda item: risk_order(item["risk_level"]), reverse=True)[:5]
    ]
)
st.dataframe(top_rows, use_container_width=True, hide_index=True)

st.markdown(f"### {T['map_title']}")
map_view = folium.Map(location=[48.0, 66.0], zoom_start=6, tiles="CartoDB dark_matter")
for item in snapshots:
    coords = REGIONS[item["region"]]
    color = RISK_COLORS.get(item["risk_level"], "gray")
    folium.CircleMarker(
        location=coords,
        radius=18,
        color=color,
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        popup=folium.Popup(
            f"<b>{item['region']}</b><br>"
            f"{T['risk_level']}: {localized_risk(item['risk_level'], T)}<br>"
            f"{T['confidence']}: {item['confidence']}<br>"
            f"{T['rainfall']}: {item['rainfall_mm']} mm<br>"
            f"{T['river']}: {item['river_level_m']} m<br>"
            f"{T['weather_source']}: {item['source']}",
            max_width=220,
        ),
        tooltip=f"{item['region']}: {localized_risk(item['risk_level'], T)}",
    ).add_to(map_view)

html(map_view._repr_html_(), height=500)

with st.expander(T["how_to_read"], expanded=False):
    st.write(T["how_to_read_text"])

st.caption("Powered by XGBoost ML | 84% Accuracy")
