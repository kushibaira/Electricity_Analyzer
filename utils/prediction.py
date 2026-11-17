
import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/electricity_model.pkl")

def predict_consumption(temperature, occupancy, appliance_usage):

    input_data = pd.DataFrame([{
        "Temperature": temperature,
        "Occupancy": occupancy,
        "Appliance_Usage": appliance_usage
    }])

    prediction = model.predict(input_data)

    return round(prediction[0], 2)
