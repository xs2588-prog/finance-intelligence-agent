from __future__ import annotations

import re


ALIASES = {
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "NVIDIA": "NVDA",
    "TESLA": "TSLA",
    "AMAZON": "AMZN",
    "GOOGLE": "GOOGL",
    "META": "META",
}

STOPWORDS = {
    "A", "AI", "AND", "ARE", "FOR", "HOW", "IS", "NEWS", "PRICE",
    "STOCK", "THE", "TODAY", "WHAT", "WHY",
}


def extract_tickers(query: str) -> list[str]:
    upper = query.upper()
    found = [ticker for company, ticker in ALIASES.items() if company in upper]
    tokens = re.findall(r"\$?[A-Za-z]{1,5}", query)
    candidates = [token.lstrip("$") for token in tokens if token.startswith("$") or token.isupper()]
    for candidate in candidates:
        if candidate not in STOPWORDS and candidate not in found:
            found.append(candidate)
    return found


def detect_intent(query: str) -> str:
    q = query.lower()
    if any(word in q for word in ("compare", " versus ", " vs ")):
        return "compare"
    if any(word in q for word in ("news", "headline", "catalyst", "happened")):
        return "news"
    if any(word in q for word in ("sentiment", "mood", "positive", "negative")):
        return "sentiment"
    if any(word in q for word in ("risk", "volatility", "drawdown")):
        return "risk"
    if any(word in q for word in ("technical", "rsi", "moving average", "trend")):
        return "technical"
    return "price"
