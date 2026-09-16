from __future__ import annotations

import math


POSITIVE_WORDS = {"beat", "growth", "profit", "record", "upgrade", "surge", "strong"}
NEGATIVE_WORDS = {"cut", "decline", "downgrade", "loss", "probe", "risk", "weak"}


def technical_metrics(history) -> dict[str, float | str]:
    close = history["Close"].astype(float)
    returns = close.pct_change().dropna()
    ma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else math.nan
    annualized_volatility = float(returns.std() * math.sqrt(252)) if len(returns) else math.nan
    rolling_peak = close.cummax()
    max_drawdown = float((close / rolling_peak - 1).min())
    trend = "above" if not math.isnan(ma20) and close.iloc[-1] > ma20 else "below"
    return {
        "last_close": float(close.iloc[-1]),
        "ma20": float(ma20),
        "trend": trend,
        "annualized_volatility": annualized_volatility,
        "max_drawdown": max_drawdown,
    }


def lexicon_sentiment(news_items) -> dict[str, float | str | int]:
    score = 0
    for item in news_items:
        words = set((item.headline + " " + item.summary).lower().split())
        score += len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"label": label, "score": score, "article_count": len(news_items)}

