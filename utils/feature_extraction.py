"""
URL-string ("lexical") features.

Every value here follows the UCI phishing dataset convention:

    -1 = phishing indicator present
     0 = suspicious / borderline
     1 = legitimate indicator

The original file had this backwards for having_IP_Address, having_At_Symbol,
Prefix_Suffix, having_Sub_Domain, Shortining_Service and
double_slash_redirecting: it returned +1 exactly when the risky condition was
present. Prefix_Suffix was the most damaging, because in the training data a
value of +1 corresponds to a 0% phishing rate, so any hyphenated domain
("secure-paypal-login.com") was handed the model a perfect legitimacy signal.

No value in this module is a placeholder. Everything is derived from the URL.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import tldextract

from utils.schema import LEXICAL_FEATURES
from utils.url_validator import NormalizedURL

# A longer list than the original five. Not exhaustive — it never can be — but
# these cover the overwhelming majority of shortened links in the wild.
SHORTENERS = {
    "bit.ly", "goo.gl", "tinyurl.com", "ow.ly", "t.co", "is.gd", "buff.ly",
    "adf.ly", "bit.do", "cutt.ly", "rb.gy", "rebrand.ly", "shorte.st",
    "soo.gd", "s2r.co", "tiny.cc", "lnkd.in", "db.tt", "qr.ae", "j.mp",
    "tr.im", "cli.gs", "yfrog.com", "migre.me", "ff.im", "url4.eu",
    "twitthis.com", "u.to", "shorturl.at", "clck.ru", "v.gd", "x.co",
}

# tldextract is pinned to its bundled snapshot so the app does not make a
# network call to publicsuffix.org on first use (which fails behind proxies and
# silently degrades domain parsing).
_extract = tldextract.TLDExtract(suffix_list_urls=())


def extract_lexical_features(n: NormalizedURL) -> dict[str, int]:
    url = n.url
    parsed = urlparse(url)
    parts = _extract(url)
    registered_domain = parts.domain
    subdomain = parts.subdomain

    return {
        # -1 when the host is a raw IP address (or hex-encoded IP), which is a
        # classic way to hide a hostname.
        "having_IP_Address": -1 if n.is_ip_literal or _is_hex_ip(n.host) else 1,

        # Dataset bucketing: <54 chars legit, 54-75 suspicious, >75 phishing.
        "URL_Length": 1 if len(url) < 54 else (0 if len(url) <= 75 else -1),

        # -1 when the registrable domain is a known shortener.
        "Shortining_Service": -1 if _registrable(parts) in SHORTENERS else 1,

        # -1 when "@" appears, since everything before it is discarded by the
        # browser and the real host is whatever follows. n.has_userinfo is
        # checked too, because normalisation strips the "user@" prefix out of
        # the rebuilt URL string.
        "having_At_Symbol": -1 if (n.has_userinfo or "@" in url) else 1,

        # -1 when "//" appears after the scheme, i.e. an embedded redirect.
        "double_slash_redirecting": -1 if url.find("//", 8) > 0 else 1,

        # -1 when a hyphen appears anywhere in the name part of the host
        # (subdomains included). "secure-paypal-login.verify.tk" hides its
        # hyphen in the subdomain, so checking the registrable domain alone
        # would miss it.
        "Prefix_Suffix": -1 if "-" in f"{subdomain}.{registered_domain}" else 1,

        # www is not a meaningful subdomain, so it is stripped first.
        # 0 remaining labels -> 1, one -> 0, two or more -> -1.
        "having_Sub_Domain": _subdomain_score(subdomain),

        # -1 for any non-standard port.
        "port": 1 if (parsed.port in (None, 80, 443)) else -1,

        # -1 when "http"/"https" appears as a token inside the HOST, e.g.
        # "https-paypal.com". The original checked whether the URL started with
        # https, which after normalisation was true for essentially every
        # input.
        "HTTPS_token": -1 if re.search(r"https?", n.host, re.I) else 1,
    }


def _registrable(parts) -> str:
    return ".".join(p for p in (parts.domain, parts.suffix) if p).lower()


def _subdomain_score(subdomain: str) -> int:
    sub = re.sub(r"^www\.?", "", subdomain or "", flags=re.I).strip(".")
    if not sub:
        return 1
    labels = len([part for part in sub.split(".") if part])
    if labels == 1:
        return 0
    return -1


def _is_hex_ip(host: str) -> bool:
    return bool(re.fullmatch(r"0x[0-9a-f]{8}", host or "", re.I))


# Sanity check: the keys produced here must exactly match the schema. The old
# predict.py used df.reindex(fill_value=0), which silently inserted zeros for
# any typo instead of raising. Fail loudly at import time instead.
_probe = set(
    extract_lexical_features(
        NormalizedURL(url="http://example.com/", host="example.com",
                      scheme_was_supplied=True, is_ip_literal=False)
    )
)
assert _probe == set(LEXICAL_FEATURES), (
    f"lexical feature mismatch: {_probe ^ set(LEXICAL_FEATURES)}"
)
