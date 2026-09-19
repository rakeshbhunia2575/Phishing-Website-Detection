"""
Run with:  python -m pytest tests -q

These lock in the things that were broken: sign conventions, no placeholder
values, the full-tier feature set being complete, and the SSRF guard.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest

from utils.feature_extraction import extract_lexical_features
from utils.live_features import _content_features
from utils.schema import CONTENT_FEATURES, FULL_FEATURES, LEXICAL_FEATURES
from utils.url_validator import is_safe_to_fetch, is_valid_url, normalize_url


def lex(url: str) -> dict:
    return extract_lexical_features(normalize_url(url))


# -- sign conventions: -1 must mean "risky", matching the training data -------

@pytest.mark.parametrize(
    "url,feature",
    [
        ("http://192.168.0.5/login.php", "having_IP_Address"),
        ("http://bit.ly/x9f", "Shortining_Service"),
        ("http://paypal.com@evil.tk/", "having_At_Symbol"),
        ("http://good.com/redirect//evil.tk", "double_slash_redirecting"),
        ("http://secure-paypal.com", "Prefix_Suffix"),
        ("http://a.b.c.evil.com", "having_Sub_Domain"),
        ("http://example.com:8080", "port"),
        ("http://https-paypal.com", "HTTPS_token"),
    ],
)
def test_risky_conditions_are_negative(url, feature):
    assert lex(url)[feature] == -1


def test_clean_url_is_all_positive():
    assert all(v == 1 for v in lex("https://www.google.com").values())


def test_no_constant_features():
    """Every lexical feature must vary across inputs - no placeholders."""
    urls = [
        "https://www.google.com",
        "http://192.168.0.5/login.php",
        "http://bit.ly/x9f",
        "http://paypal.com@evil.tk/",
        "http://good.com/a//evil.tk",
        "http://secure-paypal.com",
        "http://a.b.c.evil.com",
        "http://example.com:8080",
        "http://https-paypal.com",
        "http://" + "x" * 90 + ".com/very/long/path/that/keeps/going/on",
    ]
    df = pd.DataFrame([lex(u) for u in urls])
    constant = [c for c in df.columns if df[c].nunique() == 1]
    assert not constant, f"these features never change: {constant}"


# -- the full tier must be able to produce every column it promises ----------

def test_content_features_cover_the_schema():
    html = """
    <html><head><link rel="icon" href="/favicon.ico">
    <link rel="stylesheet" href="/s.css"></head>
    <body><a href="/a">a</a><a href="/b">b</a>
    <img src="/i.png"><script src="/j.js"></script>
    <form action="/submit"></form></body></html>
    """
    feats = _content_features(html, "https://example.com/")
    produced = set(feats)
    expected = set(CONTENT_FEATURES) - {
        "SSLfinal_State", "age_of_domain", "Domain_registeration_length",
        "Abnormal_URL", "DNSRecord", "Redirect",
    }
    assert expected <= produced


def test_benign_page_scores_clean():
    html = """
    <html><head><link rel="icon" href="/favicon.ico"></head>
    <body><a href="/x">x</a><img src="/y.png">
    <form action="/submit"></form></body></html>
    """
    feats = _content_features(html, "https://example.com/")
    assert feats["URL_of_Anchor"] == 1
    assert feats["SFH"] == 1
    assert feats["Iframe"] == 1


def test_hostile_page_scores_dirty():
    html = """
    <html><body>
    <a href="https://evil.tk/1">1</a><a href="https://evil.tk/2">2</a>
    <a href="https://evil.tk/3">3</a>
    <form action="about:blank"></form>
    <iframe src="https://evil.tk"></iframe>
    </body></html>
    """
    feats = _content_features(html, "https://bank-login.com/")
    assert feats["URL_of_Anchor"] == -1
    assert feats["SFH"] == -1
    assert feats["Iframe"] == -1


def test_schema_is_internally_consistent():
    assert set(FULL_FEATURES) == set(LEXICAL_FEATURES) | set(CONTENT_FEATURES)
    assert len(FULL_FEATURES) == len(set(FULL_FEATURES))


# -- validation and SSRF -----------------------------------------------------

def test_ip_literal_accepted_not_rejected():
    n = normalize_url("http://192.168.1.1/login.php")
    assert is_valid_url(n) and n.is_ip_literal


def test_scheme_is_not_invented():
    assert normalize_url("example.com").scheme_was_supplied is False
    assert normalize_url("https://example.com").scheme_was_supplied is True


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "169.254.169.254"])
def test_internal_hosts_are_refused(host):
    ok, _ = is_safe_to_fetch(host)
    assert ok is False


@pytest.mark.parametrize("bad", ["", "   ", "notadomain", "http://", "ftp://x.com"])
def test_invalid_input_rejected(bad):
    assert not is_valid_url(normalize_url(bad))
