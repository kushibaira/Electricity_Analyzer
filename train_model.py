
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib
import os

# Load electricity dataset
df = pd.read_csv("dataset/electricity_data.csv")

# Select input features
X = df[["Temperature", "Occupancy", "Appliance_Usage"]]

# Target value
y = df["Electricity_Consumption"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train machine learning model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test model
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)

print("Model trained successfully!")
print("Mean Absolute Error:", round(mae, 2))

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/electricity_model.pkl")

print("Model saved successfully!")
