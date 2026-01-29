"""Type definitions for AI rubric scoring."""

from dataclasses import dataclass
from typing import TypedDict


class CategoryScore(TypedDict):
    """Score for a single rubric category."""

    score: float  # 0-max_score for this category
    max_score: float  # Maximum possible score for this category
    percentage: float  # score / max_score * 100
    explanation: str  # Human-readable explanation of the score


@dataclass
class RubricResult:
    """Complete rubric scoring result.

    Attributes:
        total_score: Overall AI-likeness score (0-100)
        predictability_entropy: Category 1 score (0-25)
        sentence_uniformity: Category 2 score (0-20)
        generic_language: Category 3 score (0-20)
        structural_templates: Category 4 score (0-15)
        lack_of_friction: Category 5 score (0-10)
        over_polish: Category 6 score (0-10)
        text_length: Number of characters in analyzed text
        word_count: Number of words in analyzed text
    """

    total_score: float
    predictability_entropy: CategoryScore
    sentence_uniformity: CategoryScore
    generic_language: CategoryScore
    structural_templates: CategoryScore
    lack_of_friction: CategoryScore
    over_polish: CategoryScore
    text_length: int
    word_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_score": round(self.total_score, 2),
            "categories": {
                "predictability_entropy": self.predictability_entropy,
                "sentence_uniformity": self.sentence_uniformity,
                "generic_language": self.generic_language,
                "structural_templates": self.structural_templates,
                "lack_of_friction": self.lack_of_friction,
                "over_polish": self.over_polish,
            },
            "metadata": {
                "text_length": self.text_length,
                "word_count": self.word_count,
            },
        }
