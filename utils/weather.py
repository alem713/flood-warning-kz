from datetime import datetime, timedelta, timezone
import math
import os

import requests
import streamlit as st

CITY_IDS = {
    "Almaty": 1526384,
    "Astana": 1526273,
    "Shymkent": 1519422,
    "Karaganda": 1522874,
    "Aktobe": 1526792,
    "Pavlodar": 1520240,
    "Semey": 1516589,
    "Taraz": 1517060,
    "Oskemen": 1516905,
    "Atyrau": 1526818,
    "Kostanay": 1522798,
    "Kyzylorda": 1520127,
    "Aktau": 1526825,
    "Petropavl": 1520458,
    "Taldykorgan": 1516481,
}

REGION_PROFILES = {
    "Almaty": {"rainfall_mm": 38, "temperature_c": 14, "humidity_pct": 68, "river_level_m": 2.6, "snow_melt_mm": 12},
    "Astana": {"rainfall_mm": 16, "temperature_c": 8, "humidity_pct": 58, "river_level_m": 1.8, "snow_melt_mm": 9},
    "Shymkent": {"rainfall_mm": 24, "temperature_c": 20, "humidity_pct": 56, "river_level_m": 2.1, "snow_melt_mm": 7},
    "Karaganda": {"rainfall_mm": 18, "temperature_c": 10, "humidity_pct": 54, "river_level_m": 1.7, "snow_melt_mm": 8},
    "Aktobe": {"rainfall_mm": 20, "temperature_c": 13, "humidity_pct": 55, "river_level_m": 1.9, "snow_melt_mm": 6},
    "Pavlodar": {"rainfall_mm": 44, "temperature_c": 9, "humidity_pct": 72, "river_level_m": 3.8, "snow_melt_mm": 18},
    "Semey": {"rainfall_mm": 22, "temperature_c": 11, "humidity_pct": 58, "river_level_m": 2.0, "snow_melt_mm": 7},
    "Taraz": {"rainfall_mm": 28, "temperature_c": 19, "humidity_pct": 61, "river_level_m": 2.3, "snow_melt_mm": 8},
    "Oskemen": {"rainfall_mm": 50, "temperature_c": 8, "humidity_pct": 74, "river_level_m": 4.2, "snow_melt_mm": 20},
    "Atyrau": {"rainfall_mm": 10, "temperature_c": 18, "humidity_pct": 47, "river_level_m": 1.3, "snow_melt_mm": 3},
    "Kostanay": {"rainfall_mm": 23, "temperature_c": 7, "humidity_pct": 60, "river_level_m": 2.2, "snow_melt_mm": 10},
    "Kyzylorda": {"rainfall_mm": 11, "temperature_c": 23, "humidity_pct": 44, "river_level_m": 1.4, "snow_melt_mm": 2},
    "Aktau": {"rainfall_mm": 6, "temperature_c": 24, "humidity_pct": 43, "river_level_m": 0.9, "snow_melt_mm": 1},
    "Petropavl": {"rainfall_mm": 27, "temperature_c": 6, "humidity_pct": 63, "river_level_m": 2.8, "snow_melt_mm": 12},
    "Taldykorgan": {"rainfall_mm": 34, "temperature_c": 15, "humidity_pct": 66, "river_level_m": 2.7, "snow_melt_mm": 11},
}

DEFAULT_PROFILE = {"rainfall_mm": 20, "temperature_c": 14, "humidity_pct": 60, "river_level_m": 2.0, "snow_melt_mm": 8}


def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return os.getenv("OPENWEATHER_API_KEY", "")


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def _profile(region):
    return REGION_PROFILES.get(region, DEFAULT_PROFILE)


def _phase(region, hour_offset=0):
    now = datetime.now(timezone.utc)
    day_seed = now.timetuple().tm_yday + hour_offset / 24.0
    region_bias = (sum(ord(char) for char in region) % 17) / 17.0
    return (day_seed / 365.0) * (2 * math.pi) + region_bias * math.pi


