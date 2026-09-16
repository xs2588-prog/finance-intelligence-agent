from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Protocol

from .models import NewsItem, PriceSnapshot


class MarketDataProvider(Protocol):
    def price(self, ticker: str) -> PriceSnapshot: ...
    def history(self, ticker: str, period: str = "6mo"): ...


class NewsProvider(Protocol):
    def company_news(self, ticker: str, days: int = 7) -> list[NewsItem]: ...


class YahooFinanceProvider:
    def price(self, ticker: str) -> PriceSnapshot:
        import yfinance as yf

        data = yf.Ticker(ticker).history(period="5d", interval="1d")
        if data is None or len(data) < 2:
            raise ValueError(f"No recent price data found for {ticker}.")
        return PriceSnapshot(
            ticker=ticker,
            price=float(data["Close"].iloc[-1]),
            previous_close=float(data["Close"].iloc[-2]),
            as_of=data.index[-1].to_pydatetime(),
        )

    def history(self, ticker: str, period: str = "6mo"):
        import yfinance as yf

        data = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
        if data is None or data.empty:
            raise ValueError(f"No historical data found for {ticker}.")
        if getattr(data.columns, "nlevels", 1) > 1:
            data.columns = data.columns.get_level_values(0)
        return data


class FinnhubNewsProvider:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY is required for news analysis.")
        import finnhub

        self._client = finnhub.Client(api_key=api_key)

    def company_news(self, ticker: str, days: int = 7) -> list[NewsItem]:
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=days)
        raw = self._client.company_news(ticker, _from=start.isoformat(), to=end.isoformat()) or []
        items = []
        for item in raw[:30]:
            related = {part.strip().upper() for part in (item.get("related") or "").split(",")}
            if related and ticker.upper() not in related:
                continue
            timestamp = item.get("datetime")
            items.append(NewsItem(
                headline=item.get("headline", ""),
                summary=item.get("summary", ""),
                source=item.get("source", ""),
                published_at=datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else None,
                url=item.get("url", ""),
            ))
        return items

