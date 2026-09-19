"""
URL normalisation and validation.

Changes from the original:

  * normalize_url no longer silently invents "https://". It records whether the
    scheme was supplied by the user, so no downstream feature can mistake our
    own default for evidence about the site. (SSLfinal_State is now decided by a
    real TLS handshake, not by a string prefix.)
  * IP-literal hosts are accepted instead of rejected. They were being thrown
    out by the domain regex, even though "URL uses a raw IP" is one of the
    signals the model is supposed to see.
  * Added is_safe_to_fetch(). Because the app now fetches pages, a user could
    otherwise point it at 127.0.0.1, 169.254.169.254 or an internal 10.x host
    and use the scanner as an SSRF proxy.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse

MAX_URL_LENGTH = 2048

_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
_HOSTNAME_RE = re.compile(rf"^{_LABEL}(?:\.{_LABEL})*\.[A-Za-z]{{2,63}}\.?$")


@dataclass
class NormalizedURL:
    url: str
    host: str
    scheme_was_supplied: bool
    is_ip_literal: bool
    # Normalisation rebuilds the URL from parsed parts, which discards any
    # "user@" prefix. That prefix is exactly what the having_At_Symbol feature
    # is meant to detect, so record it before it is dropped.
    has_userinfo: bool = False


def normalize_url(raw: str) -> NormalizedURL:
    raw = (raw or "").strip()
    raw = raw.strip("<>\"'")

    scheme_was_supplied = bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", raw))
    candidate = raw if scheme_was_supplied else "http://" + raw

    parsed = urlparse(candidate)
    host = (parsed.hostname or "").lower().rstrip(".")

    # International domains -> punycode, so "аpple.com" (Cyrillic а) is not
    # compared as if it were ASCII "apple.com".
    try:
        host_ascii = host.encode("idna").decode("ascii") if host else ""
    except (UnicodeError, UnicodeDecodeError):
        host_ascii = host

    is_ip_literal = False
    try:
        ipaddress.ip_address(host_ascii)
        is_ip_literal = True
    except ValueError:
        pass

    netloc = host_ascii
    if parsed.port:
        netloc = f"{host_ascii}:{parsed.port}"

    rebuilt = urlunparse(
        (
            parsed.scheme.lower(),
            netloc,
            parsed.path or "/",
            parsed.params,
            parsed.query,
            "",  # fragments are never sent to servers; drop them
        )
    )

    return NormalizedURL(
        url=rebuilt,
        host=host_ascii,
        scheme_was_supplied=scheme_was_supplied,
        is_ip_literal=is_ip_literal,
        has_userinfo=bool(parsed.username or parsed.password),
    )


def is_valid_url(n: NormalizedURL) -> bool:
    if not n.host or len(n.url) > MAX_URL_LENGTH:
        return False
    if urlparse(n.url).scheme not in ("http", "https"):
        return False
    if n.is_ip_literal:
        return True
    if len(n.host) > 253:
        return False
    return bool(_HOSTNAME_RE.match(n.host))


def _is_private(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def is_safe_to_fetch(host: str) -> tuple[bool, str]:
    """Resolve the host and refuse anything pointing at internal space."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False, "host does not resolve"

    for info in infos:
        ip = info[4][0]
        try:
            if _is_private(ip):
                return False, f"resolves to internal address {ip}"
        except ValueError:
            return False, "unparseable address"

    return True, ""
