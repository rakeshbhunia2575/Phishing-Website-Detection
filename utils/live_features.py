"""
Content and infrastructure features, computed for real.

These are the features the original app faked. SSLfinal_State and URL_of_Anchor
alone carry ~57% of the forest's decision power, and both were constants, so
the model was effectively being asked to classify a point it had never seen.

Each function returns a dataset-convention value (-1 phishing / 0 suspicious /
1 legitimate), or None when the probe could not be completed. None propagates
up and causes predict.py to fall back to the lexical-only model instead of
inventing a number.

Safety notes, since this module now fetches attacker-controlled pages:
  * the host is resolved and checked against internal ranges before any request
  * redirects are followed manually with a cap, re-checking each hop
  * response size and time are both bounded
  * HTML is parsed, never executed
"""

from __future__ import annotations

import re
import socket
import ssl
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import requests
import tldextract
from bs4 import BeautifulSoup

from utils.url_validator import NormalizedURL, is_safe_to_fetch

CONNECT_TIMEOUT = 5
READ_TIMEOUT = 8
MAX_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 5
USER_AGENT = "Mozilla/5.0 (compatible; LinkWatch/2.0; +phishing-scanner)"

# Issuers the dataset treats as trusted CAs.
TRUSTED_ISSUER_HINTS = (
    "digicert", "globalsign", "sectigo", "comodo", "godaddy", "entrust",
    "let's encrypt", "lets encrypt", "amazon", "google trust", "verisign",
    "thawte", "geotrust", "rapidssl", "identrust", "certum", "buypass",
    "zerossl", "microsoft", "cloudflare",
)

_extract = tldextract.TLDExtract(suffix_list_urls=())


@dataclass
class ProbeResult:
    reachable: bool
    features: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    final_url: str | None = None


def probe(n: NormalizedURL) -> ProbeResult:
    notes: list[str] = []

    safe, reason = is_safe_to_fetch(n.host)
    if not safe:
        return ProbeResult(reachable=False, notes=[f"not fetched: {reason}"])

    features: dict[str, int] = {}

    features["DNSRecord"] = 1  # is_safe_to_fetch already resolved it

    ssl_state, ssl_note = _ssl_final_state(n)
    features["SSLfinal_State"] = ssl_state
    if ssl_note:
        notes.append(ssl_note)

    whois_feats, whois_notes = _whois_features(n)
    features.update(whois_feats)
    notes.extend(whois_notes)

    html, final_url, hops = _fetch(n)
    if html is None:
        return ProbeResult(reachable=False, notes=notes + ["page could not be fetched"])

    features["Redirect"] = 0 if hops <= 1 else 1
    features.update(_content_features(html, final_url))

    missing = [k for k, v in features.items() if v is None]
    for k in missing:
        features.pop(k)

    return ProbeResult(
        reachable=True, features=features, notes=notes, final_url=final_url
    )


# --------------------------------------------------------------------------
# TLS
# --------------------------------------------------------------------------

def _ssl_final_state(n: NormalizedURL) -> tuple[int, str]:
    """1 = trusted issuer and cert age >= 1 year, 0 = valid but young/unknown
    issuer, -1 = no HTTPS or the handshake fails verification."""
    port = urlparse(n.url).port or 443
    ctx = ssl.create_default_context()

    try:
        with socket.create_connection((n.host, port), timeout=CONNECT_TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=n.host) as tls:
                cert = tls.getpeercert()
    except ssl.SSLCertVerificationError as e:
        return -1, f"TLS certificate not trusted ({e.verify_message or 'verify failed'})"
    except (ssl.SSLError, socket.timeout, OSError):
        return -1, "no working HTTPS on this host"

    issuer = " ".join(
        v.lower() for rdn in cert.get("issuer", ()) for _, v in rdn
    )
    trusted = any(hint in issuer for hint in TRUSTED_ISSUER_HINTS)

    age_ok = False
    not_before = cert.get("notBefore")
    if not_before:
        try:
            start = datetime.strptime(not_before, "%b %d %H:%M:%S %Y %Z").replace(
                tzinfo=timezone.utc
            )
            age_ok = (datetime.now(timezone.utc) - start) >= timedelta(days=365)
        except ValueError:
            pass

    if trusted and age_ok:
        return 1, ""
    if trusted:
        return 0, "certificate is trusted but less than a year old"
    return 0, "certificate issuer not in the trusted list"


