from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class PriceSnapshot:
    ticker: str
    price: float
    previous_close: float
    as_of: datetime

    @property
    def change_pct(self) -> float:
        return (self.price / self.previous_close - 1) * 100


@dataclass(frozen=True)
class NewsItem:
    headline: str
    summary: str = ""
    source: str = ""
    published_at: datetime | None = None
    url: str = ""


@dataclass(frozen=True)
class AnalysisResult:
    ticker: str
    intent: str
    answer: str
    evidence: dict[str, object] = field(default_factory=dict)

