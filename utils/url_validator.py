from urllib.parse import urlparse
import re

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        if not parsed.scheme or not parsed.netloc:
            return False

        domain = parsed.netloc

        if "." not in domain:
            return False

        domain_regex = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(domain_regex, domain))

    except:
        return False
