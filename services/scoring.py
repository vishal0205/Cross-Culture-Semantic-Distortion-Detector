import re
from typing import Set

from sklearn.metrics.pairwise import cosine_similarity

from config import (
    ENTITY_HIGH_THRESHOLD,
    ENTITY_MEDIUM_THRESHOLD,
    SIMILARITY_HIGH_THRESHOLD,
    SIMILARITY_MEDIUM_THRESHOLD,
    TOKEN_HIGH_THRESHOLD,
    TOKEN_MEDIUM_THRESHOLD,
)
from services.embedding import generate_embedding
from services.schemas import DistortionReport


TOKEN_PATTERN = re.compile(r"\b[a-zA-Z']+\b")
ENTITY_PATTERN = re.compile(r"\b[A-Z][a-zA-Z]+\b")


def _normalize_tokens(text: str) -> Set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def _extract_entities(text: str) -> Set[str]:
    return {token.lower() for token in ENTITY_PATTERN.findall(text)}


def semantic_similarity_score(original_text: str, rewritten_text: str) -> float:
    original_embedding = generate_embedding(original_text)
    rewritten_embedding = generate_embedding(rewritten_text)
    return float(cosine_similarity([original_embedding], [rewritten_embedding])[0][0])


def token_overlap_score(original_text: str, rewritten_text: str) -> float:
    original_tokens = _normalize_tokens(original_text)
    rewritten_tokens = _normalize_tokens(rewritten_text)
    if not original_tokens and not rewritten_tokens:
        return 1.0
    if not original_tokens or not rewritten_tokens:
        return 0.0
    intersection = len(original_tokens & rewritten_tokens)
    union = len(original_tokens | rewritten_tokens)
    return intersection / union


def entity_preservation_score(original_text: str, rewritten_text: str) -> float:
    original_entities = _extract_entities(original_text)
    if not original_entities:
        return 1.0
    rewritten_entities = _extract_entities(rewritten_text)
    preserved = len(original_entities & rewritten_entities)
    return preserved / len(original_entities)


def length_ratio_score(original_text: str, rewritten_text: str) -> float:
    original_length = max(len(original_text.split()), 1)
    rewritten_length = len(rewritten_text.split())
    return rewritten_length / original_length


def build_report(original_text: str, rewritten_text: str) -> DistortionReport:
    semantic_similarity = semantic_similarity_score(original_text, rewritten_text)
    token_overlap = token_overlap_score(original_text, rewritten_text)
    entity_preservation = entity_preservation_score(original_text, rewritten_text)
    length_ratio = length_ratio_score(original_text, rewritten_text)

    overall_score = (
        semantic_similarity * 0.5
        + token_overlap * 0.2
        + entity_preservation * 0.2
        + min(length_ratio, 1.0) * 0.1
    )

    if (
        semantic_similarity >= SIMILARITY_HIGH_THRESHOLD
        and entity_preservation >= ENTITY_HIGH_THRESHOLD
        and token_overlap >= TOKEN_HIGH_THRESHOLD
    ):
        distortion_level = "Low"
        summary = "Meaning is well preserved with minimal distortion."
    elif (
        semantic_similarity >= SIMILARITY_MEDIUM_THRESHOLD
        and entity_preservation >= ENTITY_MEDIUM_THRESHOLD
        and token_overlap >= TOKEN_MEDIUM_THRESHOLD
    ):
        distortion_level = "Moderate"
        summary = "Core meaning is mostly preserved, but some nuance may have shifted."
    else:
        distortion_level = "High"
        summary = "The rewrite appears to alter meaning, omit detail, or lose important nuance."

    return DistortionReport(
        semantic_similarity=semantic_similarity,
        token_overlap=token_overlap,
        entity_preservation=entity_preservation,
        length_ratio=length_ratio,
        overall_score=overall_score,
        distortion_level=distortion_level,
        summary=summary,
    )
