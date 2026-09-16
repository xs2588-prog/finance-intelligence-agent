from __future__ import annotations

from .analytics import lexicon_sentiment, technical_metrics
from .models import AnalysisResult
from .routing import detect_intent, extract_tickers


class MarketAgent:
    def __init__(self, market_data, news=None):
        self.market_data = market_data
        self.news = news

    def ask(self, query: str) -> AnalysisResult:
        tickers = extract_tickers(query)
        if not tickers:
            raise ValueError("Include a ticker such as AAPL, MSFT, NVDA, or TSLA.")
        intent = detect_intent(query)
        if intent == "compare":
            return self._compare(tickers)
        ticker = tickers[0]
        if intent in {"news", "sentiment"}:
            return self._news(ticker, intent)
        if intent in {"risk", "technical"}:
            return self._technical(ticker, intent)
        snapshot = self.market_data.price(ticker)
        answer = f"{ticker} is {snapshot.change_pct:+.2f}% versus the previous close at ${snapshot.price:.2f}."
        return AnalysisResult(ticker, intent, answer, {"snapshot": snapshot})

    def _compare(self, tickers: list[str]) -> AnalysisResult:
        if len(tickers) < 2:
            raise ValueError("A comparison needs at least two tickers.")
        rows = []
        for ticker in tickers[:4]:
            metrics = technical_metrics(self.market_data.history(ticker))
            rows.append((ticker, metrics))
        best = min(rows, key=lambda row: row[1]["annualized_volatility"])
        answer = f"{best[0]} has the lowest annualized volatility in this comparison ({best[1]['annualized_volatility']:.1%})."
        return AnalysisResult(",".join(tickers[:4]), "compare", answer, {"metrics": dict(rows)})

    def _technical(self, ticker: str, intent: str) -> AnalysisResult:
        metrics = technical_metrics(self.market_data.history(ticker))
        answer = (
            f"{ticker} trades {metrics['trend']} its 20-day moving average. "
            f"Annualized volatility is {metrics['annualized_volatility']:.1%}; "
            f"maximum six-month drawdown is {metrics['max_drawdown']:.1%}."
        )
        return AnalysisResult(ticker, intent, answer, metrics)

    def _news(self, ticker: str, intent: str) -> AnalysisResult:
        if self.news is None:
            raise ValueError("News analysis requires FINNHUB_API_KEY.")
        items = self.news.company_news(ticker)
        if intent == "sentiment":
            sentiment = lexicon_sentiment(items)
            answer = f"Recent {ticker} news sentiment is {sentiment['label']} across {sentiment['article_count']} articles."
            return AnalysisResult(ticker, intent, answer, {"sentiment": sentiment, "news": items})
        headlines = [item.headline for item in items[:5]]
        answer = "\n".join(f"- {headline}" for headline in headlines) or f"No recent news found for {ticker}."
        return AnalysisResult(ticker, intent, answer, {"news": items})

