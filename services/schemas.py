from dataclasses import dataclass
from typing import List


@dataclass
class CanonicalizationResult:
    mode: str
    canonicalized_text: str
    changed_phrases: List[str]
    preserved_concepts: List[str]
    nuance_risks: List[str]
    explanation: str


@dataclass
class DistortionReport:
    semantic_similarity: float
    token_overlap: float
    entity_preservation: float
    length_ratio: float
    overall_score: float
    distortion_level: str
    summary: str


@dataclass
class ComparisonResult:
    mode: str
    canonicalization: CanonicalizationResult
    report: DistortionReport