def build_estimated_weather(region):
    profile = _profile(region)
    phase = _phase(region)
    rainfall = _clamp(profile["rainfall_mm"] + 14 * math.sin(phase) + 6 * math.cos(phase * 1.7), 0.0, 120.0)
    temperature = _clamp(profile["temperature_c"] + 6 * math.sin(phase + 1.2), -10.0, 35.0)
    humidity = _clamp(profile["humidity_pct"] + 9 * math.sin(phase + 0.4), 20.0, 100.0)
    river_level = _clamp(profile["river_level_m"] + 0.7 * math.sin(phase + 2.0), 0.5, 8.0)
    snow_melt = _clamp(profile["snow_melt_mm"] + 4 * math.cos(phase + 0.8), 0.0, 50.0)
    prev_day_rain = _clamp(rainfall * 0.65, 0.0, 80.0)

    return {
        "rainfall_mm": round(rainfall, 1),
        "temperature_c": round(temperature, 1),
        "humidity_pct": round(humidity, 1),
        "river_level_m": round(river_level, 1),
        "snow_melt_mm": round(snow_melt, 1),
        "prev_day_rain": round(prev_day_rain, 1),
        "description": "Estimated regional conditions",
        "wind_speed": round(2.0 + abs(math.sin(phase)) * 4, 1),
        "source": "estimated",
    }


def build_estimated_forecast(region):
    forecast = []
    start = datetime.now(timezone.utc)
    for step in range(24):
        hour_offset = step * 3
        profile = _profile(region)
        phase = _phase(region, hour_offset)
        rainfall = _clamp(profile["rainfall_mm"] + 16 * math.sin(phase) + 7 * math.cos(phase * 1.4), 0.0, 120.0)
        temperature = _clamp(profile["temperature_c"] + 7 * math.sin(phase + 1.0), -10.0, 35.0)
        humidity = _clamp(profile["humidity_pct"] + 10 * math.sin(phase + 0.5), 20.0, 100.0)
        river_level = _clamp(profile["river_level_m"] + 0.8 * math.sin(phase + 1.7), 0.5, 8.0)
        snow_melt = _clamp(profile["snow_melt_mm"] + 5 * math.cos(phase + 0.6), 0.0, 50.0)
        prev_day_rain = _clamp(rainfall * 0.6, 0.0, 80.0)
        forecast.append(
            {
                "datetime": (start + timedelta(hours=hour_offset)).strftime("%Y-%m-%d %H:%M"),
                "rainfall_mm": round(rainfall, 1),
                "temperature_c": round(temperature, 1),
                "humidity_pct": round(humidity, 1),
                "river_level_m": round(river_level, 1),
                "snow_melt_mm": round(snow_melt, 1),
                "prev_day_rain": round(prev_day_rain, 1),
                "description": "Estimated forecast",
                "source": "estimated",
            }
        )
    return forecast


def fetch_current_weather(region):
    api_key = get_api_key()
    city_id = CITY_IDS.get(region)
    if not api_key or not city_id:
        return None
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            "rainfall_mm": data.get("rain", {}).get("1h", 0.0),
            "temperature_c": data["main"]["temp"],
            "humidity_pct": data["main"]["humidity"],
            "river_level_m": 2.5,
            "snow_melt_mm": data.get("snow", {}).get("1h", 0.0),
            "prev_day_rain": data.get("rain", {}).get("1h", 0.0),
            "description": data["weather"][0]["description"].title(),
            "wind_speed": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"],
            "source": "live",
        }
    except Exception:
        return None


def fetch_forecast(region):
    api_key = get_api_key()
    city_id = CITY_IDS.get(region)
    if not api_key or not city_id:
        return None
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={api_key}&units=metric&cnt=24"
        response = requests.get(url, timeout=5)
        data = response.json()
        forecasts = []
        for item in data["list"]:
            forecasts.append(
                {
                    "datetime": item["dt_txt"],
                    "rainfall_mm": item.get("rain", {}).get("3h", 0.0),
                    "temperature_c": item["main"]["temp"],
                    "humidity_pct": item["main"]["humidity"],
                    "river_level_m": 2.5,
                    "snow_melt_mm": item.get("snow", {}).get("3h", 0.0),
                    "prev_day_rain": item.get("rain", {}).get("3h", 0.0),
                    "description": item["weather"][0]["description"].title(),
                    "source": "live",
                }
            )
        return forecasts
    except Exception:
        return None
