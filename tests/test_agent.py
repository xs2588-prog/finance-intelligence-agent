from datetime import datetime, timezone
import unittest

import pandas as pd

from finance_agent import FinanceAgent
from finance_agent.models import NewsItem, PriceSnapshot
from finance_agent.routing import detect_intent, extract_tickers


class FakeMarketData:
    def price(self, ticker):
        return PriceSnapshot(ticker, 105.0, 100.0, datetime.now(timezone.utc))

    def history(self, ticker, period="6mo"):
        return pd.DataFrame({"Close": [100 + i * (1 if ticker == "AAPL" else 2) for i in range(40)]})


class FakeNews:
    def company_news(self, ticker, days=7):
        return [NewsItem(f"{ticker} reports strong growth and record profit")]


class FinanceAgentTests(unittest.TestCase):
    def test_routing_and_aliases(self):
        self.assertEqual(extract_tickers("Compare Apple vs MSFT risk"), ["AAPL", "MSFT"])
        self.assertEqual(detect_intent("latest NVDA headlines"), "news")
        self.assertEqual(extract_tickers("比较苹果和微软的风险"), ["AAPL", "MSFT"])
        self.assertEqual(detect_intent("比较苹果和微软的风险"), "compare")

    def test_price_answer(self):
        result = FinanceAgent(FakeMarketData()).ask("AAPL price")
        self.assertEqual(result.intent, "price")
        self.assertIn("+5.00%", result.answer)

    def test_sentiment_answer(self):
        result = FinanceAgent(FakeMarketData(), FakeNews()).ask("AAPL sentiment")
        self.assertIn("positive", result.answer)


if __name__ == "__main__":
    unittest.main()
