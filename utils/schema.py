"""
Single source of truth for which dataset features this project can actually
compute at prediction time.

The original code fed the model 13 hardcoded constants, including the two most
important features in the forest (SSLfinal_State and URL_of_Anchor). A feature
you cannot compute must be dropped from the model, not faked.

Two tiers:

  LEXICAL_FEATURES  - derivable from the URL string alone. Always available.
  CONTENT_FEATURES  - require a network probe (DNS, TLS, WHOIS, page fetch).
                      Available only when the site is reachable.

  DROPPED_FEATURES  - present in the CSV but not computable without a paid or
                      unavailable third-party service. These are excluded from
                      both models rather than hardcoded.
"""

LEXICAL_FEATURES = [
    "having_IP_Address",
    "URL_Length",
    "Shortining_Service",
    "having_At_Symbol",
    "double_slash_redirecting",
    "Prefix_Suffix",
    "having_Sub_Domain",
    "port",
    "HTTPS_token",
]

CONTENT_FEATURES = [
    "SSLfinal_State",
    "Domain_registeration_length",
    "Favicon",
    "Request_URL",
    "URL_of_Anchor",
    "Links_in_tags",
    "SFH",
    "Submitting_to_email",
    "Abnormal_URL",
    "Redirect",
    "on_mouseover",
    "RightClick",
    "popUpWidnow",
    "Iframe",
    "age_of_domain",
    "DNSRecord",
]

FULL_FEATURES = LEXICAL_FEATURES + CONTENT_FEATURES

# Needed a service we don't have (Alexa rank, PageRank, Google index status,
# inbound link counts, PhishTank/StopBadware lists). Excluded on purpose.
DROPPED_FEATURES = [
    "web_traffic",
    "Page_Rank",
    "Google_Index",
    "Links_pointing_to_page",
    "Statistical_report",
]

TARGET = "Result"

# Dataset label convention.
PHISHING = -1
LEGITIMATE = 1
