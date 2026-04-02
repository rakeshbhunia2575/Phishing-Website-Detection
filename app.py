from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

from models.predict import predict_url
from database.db import save_prediction, get_history
from utils.url_validator import normalize_url, is_valid_url

load_dotenv()
app = Flask(__name__)

@app.route("/")
def home():
    history = get_history()
    return render_template("index.html", history=history)

@app.route("/predict", methods=["POST"])
def predict():
    raw_url = request.form.get("url")

    history = get_history()

    if not raw_url or not raw_url.strip():
        return render_template(
            "index.html",
            prediction="❌ Please enter a URL",
            history=history
        )

    url = normalize_url(raw_url)

    if not is_valid_url(url):
        return render_template(
            "index.html",
            prediction="⚠️ Invalid website address",
            history=history
        )

    result = predict_url(url)
    save_prediction(url, result)

    
    history = get_history()

    return render_template(
        "index.html",
        prediction=result,
        history=history
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
