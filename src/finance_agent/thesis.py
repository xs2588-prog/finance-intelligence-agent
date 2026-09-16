from __future__ import annotations

from datetime import datetime, timezone

from .analytics import lexicon_sentiment, technical_metrics


def _evidence(title: str, detail: str, source: str, as_of: str, kind: str) -> dict[str, str]:
    return {"title": title, "detail": detail, "source": source, "as_of": as_of, "kind": kind}


def analyze_thesis(statement: str, ticker: str, market_data, news=None) -> dict[str, object]:
    """Challenge an investment thesis with transparent, deterministic evidence."""
    snapshot = market_data.price(ticker)
    history = market_data.history(ticker, period="6mo")
    metrics = technical_metrics(history)
    close = history["Close"].astype(float)
    six_month_return = float(close.iloc[-1] / close.iloc[0] - 1) if len(close) > 1 else 0.0
    as_of = snapshot.as_of.isoformat()

    bull: list[dict[str, str]] = []
    bear: list[dict[str, str]] = []
    unknowns: list[str] = []

    if six_month_return >= 0:
        bull.append(_evidence(
            "Positive price momentum",
            f"The six-month closing-price return is {six_month_return:+.1%}.",
            "Yahoo Finance market history", as_of, "market",
        ))
    else:
        bear.append(_evidence(
            "Negative price momentum",
            f"The six-month closing-price return is {six_month_return:+.1%}.",
            "Yahoo Finance market history", as_of, "market",
        ))

    trend_target = bull if metrics["trend"] == "above" else bear
    trend_target.append(_evidence(
        f"Price is {metrics['trend']} its 20-day average",
        f"Last close: ${metrics['last_close']:.2f}; 20-day average: ${metrics['ma20']:.2f}.",
        "Calculated from Yahoo Finance history", as_of, "technical",
    ))

    volatility = float(metrics["annualized_volatility"])
    drawdown = float(metrics["max_drawdown"])
    if volatility <= 0.30:
        bull.append(_evidence(
            "Contained historical volatility",
            f"Annualized six-month volatility is {volatility:.1%}.",
            "Calculated from daily returns", as_of, "risk",
        ))
    else:
        bear.append(_evidence(
            "Elevated historical volatility",
            f"Annualized six-month volatility is {volatility:.1%}.",
            "Calculated from daily returns", as_of, "risk",
        ))

    if drawdown <= -0.20:
        bear.append(_evidence(
            "Material peak-to-trough loss",
            f"Maximum six-month drawdown is {drawdown:.1%}.",
            "Calculated from closing prices", as_of, "risk",
        ))
    else:
        bull.append(_evidence(
            "Limited recent drawdown",
            f"Maximum six-month drawdown is {drawdown:.1%}.",
            "Calculated from closing prices", as_of, "risk",
        ))

    news_status = "unavailable"
    if news is not None:
        items = news.company_news(ticker)
        sentiment = lexicon_sentiment(items)
        news_status = "available"
        target = bull if sentiment["score"] > 0 else bear if sentiment["score"] < 0 else None
        if target is not None:
            target.append(_evidence(
                f"{sentiment['label'].title()} recent news tone",
                f"Keyword analysis scored {sentiment['article_count']} recent articles at {sentiment['score']:+d}.",
                "Finnhub company news", datetime.now(timezone.utc).isoformat(), "news",
            ))
        for item in items[:3]:
            if item.headline:
                bull_or_bear = bull if any(word in item.headline.lower() for word in ("growth", "beat", "record", "upgrade")) else bear
                bull_or_bear.append(_evidence(
                    item.headline,
                    item.summary[:220] or "Recent company headline.",
                    item.source or "Finnhub", item.published_at.isoformat() if item.published_at else as_of, "news",
                ))
    else:
        unknowns.append("News catalysts are not evaluated because FINNHUB_API_KEY is not configured.")

    if not bull:
        bull.append(_evidence(
            "Potential contrarian setup",
            "Weak recent market behavior may lower expectations, but fundamentals are needed to test whether the selloff is excessive.",
            "Interpretation of observed market history", as_of, "counterpoint",
        ))
    if not bear:
        bear.append(_evidence(
            "Fundamental claim remains unverified",
            "Positive price behavior does not prove the thesis's revenue, margin, competitive, or valuation assumptions.",
            "Evidence coverage audit", as_of, "counterpoint",
        ))

    unknowns.extend([
        "This version does not yet evaluate valuation multiples or analyst estimates.",
        "Price behavior alone cannot verify the thesis's fundamental business assumptions.",
    ])

    bull_score = min(100, 20 * len(bull))
    bear_score = min(100, 20 * len(bear))
    evidence_count = len(bull) + len(bear)
    confidence = min(85, 35 + evidence_count * 7 + (8 if news_status == "available" else 0))
    balance = bull_score - bear_score
    verdict = "supported" if balance >= 20 else "challenged" if balance <= -20 else "mixed"
    verdict_text = {
        "supported": "Current evidence leans supportive, but the thesis still needs fundamental validation.",
        "challenged": "Current evidence raises meaningful counterarguments to the thesis.",
        "mixed": "Current evidence is mixed and does not justify a high-conviction conclusion.",
    }[verdict]

    return {
        "ticker": ticker,
        "thesis": statement,
        "verdict": verdict,
        "verdict_text": verdict_text,
        "confidence": confidence,
        "bull_score": bull_score,
        "bear_score": bear_score,
        "bull_case": bull,
        "bear_case": bear,
        "unknowns": unknowns,
        "methodology": "Rule-based judge using price momentum, trend, volatility, drawdown, and optional news tone.",
        "news_status": news_status,
    }