# --------------------------------------------------------------------------
# WHOIS
# --------------------------------------------------------------------------

def _whois_features(n: NormalizedURL) -> tuple[dict, list[str]]:
    feats: dict[str, int] = {}
    notes: list[str] = []

    if n.is_ip_literal:
        return {"age_of_domain": -1, "Domain_registeration_length": -1,
                "Abnormal_URL": -1}, ["host is a raw IP, no WHOIS record"]

    try:
        import whois  # python-whois
        parts = _extract(n.url)
        record = whois.whois(".".join(p for p in (parts.domain, parts.suffix) if p))
    except Exception:
        notes.append("WHOIS lookup unavailable")
        return feats, notes

    created = _first_date(record.creation_date)
    expires = _first_date(record.expiration_date)
    now = datetime.now(timezone.utc)

    if created:
        # Dataset threshold: 6 months.
        feats["age_of_domain"] = 1 if (now - created) >= timedelta(days=182) else -1
    if expires:
        feats["Domain_registeration_length"] = (
            1 if (expires - now) >= timedelta(days=365) else -1
        )

    # -1 when the host does not appear in its own WHOIS record. The original
    # was `1 if domain not in url else -1`, which is always -1 by construction.
    if record.domain_name:
        names = record.domain_name
        names = [names] if isinstance(names, str) else list(names)
        feats["Abnormal_URL"] = (
            1 if any(str(d).lower() in n.host for d in names if d) else -1
        )
    else:
        feats["Abnormal_URL"] = -1

    return feats, notes


def _first_date(value):
    if value is None:
        return None
    if isinstance(value, list):
        value = next((v for v in value if v), None)
    if not isinstance(value, datetime):
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


# --------------------------------------------------------------------------
# Page fetch
# --------------------------------------------------------------------------

def _fetch(n: NormalizedURL) -> tuple[str | None, str, int]:
    url = n.url
    hops = 0
    session = requests.Session()
    session.max_redirects = 1

    for _ in range(MAX_REDIRECTS):
        host = urlparse(url).hostname or ""
        safe, _reason = is_safe_to_fetch(host)
        if not safe:
            return None, url, hops

        try:
            resp = session.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                allow_redirects=False,
                stream=True,
                verify=True,
            )
        except requests.RequestException:
            # A failed TLS verify shouldn't block content analysis; retry once
            # without verification, since SSLfinal_State already recorded it.
            try:
                resp = session.get(
                    url, headers={"User-Agent": USER_AGENT},
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    allow_redirects=False, stream=True, verify=False,
                )
            except requests.RequestException:
                return None, url, hops

        if resp.is_redirect or resp.is_permanent_redirect:
            location = resp.headers.get("Location")
            resp.close()
            if not location:
                return None, url, hops
            url = urljoin(url, location)
            hops += 1
            continue

        if "html" not in resp.headers.get("Content-Type", "").lower():
            resp.close()
            return None, url, hops

        chunks, total = [], 0
        for chunk in resp.iter_content(8192, decode_unicode=False):
            total += len(chunk)
            chunks.append(chunk)
            if total >= MAX_BYTES:
                break
        resp.close()
        body = b"".join(chunks).decode(resp.encoding or "utf-8", errors="replace")
        return body, url, hops

    return None, url, hops


# --------------------------------------------------------------------------
# HTML content features
# --------------------------------------------------------------------------

