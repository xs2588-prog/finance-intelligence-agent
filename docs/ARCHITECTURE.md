# Architecture

## System overview

The application uses a layered architecture so that user experience, orchestration,
analytics, and third-party data access can evolve independently.

```mermaid
flowchart LR
    U["Browser user"] -->|"question or ticker"| W["Flask web layer"]
    W --> R["Ticker and intent router"]
    R --> A["FinanceAgent orchestrator"]
    W --> T["Thesis engine"]
    A --> Y["Yahoo Finance provider"]
    A --> F["Finnhub news provider"]
    A --> M["Analytics layer"]
    Y -->|"price and OHLC history"| A
    F -->|"company news"| A
    M -->|"volatility, drawdown, trend, sentiment"| A
    T --> Y
    T --> F
    T --> M
    T -->|"bull case, bear case, judge verdict"| W
    A -->|"AnalysisResult"| W
    W -->|"JSON"| U
    U -->|"localStorage"| L["Browser watchlist"]
```

## Request paths

### Natural-language analysis

```text
POST /analyze
  -> validate request
  -> extract ticker aliases and symbols
  -> classify intent
  -> select price, technical, comparison, news, or sentiment workflow
  -> call an injected provider
  -> calculate transparent metrics
  -> return a concise answer
```

### Dashboard data

```text
GET /api/dashboard/<ticker>
  -> validate ticker
  -> fetch latest and six-month market data
  -> calculate 20-day trend, annualized volatility, and maximum drawdown
  -> return chart-ready JSON
  -> render metric cards and canvas chart in the browser
```

### Investment thesis challenge

```text
POST /api/thesis
  -> validate thesis and ticker
  -> collect current price and six-month history
  -> construct Bull and Bear evidence from momentum, trend, risk, and optional news
  -> score the evidence with a bounded, deterministic Judge
  -> return source labels, dates, confidence, methodology, and unknowns
```

The Judge does not invent financial facts or hide uncertainty behind prose. Its
confidence is capped, its evidence scores are inspectable, and missing news,
valuation, or fundamental evidence is shown to the user as an explicit blind spot.

## Layers and ownership

| Layer | Files | Responsibility |
|---|---|---|
| Web/API | `app.py`, `templates/index.html` | HTTP validation, JSON responses, dashboard UI |
| Orchestration | `src/finance_agent/agent.py` | Chooses and combines analysis workflows |
| Routing | `src/finance_agent/routing.py` | Company aliases, ticker extraction, and intent rules |
| Analytics | `src/finance_agent/analytics.py` | Deterministic risk and sentiment calculations |
| Thesis engine | `src/finance_agent/thesis.py` | Builds opposing evidence cases and a transparent verdict |
| Providers | `src/finance_agent/providers.py` | Isolates Yahoo Finance and Finnhub integrations |
| Contracts | `src/finance_agent/models.py` | Typed inputs and result objects |
| Verification | `tests/` | Offline provider, routing, API, and UI smoke tests |

## Design decisions

1. **Dependency injection:** `FinanceAgent` accepts market-data and news providers.
   Tests therefore run without network access, and providers can be replaced later.
2. **Deterministic analytics:** financial metrics are ordinary Python calculations;
   an LLM is not allowed to invent prices, volatility, or drawdown values.
3. **Optional credentials:** price workflows work without secrets. Finnhub news is
   enabled only when `FINNHUB_API_KEY` exists in the environment.
4. **Dual output:** human-readable answers serve the chat experience while
   structured dashboard JSON supports charts and future clients.
5. **Client-side watchlist:** watchlist state stays in `localStorage`; the server
   stores no personal portfolio information.
6. **Adversarial research:** the thesis workflow always constructs opposing cases
   and reports missing evidence instead of optimizing for agreement with the user.

## Runtime topology

The current project runs locally as a stateless Flask application. Each request
fetches the data it needs from the selected provider. A future hosted version
could add caching, rate limiting, observability, and a durable user-account or
watchlist service without changing the analysis layer.
