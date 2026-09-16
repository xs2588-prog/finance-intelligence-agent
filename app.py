from flask import Flask, jsonify, request

from market_agent.cli import build_agent


app = Flask(__name__)
agent = build_agent()


@app.post("/analyze")
def analyze():
    query = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400
    try:
        result = agent.ask(query)
        return jsonify({"ticker": result.ticker, "intent": result.intent, "answer": result.answer})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)

