"""
Prediction orchestration.

Changes from the original:

  * No df.reindex(fill_value=0). Missing or misnamed columns now raise instead
    of being quietly filled with a zero the model will happily act on.
  * Returns a structured result, not a bare string: label, confidence, which
    model tier was used, and the signals that drove the answer.
  * Two tiers. If the site responds, the full model runs on real TLS/WHOIS/HTML
    features. If it does not, the lexical model runs and the result is reported
    as low-confidence, rather than pretending the content features exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import pandas as pd

from utils.feature_extraction import extract_lexical_features
from utils.live_features import probe
from utils.schema import LEGITIMATE, PHISHING
from utils.url_validator import NormalizedURL

MODELS = Path(__file__).resolve().parent

_full = joblib.load(MODELS / "full_model.pkl")
_full_cols = joblib.load(MODELS / "full_model_columns.pkl")
_lex = joblib.load(MODELS / "lexical_model.pkl")
_lex_cols = joblib.load(MODELS / "lexical_model_columns.pkl")

# Plain-language reason strings, shown only when the feature fired as -1.
REASONS = {
    "SSLfinal_State": "no trusted HTTPS certificate",
    "URL_of_Anchor": "most links on the page point to other domains",
    "having_Sub_Domain": "unusually deep subdomain nesting",
    "Prefix_Suffix": "hyphenated domain name",
    "Links_in_tags": "meta/script/link tags load mostly from other domains",
    "SFH": "form submits to a blank or third-party handler",
    "Request_URL": "most images and scripts load from other domains",
    "having_IP_Address": "raw IP address instead of a domain name",
    "Shortining_Service": "link shortener hides the real destination",
    "having_At_Symbol": "'@' in the URL hides the real host",
    "double_slash_redirecting": "embedded redirect in the path",
    "URL_Length": "unusually long URL",
    "port": "non-standard port",
    "HTTPS_token": "'http'/'https' used inside the hostname",
    "age_of_domain": "domain registered less than six months ago",
    "Domain_registeration_length": "domain registered for under a year",
    "Abnormal_URL": "host does not match its WHOIS record",
    "DNSRecord": "no DNS record",
    "Iframe": "hidden iframe on the page",
    "on_mouseover": "script rewrites the status bar on hover",
    "RightClick": "right-click menu disabled",
    "popUpWidnow": "pop-up asking for text input",
    "Submitting_to_email": "form emails your input directly",
    "Favicon": "favicon loaded from a different domain",
}


@dataclass
class Prediction:
    label: str                  # "Phishing Website" | "Legitimate Website"
    confidence: float           # 0..1
    tier: str                   # "full" | "lexical"
    reasons: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    features: dict = field(default_factory=dict)

    @property
    def is_phishing(self) -> bool:
        return self.label.startswith("Phishing")

    def as_text(self) -> str:
        return self.label


def _frame(features: dict, columns: list[str]) -> pd.DataFrame:
    missing = [c for c in columns if c not in features]
    if missing:
        raise ValueError(f"feature extractor did not produce: {missing}")
    extra = [k for k in features if k not in columns]
    if extra:
        raise ValueError(f"feature extractor produced unknown columns: {extra}")
    return pd.DataFrame([{c: features[c] for c in columns}], columns=columns)


def predict_url(n: NormalizedURL) -> Prediction:
    lexical = extract_lexical_features(n)
    result = probe(n)

    if result.reachable and all(c in {**lexical, **result.features} for c in _full_cols):
        features = {**lexical, **result.features}
        model, columns, tier = _full, _full_cols, "full"
    else:
        features = lexical
        model, columns, tier = _lex, _lex_cols, "lexical"
        result.notes.append(
            "Site did not respond, so only the URL itself could be checked. "
            "Treat this result as weak evidence."
        )

    df = _frame(features, columns)
    proba = model.predict_proba(df)[0]
    classes = list(model.classes_)
    p_phish = float(proba[classes.index(PHISHING)])

    is_phish = p_phish >= 0.5
    label = "Phishing Website" if is_phish else "Legitimate Website"
    confidence = p_phish if is_phish else 1 - p_phish

    reasons = [REASONS[k] for k, v in features.items() if v == -1 and k in REASONS]

    return Prediction(
        label=label,
        confidence=confidence,
        tier=tier,
        reasons=reasons[:6],
        notes=result.notes,
        features=features,
    )
