"""
Phishing URL detection API.

Run from the project root (the folder that contains "app"):

    uvicorn app.main:app --host 0.0.0.0 --port 8000

Interactive docs: http://localhost:8000/docs
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.services.predict import predict_url
from app.utils.url_validator import is_valid_url, normalize_url

logger = logging.getLogger("phishing-api")

app = FastAPI(title="Phishing URL Detection API", version="1.0.0")


class PredictRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048, examples=["https://www.google.com/"])


class PredictResponse(BaseModel):
    url: str                       # normalized URL that was actually analysed
    label: str                     # "Phishing Website" | "Legitimate Website"
    is_phishing: bool
    confidence: float              # 0..1
    tier: str                      # "full" | "lexical"
    reasons: list[str]
    notes: list[str]
    features: dict[str, int]


def _run_prediction(raw_url: str) -> PredictResponse:
    n = normalize_url(raw_url)
    if not is_valid_url(n):
        raise HTTPException(status_code=400, detail=f"Invalid URL: {raw_url!r}")

    try:
        p = predict_url(n)
    except Exception:
        logger.exception("prediction failed for %s", n.url)
        raise HTTPException(status_code=500, detail="Prediction failed")

    data = asdict(p)  # Prediction is a dataclass -> plain dict
    return PredictResponse(
        url=n.url,
        label=data["label"],
        is_phishing=p.is_phishing,
        confidence=round(float(data["confidence"]), 4),
        tier=data["tier"],
        reasons=data["reasons"],
        notes=data["notes"],
        features={k: int(v) for k, v in data["features"].items()},
    )


# Plain "def" (not "async def") on purpose: predict_url does blocking network
# I/O (DNS, TLS, WHOIS, page fetch), so FastAPI runs it in a worker thread
# instead of freezing the event loop.
@app.post("/predict", response_model=PredictResponse)
def predict_post(req: PredictRequest):
    return _run_prediction(req.url)


@app.get("/predict", response_model=PredictResponse)
def predict_get(url: str):
    return _run_prediction(url)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)