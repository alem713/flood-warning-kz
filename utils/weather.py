import requests
import os
import streamlit as st

# City name to OpenWeatherMap city ID mapping for KZ cities
CITY_IDS = {
    "Almaty":       1526384,
    "Astana":       1526273,
    "Shymkent":     1519422,
    "Karaganda":    1522874,
    "Aktobe":       1526792,
    "Pavlodar":     1520240,
    "Semey":        1516589,
    "Taraz":        1517060,
    "Oskemen":      1516905,
    "Atyrau":       1526818,
    "Kostanay":     1522798,
    "Kyzylorda":    1520127,
    "Aktau":        1526825,
    "Petropavl":    1520458,
    "Taldykorgan":  1516481,
}

def get_api_key():
    try:
        return st.secrets["OPENWEATHER_API_KEY"]
    except:
        return os.getenv("OPENWEATHER_API_KEY", "")

def fetch_current_weather(region):
    """Fetch current weather for a region."""
    api_key = get_api_key()
    city_id = CITY_IDS.get(region)
    if not api_key or not city_id:
        return None
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric"
        r = requests.get(url, timeout=5)
        data = r.json()
        return {
            "rainfall_mm":    data.get("rain", {}).get("1h", 0.0),
            "temperature_c":  data["main"]["temp"],
            "humidity_pct":   data["main"]["humidity"],
            "river_level_m":  2.5,  # No free river API — use default
            "snow_melt_mm":   data.get("snow", {}).get("1h", 0.0),
            "prev_day_rain":  data.get("rain", {}).get("3h", 0.0) / 3,
            "description":    data["weather"][0]["description"].title(),
            "wind_speed":     data["wind"]["speed"],
            "icon":           data["weather"][0]["icon"],
        }
    except:
        return None

def fetch_forecast(region):
    """Fetch 72-hour forecast (3-hour intervals) for a region."""
    api_key = get_api_key()
    city_id = CITY_IDS.get(region)
    if not api_key or not city_id:
        return None
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={api_key}&units=metric&cnt=24"
        r = requests.get(url, timeout=5)
        data = r.json()
        forecasts = []
        for item in data["list"]:
            forecasts.append({
                "datetime":      item["dt_txt"],
                "rainfall_mm":   item.get("rain", {}).get("3h", 0.0),
                "temperature_c": item["main"]["temp"],
                "humidity_pct":  item["main"]["humidity"],
                "river_level_m": 2.5,
                "snow_melt_mm":  item.get("snow", {}).get("3h", 0.0),
                "prev_day_rain": item.get("rain", {}).get("3h", 0.0),
                "description":   item["weather"][0]["description"].title(),
            })
        return forecasts
    except:
        return None