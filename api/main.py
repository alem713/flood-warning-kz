from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="🌊 Flood Warning KZ API")

# Load model
model = joblib.load("model/flood_model.joblib")

RISK_LABELS = {0: "Low", 1: "Medium", 2: "High", 3: "Critical"}
RISK_COLORS = {0: "🟢", 1: "🟡", 2: "🟠", 3: "🔴"}

class WeatherInput(BaseModel):
    region: str
    rainfall_mm: float
    temperature_c: float
    humidity_pct: float
    river_level_m: float
    snow_melt_mm: float
    prev_day_rain: float

@app.get("/")
def root():
    return {"message": " Flood Warning KZ API is running!"}

@app.post("/predict")
def predict(data: WeatherInput):
    features = np.array([[
        data.rainfall_mm,
        data.temperature_c,
        data.humidity_pct,
        data.river_level_m,
        data.snow_melt_mm,
        data.prev_day_rain
    ]])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    return {
        "region": data.region,
        "risk_level": RISK_LABELS[prediction],
        "risk_emoji": RISK_COLORS[prediction],
        "confidence": f"{max(probability):.1%}",
        "probabilities": {
            "Low": f"{probability[0]:.1%}",
            "Medium": f"{probability[1]:.1%}",
            "High": f"{probability[2]:.1%}",
            "Critical": f"{probability[3]:.1%}",
        }
    }

@app.get("/health")
def health():
    return {"status": "✅ online"}