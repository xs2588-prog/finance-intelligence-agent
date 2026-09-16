import math
import re

from flask import Flask, jsonify, render_template, request

from market_agent.analytics import technical_metrics
from market_agent.cli import build_agent


app = Flask(__name__)
agent = build_agent()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/dashboard/<ticker>")
def dashboard(ticker):
    ticker = ticker.upper().strip()
    if not re.fullmatch(r"[A-Z]{1,5}", ticker):
        return jsonify({"error": "invalid ticker"}), 400
    try:
        snapshot = agent.market_data.price(ticker)
        history = agent.market_data.history(ticker, period="6mo")
        metrics = technical_metrics(history)
        closes = history["Close"].astype(float).tail(126)
        points = [
            {"date": str(index.date()) if hasattr(index, "date") else str(index), "close": round(value, 2)}
            for index, value in closes.items()
        ]
        clean_metrics = {
            key: None if isinstance(value, float) and math.isnan(value) else value
            for key, value in metrics.items()
        }
        return jsonify({
            "ticker": ticker,
            "price": round(snapshot.price, 2),
            "change_pct": round(snapshot.change_pct, 2),
            "as_of": snapshot.as_of.isoformat(),
            "metrics": clean_metrics,
            "history": points,
        })
    except (ValueError, KeyError, IndexError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/analyze")
def analyze():
    query = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400
    try:
        result = agent.ask(query)
        return jsonify({"ticker": result.ticker, "intent": result.intent, "answer": result.answer})
    except (ValueError, KeyError, IndexError) as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)
