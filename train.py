"""
Retrains the classifier on only the features this app can actually compute.

Run:  python train.py

Two models are produced:

  full_model     - lexical + live content features. Used when the site responds.
  lexical_model  - URL-string features only. Used when the site is unreachable,
                   which is common for phishing pages that have been taken down.

The five columns needing a third-party service (web_traffic, Page_Rank,
Google_Index, Links_pointing_to_page, Statistical_report) are dropped. The old
model kept them and fed constants; that was the main source of wrong answers.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split

from utils.schema import (
    CONTENT_FEATURES,
    DROPPED_FEATURES,
    FULL_FEATURES,
    LEXICAL_FEATURES,
    TARGET,
)

DATA = Path("data/phising.csv")
OUT = Path("models")
SEED = 42


def train_one(df: pd.DataFrame, columns: list[str], name: str) -> dict:
    X = df[columns]
    y = df[TARGET]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=400,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    )
    clf.fit(X_tr, y_tr)

    pred = clf.predict(X_te)
    proba = clf.predict_proba(X_te)[:, list(clf.classes_).index(-1)]
    cv = cross_val_score(clf, X, y, cv=5, scoring="accuracy")

    print(f"\n=== {name} ({len(columns)} features) ===")
    print(classification_report(y_te, pred, target_names=["phishing", "legit"], digits=3))
    print("confusion matrix [rows=true phishing,legit]:")
    print(confusion_matrix(y_te, pred, labels=[-1, 1]))
    print(f"ROC-AUC: {roc_auc_score((y_te == -1).astype(int), proba):.3f}")
    print(f"5-fold CV accuracy: {cv.mean():.3f} +/- {cv.std():.3f}")

    importances = (
        pd.Series(clf.feature_importances_, index=columns)
        .sort_values(ascending=False)
        .round(4)
    )
    print("\ntop features:")
    print(importances.head(8).to_string())

    joblib.dump(clf, OUT / f"{name}.pkl")
    joblib.dump(list(columns), OUT / f"{name}_columns.pkl")

    return {
        "features": list(columns),
        "test_accuracy": float((pred == y_te).mean()),
        "cv_accuracy_mean": float(cv.mean()),
        "cv_accuracy_std": float(cv.std()),
        "importances": importances.to_dict(),
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(DATA)

    missing = [c for c in FULL_FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise SystemExit(f"dataset is missing columns: {missing}")

    print(f"rows: {len(df)}   dropped (not computable): {DROPPED_FEATURES}")

    report = {
        "full_model": train_one(df, FULL_FEATURES, "full_model"),
        "lexical_model": train_one(df, LEXICAL_FEATURES, "lexical_model"),
        "dropped_features": DROPPED_FEATURES,
        "content_features": CONTENT_FEATURES,
    }

    (OUT / "training_report.json").write_text(json.dumps(report, indent=2))
    print(f"\nsaved models and models/training_report.json")


if __name__ == "__main__":
    main()
