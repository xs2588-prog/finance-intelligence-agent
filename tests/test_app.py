import unittest

import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Market Intelligence Agent", response.data)

    def test_analyze_requires_query(self):
        response = self.client.post("/analyze", json={})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
