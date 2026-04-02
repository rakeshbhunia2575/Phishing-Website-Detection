import joblib
import pandas as pd
from utils.feature_extraction import extract_features

# Load model & columns
model = joblib.load("models/phishing_model.pkl")
model_columns = joblib.load("models/model_columns.pkl")

def predict_url(url: str) -> str:
    features = extract_features(url)

    df = pd.DataFrame([features])
    df = df.reindex(columns=model_columns, fill_value=0)

    prediction = model.predict(df)[0]

    # ⚠️ adjust label if needed
    if prediction == 1:
        return "Phishing Website"
    else:
        return "Legitimate Website"
