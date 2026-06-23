from fastapi import FastAPI
from pydantic import BaseModel

from utils.model import predict_risk

app = FastAPI(title="🌊 Flood Warning KZ API")

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
    return {"message": "Flood Warning KZ API is running!"}

@app.post("/predict")
def predict(data: WeatherInput):
    return predict_risk(
        data.region,
        data.rainfall_mm,
        data.temperature_c,
        data.humidity_pct,
        data.river_level_m,
        data.snow_melt_mm,
        data.prev_day_rain,
    )

@app.get("/health")
def health():
    return {"status": "✅ online"}
