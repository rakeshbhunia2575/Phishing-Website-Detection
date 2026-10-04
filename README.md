
# PhishyLink: Phishing Website Detection  [![PhishyLink live demo](assets/live-demo-badge.svg)](https://phishing-website-detection-ym5d.onrender.com/)

PhishyLink checks a web link for signs of phishing before you click it. Paste a URL into the web page and you get a verdict (**Phishing Website** or **Legitimate Website**), the main reason, notes about how reliable the check was, and a plain-language message telling you what to do. Every check is saved, and the page shows your recent checks in a dropdown.

> PhishyLink gives guidance, not a guarantee. When in doubt, never enter passwords or payment details.

---

## Table of contents

1. [Features](#features)
2. [How it works](#how-it-works)
3. [Tech stack](#tech-stack)
4. [Project structure](#project-structure)
5. [Limitations](#limitations)
6. [Security notes](#security-notes)
7. [License](#license)

---

## Features

- Machine-learning phishing detection with a confidence score
- Two detection tiers: a **full** check (link, certificate, domain, page content) and a **lexical** fallback (link text only) when a site cannot be reached
- A clear verdict, reason and notes for every result
- Colour-coded advice message: green (safe), orange (be careful), red (avoid)
- History of previous checks in a dropdown, newest first, showing the URL, label and confidence
- Responsive page that works on phones, tablets and desktops
- Single deployment for the page and the API: the frontend is served by Spring Boot

## How it works

```
 Browser (HTML / CSS / JS)
        │   POST /api/predict   { "urlReq": "https://..." }
        ▼
 Spring Boot  ── stores each result ──►  MySQL
        │   POST /predict       { "url": "https://..." }
        ▼
 FastAPI + scikit-learn model
```

1. The user pastes a link in the page.
2. Spring Boot sends it to the FastAPI service.
3. FastAPI normalises and validates the URL, extracts features and runs the model.
   - **Full tier:** when the site responds, the model uses the link's features plus live checks such as the HTTPS certificate, WHOIS domain age, DNS record and page content (forms, iframes, external links).
   - **Lexical tier:** when the site does not respond, only features of the URL text are used (IP address, length, `@` sign, hyphens, subdomains, shortening services, odd ports and similar). The result is then weaker evidence, and the notes say so.
4. Spring Boot saves unique URLs to MySQL and returns the verdict with a message:
   - **Phishing Website**: "The website is malicious. Avoid it." (red)
   - **Legitimate Website, full tier**: "This website is good to go." (green)
   - **Legitimate Website, lexical tier**: "The website could be malicious, try to avoid it." (orange)

FastAPI refuses to fetch private, loopback and other internal addresses, so the checker cannot be used to probe your own network.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (no framework) |
| Backend API | Java 21, Spring Boot, Spring Web MVC, Spring Data JPA, Maven |
| Database | MySQL |
| ML service | Python 3.12, FastAPI, Uvicorn, scikit-learn, pandas, joblib |
| Deployment | Docker, Render (services), Aiven (MySQL) |

## Project structure

```
Phishing-Website-Detection/
├── README.md
├── .gitignore
│
├── PhishingWebsiteDetection/                 Spring Boot service and frontend
│   ├── Dockerfile
│   ├── pom.xml
│   ├── mvnw, mvnw.cmd, .mvn/
│   └── src/main/
│       ├── java/com/PhishyLink/PhishingWebsiteDetection/
│       │   ├── PhishingWebsiteDetectionApplication.java
│       │   ├── controller/      PredictionController
│       │   ├── dto/             RequestDto, ResponseDto
│       │   ├── entity/          UrlData, Features, FastApiResponse
│       │   ├── exceptions/      GlobalExceptionHandler, InvalidUrlException, OutOfServiceException
│       │   ├── mapping/         MapToResponseDto, MaptoUrl
│       │   ├── repository/      PredictionRepository, FeaturesData
│       │   └── service/         PredictionService
│       └── resources/
│           ├── application.properties
│           └── static/          index.html, style.css, script.js, favicon.png
│
└── FastApiModel/                             FastAPI model service
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py                           API endpoints
        ├── models/                           trained .pkl models and column lists
        ├── services/predict.py               prediction logic and reasons
        └── utils/                            URL validation and feature extraction
```

## Limitations

- Results are probabilistic. Both false positives and false negatives are possible.
- The lexical tier sees only the link text, so a single suspicious signal (such as an IP address) may not be enough to flag a link. Its results are weaker evidence.
- WHOIS lookups can fail or be blocked on some hosts, which reduces the information available to the full tier.
- Free hosting adds cold-start delays and memory limits.

## Security notes

- No secrets are stored in the repository. Use environment variables.
- Use a dedicated database user with permissions on this database only, and a strong, unique password.
- The FastAPI service is reachable on the internet when deployed this way. For anything beyond a demo, add authentication between the two services.
