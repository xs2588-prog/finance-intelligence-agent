# Market Intelligence Agent

A portfolio-ready Python project that turns natural-language stock questions into concise, evidence-backed answers. It combines market prices, technical risk metrics, company news, and lightweight sentiment analysis behind one modular agent interface.

> Educational research tool only — not financial advice.

## Why this project

The original prototype was developed in Google Colab as an 86-cell notebook. This repository refactors that experiment into a testable Python package with explicit provider boundaries, credential-safe configuration, an offline demo notebook, a CLI, and a small REST API.

## Features

- Natural-language intent and ticker extraction
- Current-price and previous-close comparison
- Six-month trend, annualized volatility, and maximum drawdown
- Multi-stock risk comparison
- Finnhub company-news retrieval with relevance filtering
- Explainable lexicon sentiment baseline
- Swappable data providers for testing and future model integrations
- CLI and Flask API entry points

## Architecture

```text
User question
     |
     v
Ticker + intent router
     |
     +--> Yahoo Finance --> price / history --> risk metrics
     |
     +--> Finnhub -------> company news -----> sentiment
     |
     v
Structured AnalysisResult
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Add your own Finnhub key to `.env` only if you want news features. Price and technical analysis do not require it.

```bash
market-agent "How is AAPL trading?"
market-agent "Compare AAPL vs MSFT risk"
market-agent "Latest NVDA news"
```

Run the API:

```bash
flask --app app run
curl -X POST http://127.0.0.1:5000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"query":"Compare AAPL vs MSFT risk"}'
```

## Demo notebook

[`notebooks/portfolio_demo.ipynb`](notebooks/portfolio_demo.ipynb) is an offline, deterministic walkthrough. It uses dependency injection and fake providers, so reviewers can inspect the routing, analytics, and visual output without API keys or network access.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

## Design decisions

- **Credentials stay outside source control.** Secrets load from environment variables and `.env` is ignored.
- **Providers are injectable.** Tests and demos do not depend on live APIs.
- **Metrics remain inspectable.** The agent returns both readable text and structured evidence.
- **LLMs are optional.** A deterministic baseline keeps the repository lightweight and reproducible; FinBERT or a fine-tuned model can be added behind the sentiment interface.

## Limitations and roadmap

- Yahoo Finance is convenient rather than exchange-grade real-time data.
- The baseline sentiment model is intentionally simple and should not be treated as a trading signal.
- Next steps: FinBERT adapter, cached data layer, richer evaluation set, Docker deployment, and a small web UI.

## Security note

The source notebook contained embedded third-party credentials. They were removed from this repository. Any credentials previously exposed in a notebook should be revoked and replaced before further use.

