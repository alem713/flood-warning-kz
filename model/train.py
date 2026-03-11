import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier
import joblib

# Load data
print(" Loading dataset...")
df = pd.read_csv("data/historical_floods.csv")

# Features & target
features = ["rainfall_mm", "temperature_c", "humidity_pct", 
            "river_level_m", "snow_melt_mm", "prev_day_rain"]
X = df[features]
y = df["risk_level"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
print(" Training model...")
model = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42,
    eval_metric="mlogloss"
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n Model trained! Accuracy: {acc:.2%}")
print("\n Report:")
print(classification_report(y_test, y_pred, 
      target_names=["Low", "Medium", "High", "Critical"]))

# Save model
joblib.dump(model, "model/flood_model.joblib")
print(" Model saved to model/flood_model.joblib")