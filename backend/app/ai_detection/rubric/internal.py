"""Internal AI-likeness rubric scoring engine.

This module contains all scoring logic and heuristics.
DO NOT import this module directly - use scorer.py public API.

Rubric Categories:
1. Predictability & Entropy (0-25): Measures text diversity and randomness
2. Sentence & Paragraph Uniformity (0-20): Detects mechanical consistency
3. Generic Language & Clichés (0-20): Identifies overused AI phrases
4. Structural Template Signals (0-15): Detects formulaic patterns
5. Lack of Human Friction (0-10): Measures absence of natural errors
6. Over-Polish & Safety Tone (0-10): Detects excessive formality

Total Score: 0-100 (higher = more AI-like)
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import List, TypedDict


# Rubric version for auditability and drift tracking
RUBRIC_VERSION = "1.0.0"


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class CategoryScore(TypedDict):
    """Score for a single rubric category."""

    score: float  # 0-max_score for this category
    max_score: float  # Maximum possible score for this category
    percentage: float  # score / max_score * 100
    explanation: str  # Human-readable explanation with evidence
    evidence: List[str]  # Actual text snippets that triggered this score


@dataclass
class InternalRubricResult:
    """Internal rubric scoring result (not exposed in public API)."""

    rubric_version: str
    total_score: float
    predictability_entropy: CategoryScore
    sentence_uniformity: CategoryScore
    generic_language: CategoryScore
    structural_templates: CategoryScore
    lack_of_friction: CategoryScore
    over_polish: CategoryScore
    text_length: int
    word_count: int


# ============================================================================
# AI-LIKE PHRASES AND PATTERNS
# ============================================================================

# Common AI-generated phrases (case-insensitive)
AI_PHRASES = [
    "it's important to note",
    "it's worth noting",
    "it's crucial to",
    "it's essential to",
    "in today's world",
    "in today's digital age",
    "in conclusion",
    "to summarize",
    "in summary",
    "as an AI",
    "I don't have personal",
    "I cannot provide",
    "delve into",
    "dive into",
    "navigate the",
    "landscape of",
    "realm of",
    "tapestry of",
    "myriad of",
    "plethora of",
    "it's no secret that",
    "the fact of the matter",
    "at the end of the day",
    "game changer",
    "paradigm shift",
    "cutting edge",
    "state of the art",
    "leverage",
    "utilize",
    "facilitate",
    "optimize",
    "streamline",
    "robust",
    "comprehensive",
    "holistic",
    "synergy",
    "ecosystem",
]

# Formulaic opening patterns
TEMPLATE_OPENINGS = [
    r"^In this (article|post|guide|blog)",
    r"^(Welcome to|Introduction to)",
    r"^(Have you ever|Are you|Do you)",
    r"^(Imagine|Picture this|Consider)",
    r"^(Let's|Let us) (explore|discuss|examine|dive into)",
]

# Safety/hedging phrases
SAFETY_PHRASES = [
    "generally speaking",
    "in most cases",
    "typically",
    "usually",
    "often",
    "may be",
    "might be",
    "could be",
    "it depends",
    "varies depending",
    "consult a professional",
    "seek expert advice",
]


# ============================================================================
# CATEGORY 1: PREDICTABILITY & ENTROPY (0-25)
# ============================================================================


def score_predictability_entropy(text: str, words: List[str]) -> CategoryScore:
    """Score text predictability and entropy.

    Measures:
    - Lexical diversity (unique words / total words)
    - Word length variance
    - Repetition patterns

    Args:
        text: Input text
        words: List of words

    Returns:
        Category score with explanation and evidence
    """
    if len(words) < 10:
        return CategoryScore(
            score=0.0,
            max_score=25.0,
            percentage=0.0,
            explanation="Text too short to analyze entropy (< 10 words)",
            evidence=[],
        )

    signals = []
    evidence = []
    score = 0.0

    # 1. Lexical diversity (10 points)
    unique_words = len(set(w.lower() for w in words))
    lexical_diversity = unique_words / len(words)

    if lexical_diversity < 0.4:
        diversity_score = 10.0
        signals.append(f"Very low lexical diversity ({lexical_diversity:.2f})")
    elif lexical_diversity < 0.5:
        diversity_score = 7.0
        signals.append(f"Low lexical diversity ({lexical_diversity:.2f})")
    elif lexical_diversity < 0.6:
        diversity_score = 4.0
        signals.append(f"Moderate lexical diversity ({lexical_diversity:.2f})")
    else:
        diversity_score = 0.0
        signals.append(f"High lexical diversity ({lexical_diversity:.2f})")

    score += diversity_score

    # 2. Word length variance (8 points)
    word_lengths = [len(w) for w in words]
    avg_length = sum(word_lengths) / len(word_lengths)
    variance = sum((l - avg_length) ** 2 for l in word_lengths) / len(word_lengths)
    std_dev = math.sqrt(variance)

    if std_dev < 2.0:
        variance_score = 8.0
        signals.append(f"Very uniform word lengths (σ={std_dev:.2f})")
    elif std_dev < 2.5:
        variance_score = 5.0
        signals.append(f"Low word length variance (σ={std_dev:.2f})")
    else:
        variance_score = 0.0
        signals.append(f"Natural word length variance (σ={std_dev:.2f})")

    score += variance_score

    # 3. Repetition patterns (7 points)
    word_freq = Counter(w.lower() for w in words)
    most_common = word_freq.most_common(5)
    max_freq = most_common[0][1] if most_common else 0
    repetition_ratio = max_freq / len(words)

    if repetition_ratio > 0.05:
        repetition_score = 7.0
        most_common_word = most_common[0][0] if most_common else ""
        signals.append(
            f"High word repetition: '{most_common_word}' ({repetition_ratio:.2%})"
        )
        evidence.append(f"Most repeated: '{most_common_word}' ({most_common[0][1]}x)")
    elif repetition_ratio > 0.03:
        repetition_score = 4.0
        most_common_word = most_common[0][0] if most_common else ""
        signals.append(
            f"Moderate word repetition: '{most_common_word}' ({repetition_ratio:.2%})"
        )
        evidence.append(f"Most repeated: '{most_common_word}' ({most_common[0][1]}x)")
    else:
        repetition_score = 0.0
        signals.append(f"Low word repetition ({repetition_ratio:.2%})")

    score += repetition_score

    explanation = " | ".join(signals)

    return CategoryScore(
        score=score,
        max_score=25.0,
        percentage=(score / 25.0) * 100,
        explanation=explanation,
        evidence=evidence,
    )


# ============================================================================
# CATEGORY 2: SENTENCE & PARAGRAPH UNIFORMITY (0-20)
# ============================================================================


def score_sentence_uniformity(text: str) -> CategoryScore:
    """Score sentence and paragraph uniformity.

    Measures:
    - Sentence length consistency
    - Paragraph length consistency

    Args:
        text: Input text

    Returns:
        Category score with explanation and evidence
    """
    # Split into sentences (simple heuristic)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 3:
        return CategoryScore(
            score=0.0,
            max_score=20.0,
            percentage=0.0,
            explanation="Text too short to analyze uniformity (< 3 sentences)",
            evidence=[],
        )

    signals = []
    evidence = []
    score = 0.0

    # 1. Sentence length uniformity (12 points)
    sentence_lengths = [len(s.split()) for s in sentences]
    avg_sent_length = sum(sentence_lengths) / len(sentence_lengths)
    sent_variance = sum((l - avg_sent_length) ** 2 for l in sentence_lengths) / len(
        sentence_lengths
    )
    sent_std_dev = math.sqrt(sent_variance)
    coefficient_of_variation = (
        sent_std_dev / avg_sent_length if avg_sent_length > 0 else 0
    )

    if coefficient_of_variation < 0.3:
        uniformity_score = 12.0
        signals.append(
            f"Very uniform sentence lengths (CV={coefficient_of_variation:.2f})"
        )
        evidence.append(
            f"Sentence lengths: {sentence_lengths[:5]} (avg={avg_sent_length:.1f})"
        )
    elif coefficient_of_variation < 0.5:
        uniformity_score = 7.0
        signals.append(
            f"Moderately uniform sentences (CV={coefficient_of_variation:.2f})"
        )
    else:
        uniformity_score = 0.0
        signals.append(
            f"Natural sentence length variance (CV={coefficient_of_variation:.2f})"
        )

    score += uniformity_score

    # 2. Paragraph uniformity (8 points)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if len(paragraphs) >= 3:
        para_lengths = [len(p.split()) for p in paragraphs]
        avg_para_length = sum(para_lengths) / len(para_lengths)
        para_variance = sum((l - avg_para_length) ** 2 for l in para_lengths) / len(
            para_lengths
        )
        para_std_dev = math.sqrt(para_variance)
        para_cv = para_std_dev / avg_para_length if avg_para_length > 0 else 0

        if para_cv < 0.3:
            para_score = 8.0
            signals.append(f"Very uniform paragraph lengths (CV={para_cv:.2f})")
            evidence.append(
                f"Paragraph lengths: {para_lengths[:3]} (avg={avg_para_length:.1f})"
            )
        elif para_cv < 0.5:
            para_score = 4.0
            signals.append(f"Moderately uniform paragraphs (CV={para_cv:.2f})")
        else:
            para_score = 0.0
            signals.append(f"Natural paragraph variance (CV={para_cv:.2f})")

        score += para_score
    else:
        signals.append("Too few paragraphs to analyze uniformity")

    explanation = " | ".join(signals)

    return CategoryScore(
        score=score,
        max_score=20.0,
        percentage=(score / 20.0) * 100,
        explanation=explanation,
        evidence=evidence,
    )


# ============================================================================
# CATEGORY 3: GENERIC LANGUAGE & CLICHÉS (0-20)
# ============================================================================

# NOTE: Transition adverbs (firstly, secondly, etc.) are counted in both
# Category 3 (adverb overuse) and Category 4 (transitions). This is intentional
# as they signal both generic language AND structural templates.


def score_generic_language(text: str) -> CategoryScore:
    """Score generic language and AI clichés.

    Measures:
    - Presence of common AI phrases
    - Buzzword density
    - Adverb overuse

    Args:
        text: Input text

    Returns:
        Category score with explanation and evidence
    """
    text_lower = text.lower()
    signals = []
    evidence = []
    score = 0.0

    # 1. AI phrase detection (15 points)
    found_phrases = [phrase for phrase in AI_PHRASES if phrase in text_lower]
    phrase_count = len(found_phrases)

    if phrase_count >= 5:
        phrase_score = 15.0
        evidence_sample = ", ".join(f"'{p}'" for p in found_phrases[:3])
        signals.append(f"Found {phrase_count} AI-like phrases: {evidence_sample}...")
        evidence.extend(found_phrases[:5])
    elif phrase_count >= 3:
        phrase_score = 10.0
        evidence_sample = ", ".join(f"'{p}'" for p in found_phrases)
        signals.append(f"Found {phrase_count} AI-like phrases: {evidence_sample}")
        evidence.extend(found_phrases)
    elif phrase_count >= 1:
        phrase_score = 5.0
        evidence_sample = ", ".join(f"'{p}'" for p in found_phrases)
        signals.append(f"Found {phrase_count} AI-like phrase(s): {evidence_sample}")
        evidence.extend(found_phrases)
    else:
        phrase_score = 0.0
        signals.append("No common AI phrases detected")

    score += phrase_score

    # 2. Adverb overuse (5 points)
    # AI tends to use more adverbs for hedging
    adverbs = re.findall(r"\b\w+ly\b", text_lower)
    words = text_lower.split()
    adverb_ratio = len(adverbs) / len(words) if words else 0

    if adverb_ratio > 0.05:
        adverb_score = 5.0
        adverb_sample = ", ".join(adverbs[:5])
        signals.append(
            f"High adverb usage ({adverb_ratio:.2%}): {adverb_sample}..."
        )
        evidence.append(f"Adverbs: {adverb_sample}")
    elif adverb_ratio > 0.03:
        adverb_score = 2.0
        signals.append(f"Moderate adverb usage ({adverb_ratio:.2%})")
    else:
        adverb_score = 0.0
        signals.append(f"Normal adverb usage ({adverb_ratio:.2%})")

    score += adverb_score

    explanation = " | ".join(signals)

    return CategoryScore(
        score=score,
        max_score=20.0,
        percentage=(score / 20.0) * 100,
        explanation=explanation,
        evidence=evidence,
    )


# ============================================================================
# CATEGORY 4: STRUCTURAL TEMPLATE SIGNALS (0-15)
# ============================================================================


def score_structural_templates(text: str) -> CategoryScore:
    """Score structural template signals.

    Measures:
    - Formulaic openings
    - List/enumeration patterns
    - Transition phrases

    Args:
        text: Input text

    Returns:
        Category score with explanation and evidence
    """
    signals = []
    evidence = []
    score = 0.0

    # 1. Formulaic openings (8 points)
    first_sentence = text.split(".")[0] if "." in text else text[:200]
    template_matches = [
        pattern
        for pattern in TEMPLATE_OPENINGS
        if re.search(pattern, first_sentence, re.IGNORECASE)
    ]

    if template_matches:
        opening_score = 8.0
        opening_snippet = first_sentence[:60] + "..." if len(first_sentence) > 60 else first_sentence
        signals.append(f"Formulaic opening: '{opening_snippet}'")
        evidence.append(f"Opening: '{opening_snippet}'")
    else:
        opening_score = 0.0
        signals.append("Natural opening")

    score += opening_score

    # 2. Numbered lists (4 points)
    numbered_items = re.findall(r"^\s*\d+[\.)]\s+", text, re.MULTILINE)

    if len(numbered_items) >= 5:
        list_score = 4.0
        signals.append(f"Heavy list structure ({len(numbered_items)} items)")
        evidence.append(f"Numbered list items: {len(numbered_items)}")
    elif len(numbered_items) >= 3:
        list_score = 2.0
        signals.append(f"Moderate list structure ({len(numbered_items)} items)")
        evidence.append(f"Numbered list items: {len(numbered_items)}")
    else:
        list_score = 0.0
        signals.append("Minimal list structure")

    score += list_score

    # 3. Transition phrases (3 points)
    transitions = [
        "firstly",
        "secondly",
        "thirdly",
        "finally",
        "moreover",
        "furthermore",
        "additionally",
        "in addition",
        "however",
        "nevertheless",
    ]
    text_lower = text.lower()
    found_transitions = [t for t in transitions if t in text_lower]
    transition_count = len(found_transitions)

    if transition_count >= 4:
        transition_score = 3.0
        transition_sample = ", ".join(f"'{t}'" for t in found_transitions[:4])
        signals.append(f"Heavy transition usage: {transition_sample}")
        evidence.extend(found_transitions[:4])
    elif transition_count >= 2:
        transition_score = 1.5
        transition_sample = ", ".join(f"'{t}'" for t in found_transitions)
        signals.append(f"Moderate transition usage: {transition_sample}")
        evidence.extend(found_transitions)
    else:
        transition_score = 0.0
        signals.append("Minimal transition usage")

    score += transition_score

    explanation = " | ".join(signals)

    return CategoryScore(
        score=score,
        max_score=15.0,
        percentage=(score / 15.0) * 100,
        explanation=explanation,
        evidence=evidence,
    )


# ============================================================================
# CATEGORY 5: LACK OF HUMAN FRICTION (0-10)
# ============================================================================


def score_lack_of_friction(text: str, words: List[str]) -> CategoryScore:
    """Score lack of human friction.

    Measures:
    - Absence of typos/errors
    - Perfect punctuation
    - Lack of informal markers

    Args:
        text: Input text
        words: List of words

    Returns:
        Category score with explanation and evidence
    """
    signals = []
    evidence = []
    score = 0.0

    # 1. Perfect capitalization (4 points)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if sentences:
        capitalized = sum(1 for s in sentences if s and s[0].isupper())
        cap_ratio = capitalized / len(sentences)

        if cap_ratio == 1.0 and len(sentences) >= 3:
            cap_score = 4.0
            signals.append("Perfect sentence capitalization")
            evidence.append(f"All {len(sentences)} sentences capitalized")
        else:
            cap_score = 0.0
            signals.append(f"Natural capitalization ({cap_ratio:.0%})")

        score += cap_score
    else:
        signals.append("No sentences to analyze")

    # 2. Lack of contractions (3 points)
    contractions = re.findall(r"\b\w+'\w+\b", text)
    contraction_ratio = len(contractions) / len(words) if words else 0

    if contraction_ratio < 0.01:
        contraction_score = 3.0
        signals.append("Very few contractions (formal)")
        evidence.append(f"Contractions: {len(contractions)}/{len(words)} words")
    elif contraction_ratio < 0.02:
        contraction_score = 1.5
        signals.append("Few contractions")
    else:
        contraction_score = 0.0
        signals.append(f"Natural contraction usage ({contraction_ratio:.2%})")

    score += contraction_score

    # 3. Lack of informal markers (3 points)
    informal_markers = ["lol", "haha", "omg", "btw", "tbh", "...", "!!", "??"]
    text_lower = text.lower()
    found_informal = [m for m in informal_markers if m in text_lower]
    informal_count = len(found_informal)

    if informal_count == 0 and len(words) > 50:
        informal_score = 3.0
        signals.append("No informal markers (very formal)")
        evidence.append("No informal markers found")
    else:
        informal_score = 0.0
        if found_informal:
            informal_sample = ", ".join(f"'{m}'" for m in found_informal[:3])
            signals.append(f"Natural informality: {informal_sample}")

    score += informal_score

    explanation = " | ".join(signals)

    return CategoryScore(
        score=score,
        max_score=10.0,
        percentage=(score / 10.0) * 100,
        explanation=explanation,
        evidence=evidence,
    )


# ============================================================================
# CATEGORY 6: OVER-POLISH & SAFETY TONE (0-10)
# ============================================================================


def score_over_polish(text: str) -> CategoryScore:
    """Score over-polish and safety tone.

    Measures:
    - Hedging language
    - Disclaimers
    - Excessive politeness

    Args:
        text: Input text

    Returns:
        Category score with explanation and evidence
    """
    text_lower = text.lower()
    signals = []
    evidence = []
    score = 0.0

    # 1. Safety/hedging phrases (7 points)
    found_safety = [phrase for phrase in SAFETY_PHRASES if phrase in text_lower]
    safety_count = len(found_safety)

    if safety_count >= 4:
        safety_score = 7.0
        safety_sample = ", ".join(f"'{p}'" for p in found_safety[:4])
        signals.append(f"Heavy hedging language: {safety_sample}")
        evidence.extend(found_safety[:4])
    elif safety_count >= 2:
        safety_score = 4.0
        safety_sample = ", ".join(f"'{p}'" for p in found_safety)
        signals.append(f"Moderate hedging: {safety_sample}")
        evidence.extend(found_safety)
    elif safety_count >= 1:
        safety_score = 2.0
        safety_sample = ", ".join(f"'{p}'" for p in found_safety)
        signals.append(f"Some hedging: {safety_sample}")
        evidence.extend(found_safety)
    else:
        safety_score = 0.0
        signals.append("No hedging detected")

    score += safety_score

    # 2. Disclaimer patterns (3 points)
    disclaimers = [
        "please note",
        "keep in mind",
        "be aware",
        "remember that",
        "it is important",
        "you should know",
    ]
    found_disclaimers = [d for d in disclaimers if d in text_lower]
    disclaimer_count = len(found_disclaimers)

    if disclaimer_count >= 2:
        disclaimer_score = 3.0
        disclaimer_sample = ", ".join(f"'{d}'" for d in found_disclaimers)
        signals.append(f"Multiple disclaimers: {disclaimer_sample}")
        evidence.extend(found_disclaimers)
    elif disclaimer_count >= 1:
        disclaimer_score = 1.5
        disclaimer_sample = ", ".join(f"'{d}'" for d in found_disclaimers)
        signals.append(f"Some disclaimers: {disclaimer_sample}")
        evidence.extend(found_disclaimers)
    else:
        disclaimer_score = 0.0
        signals.append("No disclaimers")

    score += disclaimer_score

    explanation = " | ".join(signals)

    return CategoryScore(
        score=score,
        max_score=10.0,
        percentage=(score / 10.0) * 100,
        explanation=explanation,
        evidence=evidence,
    )


# ============================================================================
# MAIN INTERNAL SCORING FUNCTION
# ============================================================================


def score_text_internal(text: str) -> InternalRubricResult:
    """Score text using AI-likeness rubric (internal function).

    This is a pure function with deterministic output.
    Same input will always produce the same output.

    Args:
        text: Input text to analyze

    Returns:
        InternalRubricResult with total score and category breakdowns

    Raises:
        ValueError: If text is empty, too short, or total score exceeds 100
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    text = text.strip()

    # Basic tokenization
    words = re.findall(r"\b\w+\b", text)

    if len(words) < 5:
        raise ValueError("Text too short (minimum 5 words required)")

    # Score each category
    predictability = score_predictability_entropy(text, words)
    uniformity = score_sentence_uniformity(text)
    generic = score_generic_language(text)
    templates = score_structural_templates(text)
    friction = score_lack_of_friction(text, words)
    polish = score_over_polish(text)

    # Calculate total score
    total = (
        predictability["score"]
        + uniformity["score"]
        + generic["score"]
        + templates["score"]
        + friction["score"]
        + polish["score"]
    )

    # CRITICAL: Enforce maximum total score
    # Do NOT silently clamp - raise error if scoring logic is broken
    if total > 100.0:
        raise ValueError(
            f"Rubric scoring error: total_score={total:.2f} exceeds maximum of 100.0. "
            f"This indicates a bug in the scoring logic."
        )

    return InternalRubricResult(
        rubric_version=RUBRIC_VERSION,
        total_score=total,
        predictability_entropy=predictability,
        sentence_uniformity=uniformity,
        generic_language=generic,
        structural_templates=templates,
        lack_of_friction=friction,
        over_polish=polish,
        text_length=len(text),
        word_count=len(words),
    )
