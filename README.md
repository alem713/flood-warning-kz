# Flood Warning KZ

Flood Warning KZ is a Streamlit dashboard and FastAPI service for flood-risk screening across major regions of Kazakhstan.

## What it does

- Predicts flood risk from weather and river inputs
- Uses live OpenWeatherMap data when an API key is available
- Falls back to deterministic regional estimates when live data is missing
- Shows a Kazakhstan-wide risk map
- Displays a 72-hour forecast view when weather data is available
- Includes a relief-tracker demo section for presentation purposes

## Tech stack

- Python
- Streamlit
- FastAPI
- XGBoost
- Folium
- Plotly

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard/app.py
```

Run the API:

```bash
uvicorn api.main:app --reload
```

## Project notes

- The model is a demo classifier trained on synthetic historical flood data.
- Live weather data is preferred when an OpenWeatherMap API key is provided.
- The fallback weather path is deterministic, not random, so the app feels stable.
- The current "recent rain" feature is a rainfall proxy used by the model input pipeline.

## Main files

- `dashboard/app.py` — Streamlit app
- `api/main.py` — FastAPI prediction endpoint
- `utils/weather.py` — Weather fetch helpers
- `utils/model.py` — Shared model loading and prediction logic
- `model/train.py` — Model training script
