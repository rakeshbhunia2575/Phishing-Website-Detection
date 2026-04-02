import re
import tldextract
from urllib.parse import urlparse

def extract_features(url: str) -> dict:
    features = {}

    features["URL_Length"] = len(url)
    features["having_At_Symbol"] = 1 if "@" in url else 0
    features["having_IP_Address"] = 1 if re.search(r"\d+\.\d+\.\d+\.\d+", url) else 0
    features["double_slash_redirecting"] = 1 if url.count("//") > 1 else 0

    extracted = tldextract.extract(url)
    features["Prefix_Suffix"] = 1 if "-" in extracted.domain else 0
    features["having_Sub_Domain"] = len(extracted.subdomain.split(".")) if extracted.subdomain else 0

    parsed = urlparse(url)
    features["HTTPS_token"] = 1 if parsed.scheme == "https" else 0

    return features
