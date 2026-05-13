from difflib import SequenceMatcher
from typing import List

from services.schemas import CanonicalizationResult, DistortionReport


def metric_rows(report: DistortionReport) -> List[dict]:
    return [
        {
            "Metric": "Semantic similarity",
            "Score": round(report.semantic_similarity, 4),
            "What it means": "How close the overall meaning remains.",
        },
        {
            "Metric": "Token overlap",
            "Score": round(report.token_overlap, 4),
            "What it means": "How much vocabulary is shared after rewriting.",
        },
        {
            "Metric": "Entity preservation",
            "Score": round(report.entity_preservation, 4),
            "What it means": "Whether important named items were retained.",
        },
        {
            "Metric": "Length ratio",
            "Score": round(report.length_ratio, 4),
            "What it means": "How much the rewrite compresses or expands the text.",
        },
    ]


def risk_items(canonicalization: CanonicalizationResult) -> List[str]:
    if canonicalization.nuance_risks:
        return canonicalization.nuance_risks
    return ["No major nuance risks were flagged by the model."]


def highlight_text_diff(original_text: str, rewritten_text: str) -> tuple[str, str]:
    original_tokens = original_text.split()
    rewritten_tokens = rewritten_text.split()
    matcher = SequenceMatcher(a=original_tokens, b=rewritten_tokens)

    original_parts = []
    rewritten_parts = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        original_chunk = " ".join(original_tokens[i1:i2])
        rewritten_chunk = " ".join(rewritten_tokens[j1:j2])

        if tag == "equal":
            if original_chunk:
                original_parts.append(original_chunk)
            if rewritten_chunk:
                rewritten_parts.append(rewritten_chunk)
        else:
            if original_chunk:
                original_parts.append(f":red-background[{original_chunk}]")
            if rewritten_chunk:
                rewritten_parts.append(f":green-background[{rewritten_chunk}]")

    return " ".join(original_parts), " ".join(rewritten_parts)
