import unittest

import app
from tests.test_agent import FakeMarketData


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Finance Intelligence Agent", response.data)

    def test_analyze_requires_query(self):
        response = self.client.post("/analyze", json={})
        self.assertEqual(response.status_code, 400)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.json, {"status": "ok"})

    def test_dashboard(self):
        original = app.agent.market_data
        app.agent.market_data = FakeMarketData()
        try:
            response = self.client.get("/api/dashboard/AAPL")
        finally:
            app.agent.market_data = original
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["ticker"], "AAPL")
        self.assertEqual(len(response.json["history"]), 40)


if __name__ == "__main__":
    unittest.main()
