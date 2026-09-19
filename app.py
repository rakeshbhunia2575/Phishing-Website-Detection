import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request

from database.db import get_history, save_prediction
from models.predict import predict_url
from utils.url_validator import is_valid_url, normalize_url

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/")
def home():
    return render_template("index.html", history=get_history())


@app.route("/predict", methods=["POST"])
def predict():
    raw_url = request.form.get("url", "")

    if not raw_url.strip():
        return render_template(
            "index.html", prediction="Please enter a URL", history=get_history()
        )

    n = normalize_url(raw_url)

    if not is_valid_url(n):
        return render_template(
            "index.html",
            prediction="Invalid website address",
            history=get_history(),
        )

    try:
        result = predict_url(n)
    except Exception:
        # A scan failure must not be rendered as "Legitimate".
        app.logger.exception("scan failed for %s", n.host)
        return render_template(
            "index.html",
            prediction="Scan failed - could not check this address",
            history=get_history(),
        )

    save_prediction(n.url, result.label)

    return render_template(
        "index.html",
        prediction=result.as_text(),
        reasons=result.reasons,
        notes=result.notes,
        tier=result.tier,
        history=get_history(),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
