from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from .agent import MarketAgent
from .providers import FinnhubNewsProvider, YahooFinanceProvider


def build_agent() -> MarketAgent:
    load_dotenv()
    news = FinnhubNewsProvider() if os.getenv("FINNHUB_API_KEY") else None
    return MarketAgent(YahooFinanceProvider(), news)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a stock research question.")
    parser.add_argument("query", nargs="+", help="e.g. 'Compare AAPL vs MSFT risk'")
    args = parser.parse_args()
    print(build_agent().ask(" ".join(args.query)).answer)


if __name__ == "__main__":
    main()

