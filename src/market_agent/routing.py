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
    "苹果": "AAPL",
    "微软": "MSFT",
    "英伟达": "NVDA",
    "特斯拉": "TSLA",
    "亚马逊": "AMZN",
    "谷歌": "GOOGL",
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
    if any(word in q for word in ("compare", " versus ", " vs ", "比较", "对比")):
        return "compare"
    if any(word in q for word in ("news", "headline", "catalyst", "happened", "新闻", "消息", "催化剂")):
        return "news"
    if any(word in q for word in ("sentiment", "mood", "positive", "negative", "情绪", "正面", "负面")):
        return "sentiment"
    if any(word in q for word in ("risk", "volatility", "drawdown", "风险", "波动", "回撤")):
        return "risk"
    if any(word in q for word in ("technical", "rsi", "moving average", "trend", "技术", "均线", "趋势")):
        return "technical"
    return "price"
