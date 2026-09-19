# What was wrong and what changed

## The root cause

`data/phising.csv` is the UCI phishing dataset. Its features are page-level and
infrastructure-level: TLS certificate trust and age, the fraction of `<a>` tags
pointing off-domain, Alexa traffic rank, WHOIS domain age. The old
`extract_features()` only had a URL string, so it hardcoded 13 of 25 features to
fixed constants — including `SSLfinal_State` (0.307 importance) and
`URL_of_Anchor` (0.260). About 57% of the forest's decision power was frozen at
a value it never saw in training. Every prediction was effectively a coin flip
dressed up as a confident classification.

Observed with the original code:

| URL | Old output |
|---|---|
| `paypal-secure-login.verify-account.tk` | Legitimate (0.92) |
| `bit.ly/xyz` | Legitimate (0.74) |
| `http://secure-bank.com` | Legitimate (0.74) |
| `http://google.com` | **Phishing** (0.71) |

## Bugs fixed

**1. Inverted sign conventions.** The dataset uses `-1` for "risky condition
present". The old extractor returned `+1` for exactly those conditions on
`having_IP_Address`, `having_At_Symbol`, `Prefix_Suffix`, `having_Sub_Domain`,
`Shortining_Service` and `double_slash_redirecting`. `Prefix_Suffix` was the
worst: in the training data `+1` corresponds to a **0%** phishing rate, so any
hyphenated domain handed the model a perfect legitimacy signal.

**2. `normalize_url` invented `https://`.** Since `SSLfinal_State` and
`HTTPS_token` were both `url.startswith("https")`, every typed-in domain got
`SSLfinal_State = 1` — the single strongest legitimate signal (phishing rate
drops from 0.86 to 0.11). The app was reading back its own default as evidence.
Now normalisation records whether the scheme was supplied, and SSL state comes
from a real TLS handshake.

**3. `Abnormal_URL` was a constant.** `1 if domain not in url else -1` — the
domain is extracted *from* the URL, so it was always `-1`. Now compared against
the WHOIS record.

**4. `HTTPS_token` checked the wrong thing.** It's meant to catch `https` used
as a token *inside the hostname* (`https-paypal.com`), not the scheme.

**5. `df.reindex(fill_value=0)` masked errors.** Any typo in a feature name
became a silent zero. Now missing or unknown columns raise.

**6. IP-literal URLs were rejected as invalid** by the domain regex, so the one
case `having_IP_Address` exists to catch never reached the model.

**7. MongoDB connection leak.** `get_collection()` opened a fresh `MongoClient`
on every call and was called three times per request. Now cached, with a
selection timeout and error handling so a DB failure can't kill a scan.

**8. Exceptions rendered as "Legitimate".** Any crash in `predict_url` produced
a 500 or, worse, a misleading result. Now caught and shown as a scan failure.

## Design changes

**Dropped the five features that need a service we don't have** —
`web_traffic`, `Page_Rank`, `Google_Index`, `Links_pointing_to_page`,
`Statistical_report`. A feature you can't compute must be removed from the
model, not faked.

**Two model tiers** (`train.py`):

| Model | Features | Test accuracy | 5-fold CV |
|---|---|---|---|
| `full_model` | 25 (lexical + live probe) | **95.3%** | 0.951 ± 0.005 |
| `lexical_model` | 9 (URL string only) | 74.0% | 0.741 ± 0.034 |

The full model runs when the site responds. When it doesn't — common for
phishing pages already taken down — the lexical model runs and the UI says the
scan was limited. That 74% is the honest ceiling for URL-only classification on
this dataset; the old code was implicitly claiming the 95% number while feeding
the model garbage.

**Live probes** (`utils/live_features.py`): TLS handshake with issuer and cert
age checks, WHOIS for domain age and registration length, DNS resolution, and a
parsed HTML fetch for anchor ratios, form handlers, iframes, favicon origin and
pop-up behaviour.

**SSRF guard.** Because the app now fetches attacker-supplied URLs, every host
is resolved and rejected if it points at loopback, private, link-local or
reserved space — otherwise someone could aim the scanner at `169.254.169.254`
and read your cloud metadata. Redirects are followed manually with a cap and
re-checked at each hop; response size and time are bounded; HTML is parsed,
never executed.

**Explanations.** The result now shows which signals fired, so a wrong answer is
debuggable instead of opaque.

## Files

| File | Status |
|---|---|
| `utils/schema.py` | new — single source of truth for feature tiers |
| `utils/feature_extraction.py` | rewritten — lexical only, correct signs |
| `utils/live_features.py` | new — TLS, WHOIS, DNS, HTML probes |
| `utils/url_validator.py` | rewritten — normalisation, IDN, SSRF guard |
| `models/predict.py` | rewritten — tiered, strict columns, explanations |
| `train.py` | new — retrains both models, prints metrics |
| `scan.py` | new — CLI for testing without Flask |
| `tests/test_features.py` | new — 24 tests |
| `app.py`, `database/db.py`, `templates/`, `static/` | updated |

## Running it

```bash
pip install -r requirements.txt
python train.py                  # regenerates models/
python -m pytest tests -q
python scan.py --features github.com
python app.py
```

`models/phishing_model.pkl` and `model_columns.pkl` were deleted — they were
trained on columns the app can't supply. `full_model.pkl` and
`lexical_model.pkl` replace them.

## Remaining limits

The full model still assumes a page that renders server-side. A JavaScript-only
SPA yields a near-empty DOM, so anchor and link ratios are unreliable. If you
want to go further, a headless browser (Playwright) for rendering and a
PhishTank/OpenPhish feed for the `Statistical_report` column would close most of
the gap.
