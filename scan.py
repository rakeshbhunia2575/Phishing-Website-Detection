"""
Command-line scanner, for checking behaviour without starting Flask.

    python scan.py google.com http://192.168.0.1/login.php
    python scan.py --features paypal-secure.verify-login.tk
    python scan.py --offline suspicious-site.tk     # skip all network probes
"""

from __future__ import annotations

import argparse
import sys

from models.predict import predict_url
from utils.feature_extraction import extract_lexical_features
from utils.url_validator import is_valid_url, normalize_url


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--features", action="store_true", help="print every feature value")
    ap.add_argument("--offline", action="store_true", help="lexical features only")
    args = ap.parse_args()

    for raw in args.urls:
        n = normalize_url(raw)
        if not is_valid_url(n):
            print(f"{raw}\n  invalid URL\n")
            continue

        if args.offline:
            feats = extract_lexical_features(n)
            print(raw)
            for k, v in feats.items():
                print(f"  {k:28s} {v:+d}")
            print()
            continue

        r = predict_url(n)
        icon = "!" if r.is_phishing else "."
        print(f"{icon} {raw}")
        print(f"  {r.as_text()}   [{r.tier} scan]")
        for reason in r.reasons:
            print(f"  - {reason}")
        for note in r.notes:
            print(f"  ~ {note}")
        if args.features:
            for k, v in sorted(r.features.items()):
                print(f"    {k:28s} {v:+d}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
