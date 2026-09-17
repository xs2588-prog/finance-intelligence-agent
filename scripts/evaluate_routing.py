"""Evaluate deterministic intent routing and ticker extraction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from finance_agent.routing import detect_intent, extract_tickers


ROOT = Path(__file__).resolve().parents[1]


def evaluate(cases: list[dict[str, object]]) -> dict[str, object]:
    details = []
    intent_correct = 0
    ticker_correct = 0
    joint_correct = 0

    for case in cases:
        query = str(case["query"])
        expected_intent = str(case["intent"])
        expected_tickers = list(case["tickers"])
        predicted_intent = detect_intent(query)
        predicted_tickers = extract_tickers(query)
        intent_ok = predicted_intent == expected_intent
        ticker_ok = predicted_tickers == expected_tickers
        intent_correct += int(intent_ok)
        ticker_correct += int(ticker_ok)
        joint_correct += int(intent_ok and ticker_ok)
        details.append(
            {
                "query": query,
                "expected": {"intent": expected_intent, "tickers": expected_tickers},
                "predicted": {"intent": predicted_intent, "tickers": predicted_tickers},
                "passed": intent_ok and ticker_ok,
            }
        )

    total = len(cases)
    return {
        "dataset": "evaluation/routing_cases.json",
        "case_count": total,
        "metrics": {
            "intent_accuracy": intent_correct / total,
            "ticker_exact_match": ticker_correct / total,
            "joint_exact_match": joint_correct / total,
        },
        "failures": [row for row in details if not row["passed"]],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/routing_cases.json")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation/results.json")
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text())
    results = evaluate(cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results["metrics"], indent=2))
    print(f"cases={results['case_count']} failures={len(results['failures'])}")


if __name__ == "__main__":
    main()
