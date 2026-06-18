# Flood Warning KZ

Flood Warning KZ is a simple Streamlit dashboard and FastAPI service for flood-risk screening across major regions of Kazakhstan.

## What it does

- Shows a clear risk status with no manual input required
- Uses live OpenWeatherMap data when an API key is available
- Falls back to deterministic regional estimates when live data is missing
- Supports English, Kazakh, and Russian
- Shows a Kazakhstan-wide risk map
- Highlights the regions that need attention

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

If you want the app to keep restarting on Windows, use:

```powershell
.\run_dashboard.ps1
```

Or double-click:

```text
run_dashboard.bat
```

For a fully hidden background start, run:

```text
start_dashboard.vbs
```

Run the API:

```bash
uvicorn api.main:app --reload
```

## Project notes

- The model is a demo classifier trained on synthetic historical flood data.
- The dashboard is automatic: people only read the risk result, they do not enter weather values.
- Live weather data is preferred when an OpenWeatherMap API key is provided.
- The fallback weather path is deterministic, not random, so the app feels stable.
- The current "recent rain" feature is a rainfall proxy used by the model input pipeline.
- `run_dashboard.ps1` will restart Streamlit if it exits.
- `start_dashboard.vbs` starts the watchdog without opening a visible console window.
- `run_dashboard.bat` now opens the hidden launcher.

## Main files

- `dashboard/app.py` — Streamlit app
- `api/main.py` — FastAPI prediction endpoint
- `utils/weather.py` — Weather fetch helpers
- `utils/model.py` — Shared model loading and prediction logic
- `model/train.py` — Model training script
