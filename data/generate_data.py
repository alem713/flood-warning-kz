import pandas as pd
import numpy as np

np.random.seed(42)

regions = [
    "Almaty", "Astana", "Shymkent", "Karaganda", "Aktobe",
    "Pavlodar", "Semey", "Taraz", "Oskemen", "Atyrau",
    "Kostanay", "Kyzylorda", "Aktau", "Petropavl", "Taldykorgan"
]

n = 1000
data = {
    "region": np.random.choice(regions, n),
    "rainfall_mm": np.random.uniform(0, 120, n),
    "temperature_c": np.random.uniform(-10, 35, n),
    "humidity_pct": np.random.uniform(20, 100, n),
    "river_level_m": np.random.uniform(0.5, 8.0, n),
    "snow_melt_mm": np.random.uniform(0, 50, n),
    "prev_day_rain": np.random.uniform(0, 80, n),
}

df = pd.DataFrame(data)

def risk_label(row):
    score = 0
    if row["rainfall_mm"] > 60: score += 3
    elif row["rainfall_mm"] > 30: score += 2
    elif row["rainfall_mm"] > 15: score += 1

    if row["river_level_m"] > 6: score += 3
    elif row["river_level_m"] > 4: score += 2
    elif row["river_level_m"] > 2.5: score += 1

    if row["snow_melt_mm"] > 30: score += 2
    elif row["snow_melt_mm"] > 15: score += 1

    if row["humidity_pct"] > 85: score += 1
    if row["prev_day_rain"] > 40: score += 1

    if score >= 7: return 3
    elif score >= 5: return 2
    elif score >= 3: return 1
    else: return 0

df["risk_level"] = df.apply(risk_label, axis=1)
df["risk_label"] = df["risk_level"].map({
    0: "Low", 1: "Medium", 2: "High", 3: "Critical"
})

df.to_csv("data/historical_floods.csv", index=False)
print("✅ Dataset created!")
print(df["risk_label"].value_counts())