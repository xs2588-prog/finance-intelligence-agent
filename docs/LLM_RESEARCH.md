# LLM research track

The original Colab research prototype used a managed fine-tuning artifact with
LoRA/PEFT adapter checkpoints and a 15-label financial intent taxonomy. It also
used `ProsusAI/finbert` for article-level financial sentiment. Large model
weights, proprietary training data, and credentials are not committed here.

## Constrained LoRA inference

`src/finance_agent/lora_intent.py` preserves the prototype's inference contract:

- deterministic decoding with at most four generated tokens;
- exactly one label from an explicit allowlist;
- parser validation and an `analysis` fallback for malformed output;
- no model-generated prices or risk metrics.

The public application defaults to a deterministic rules-based router so it can
run locally without GPU memory or model downloads. A compatible PEFT model can
be loaded by the caller and passed to `predict_intent`.

## FinBERT boundary

In the research notebook, FinBERT supplied the sentiment label while the causal
language model only explained the already-computed result. This separation keeps
free-form generation from silently overriding the classifier. The lightweight
web application uses an inspectable lexicon baseline; FinBERT remains an optional
model integration rather than a required runtime dependency.

## Evaluation policy

The notebook contains model artifacts but does not preserve enough information
to reproduce a trustworthy fine-tuning accuracy value. This repository therefore
does not claim one. Instead, `evaluation/routing_cases.json` and
`scripts/evaluate_routing.py` publish a reproducible baseline evaluation for
intent routing and ticker extraction. Future adapter results should be added only
with the exact model, dataset split, seed, and scoring script recorded.
