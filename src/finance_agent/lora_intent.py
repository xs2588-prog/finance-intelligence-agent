"""Optional constrained inference for a local LoRA intent adapter.

Model weights are intentionally not committed. This module documents the
inference contract used by the research prototype while keeping the default
application lightweight and deterministic.
"""

from __future__ import annotations

from collections.abc import Sequence


INTENT_LABELS = (
    "price_now",
    "news",
    "sentiment",
    "fundamentals",
    "technical_full",
    "technical_indicator",
    "technical_ma_check",
    "technical_trend",
    "technical_risk",
    "return",
    "compare",
    "bull",
    "bear",
    "risk",
    "analysis",
)


def build_intent_prompt(query: str, labels: Sequence[str] = INTENT_LABELS) -> str:
    return (
        "You are a financial intent classifier.\n\n"
        "Choose exactly ONE intent from this list:\n"
        + ", ".join(labels)
        + f"\n\nUser query:\n{query}\n\nIntent:"
    )


def parse_intent(text: str, labels: Sequence[str] = INTENT_LABELS) -> str:
    """Return one validated label or the safe fallback ``analysis``."""
    tail = text.split("Intent:", 1)[-1].strip()
    prediction = tail.split()[0].lower().strip(".,:;") if tail else ""
    return prediction if prediction in labels else "analysis"


def predict_intent(query: str, model, tokenizer) -> str:
    """Run deterministic, bounded generation with a loaded PEFT model."""
    import torch

    inputs = tokenizer(
        build_intent_prompt(query),
        return_tensors="pt",
        truncation=True,
        max_length=256,
    ).to(model.device)
    newline_ids = tokenizer.encode("\n", add_special_tokens=False)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=4,
            do_sample=False,
            eos_token_id=newline_ids[0] if newline_ids else tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )
    return parse_intent(tokenizer.decode(outputs[0], skip_special_tokens=True))
