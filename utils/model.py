from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "model" / "flood_model.joblib"

FEATURE_COLUMNS = [
    "rainfall_mm",
    "temperature_c",
    "humidity_pct",
    "river_level_m",
    "snow_melt_mm",
    "prev_day_rain",
]

RISK_LABELS = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
RISK_EMOJI = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
RISK_COLORS = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "darkred"}


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing model artifact: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def predict_risk(
    region: str,
    rainfall_mm: float,
    temperature_c: float,
    humidity_pct: float,
    river_level_m: float,
    snow_melt_mm: float,
    prev_day_rain: float,
):
    features = np.array(
        [[rainfall_mm, temperature_c, humidity_pct, river_level_m, snow_melt_mm, prev_day_rain]],
        dtype=float,
    )
    model = load_model()
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    risk_level = RISK_LABELS[prediction]

    return {
        "region": region,
        "risk_level": risk_level,
        "risk_emoji": RISK_EMOJI[risk_level],
        "confidence": f"{max(probabilities):.1%}",
        "probabilities": {
            RISK_LABELS[index]: f"{probabilities[index]:.1%}"
            for index in range(len(RISK_LABELS))
        },
    }