def _content_features(html: str, final_url: str) -> dict[str, int]:
    soup = BeautifulSoup(html, "html.parser")
    base = _registrable(final_url)

    return {
        "Favicon": _favicon(soup, final_url, base),
        "Request_URL": _request_url(soup, final_url, base),
        "URL_of_Anchor": _url_of_anchor(soup, final_url, base),
        "Links_in_tags": _links_in_tags(soup, final_url, base),
        "SFH": _sfh(soup, final_url, base),
        "Submitting_to_email": _submitting_to_email(soup, html),
        "on_mouseover": -1 if re.search(
            r"onmouseover\s*=\s*[\"'][^\"']*window\.status", html, re.I) else 1,
        "RightClick": -1 if re.search(
            r"event\.button\s*==\s*2|contextmenu", html, re.I) else 1,
        "popUpWidnow": _popup(html),
        "Iframe": -1 if soup.find_all(["iframe", "frame"]) else 1,
    }


def _registrable(url: str) -> str:
    p = _extract(url)
    return ".".join(x for x in (p.domain, p.suffix) if x).lower()


def _is_external(link: str, base_url: str, base_domain: str) -> bool | None:
    link = (link or "").strip()
    if not link or link.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
        return None  # not a real navigation target; excluded from the ratio
    absolute = urljoin(base_url, link)
    other = _registrable(absolute)
    if not other:
        return None
    return other != base_domain


def _ratio(links, base_url, base_domain) -> float | None:
    flags = [_is_external(l, base_url, base_domain) for l in links]
    flags = [f for f in flags if f is not None]
    if not flags:
        return None
    return sum(flags) / len(flags)


def _bucket(ratio: float | None, low: float, high: float) -> int | None:
    """<low -> 1, low..high -> 0, >high -> -1."""
    if ratio is None:
        return None
    if ratio < low:
        return 1
    if ratio <= high:
        return 0
    return -1


def _favicon(soup, base_url, base_domain) -> int:
    """-1 when the favicon is loaded from a different registrable domain."""
    for link in soup.find_all("link"):
        rel = " ".join(link.get("rel") or []).lower()
        if "icon" not in rel:
            continue
        ext = _is_external(link.get("href", ""), base_url, base_domain)
        if ext is True:
            return -1
    return 1


def _url_of_anchor(soup, base_url, base_domain) -> int | None:
    links = [a.get("href", "") for a in soup.find_all("a")]
    return _bucket(_ratio(links, base_url, base_domain), 0.31, 0.67)


def _request_url(soup, base_url, base_domain) -> int | None:
    links = []
    for tag, attr in (("img", "src"), ("video", "src"), ("audio", "src"),
                      ("source", "src"), ("script", "src")):
        links += [t.get(attr, "") for t in soup.find_all(tag)]
    ratio = _ratio(links, base_url, base_domain)
    if ratio is None:
        return None
    # This column is binary in the CSV, so collapse to two classes at 22%.
    return 1 if ratio < 0.22 else -1


def _links_in_tags(soup, base_url, base_domain) -> int | None:
    links = [m.get("content", "") for m in soup.find_all("meta")]
    links += [s.get("src", "") for s in soup.find_all("script")]
    links += [l.get("href", "") for l in soup.find_all("link")]
    return _bucket(_ratio(links, base_url, base_domain), 0.17, 0.81)


def _sfh(soup, base_url, base_domain) -> int | None:
    forms = soup.find_all("form")
    if not forms:
        return 1
    worst = 1
    for form in forms:
        action = (form.get("action") or "").strip()
        if action == "" or action.lower() in ("about:blank", "#"):
            return -1
        ext = _is_external(action, base_url, base_domain)
        if ext:
            worst = min(worst, 0)
    return worst


def _submitting_to_email(soup, html: str) -> int:
    if re.search(r"mail\s*\(", html, re.I):
        return -1
    for form in soup.find_all("form"):
        if (form.get("action") or "").lower().startswith("mailto:"):
            return -1
    return 1


def _popup(html: str) -> int:
    for match in re.finditer(r"window\.open\s*\(", html, re.I):
        window = html[match.start(): match.start() + 600]
        if re.search(r"type\s*=\s*[\"']?(text|password)", window, re.I):
            return -1
    return 1
