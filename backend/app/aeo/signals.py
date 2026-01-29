"""
AEO Signal Extractors.

This module purely extracts structural, statistical, and textual signals from content.
It contains NO scoring logic and makes NO external calls.
It is deterministic and regex-based.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# -------------------------------------------------------------------------
# CONSTANTS & PATTERNS
# -------------------------------------------------------------------------

# Fluff phrases to detect "generic" or "filler" content
FLUFF_PHRASES = [
    r"in today's world",
    r"it is important to note",
    r"needless to say",
    r"at the end of the day",
    r"all things considered",
    r"last but not least",
    r"in conclusion",
    r"without further ado",
    r"let's dive in",
    r"game changer",
]

# Patterns for structure
H1_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
H2_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
H3_PATTERN = re.compile(r"^###\s+(.+)$", re.MULTILINE)
LIST_ITEM_PATTERN = re.compile(r"^(\s*[-*]|\s*\d+\.)\s+(.+)$", re.MULTILINE)

# Patterns for entities / data
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")  # 1900-2099 coverage
URL_PATTERN = re.compile(r"https?://[^\s)]+")
NUMERIC_FACT_PATTERN = re.compile(r"\b\d+(\.\d+)?%?")  # Numbers and Percentages

# -------------------------------------------------------------------------
# EXTRACTOR LOGIC
# -------------------------------------------------------------------------

def extract_aeo_signals(content: str) -> Dict[str, Any]:
    """
    Extract raw deterministic signals from markdown content.
    
    Args:
        content: Raw markdown text string.
        
    Returns:
        Dictionary of raw signal data.
    """
    if not content:
        return _empty_signals()

    # Pre-computation
    lines = content.split('\n')
    words = content.split()
    word_count = len(words)
    
    # 1. Answer First Analysis (First 120 words)
    first_120_words = " ".join(words[:120])
    
    # 2. Structural Analysis
    h1_matches = H1_PATTERN.findall(content)
    h2_matches = H2_PATTERN.findall(content)
    h3_matches = H3_PATTERN.findall(content)
    list_items = LIST_ITEM_PATTERN.findall(content)
    
    # 3. Fluff / Conciseness
    fluff_counts = {}
    total_fluff_hits = 0
    content_lower = content.lower()
    for phrase_regex in FLUFF_PHRASES:
        hits = len(re.findall(phrase_regex, content_lower))
        if hits > 0:
            fluff_counts[phrase_regex] = hits
            total_fluff_hits += hits

    # 4. Authority Signals (Citations / Data)
    outbound_links = URL_PATTERN.findall(content)
    numeric_facts = NUMERIC_FACT_PATTERN.findall(content)
    
    # 5. Entity Signals (Heuristic: Years, Capitalized Sequences)
    # Note: Capitalized sequences is a rough proxy for Proper Nouns in regex-only mode
    years = YEAR_PATTERN.findall(content)
    
    # 6. Readability Stats
    # Rough sentence split by punctuation
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sentence_length = word_count / len(sentences) if sentences else 0
    long_paragraphs = [
        line for line in lines 
        if len(line.split()) > 60  # Arbitrary "long" threshold for scannability
    ]

    return {
        "meta": {
            "word_count": word_count,
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_length, 2),
        },
        "structure": {
            "h1_count": len(h1_matches),
            "h2_count": len(h2_matches),
            "h3_count": len(h3_matches),
            "list_item_count": len(list_items),
            "has_proper_hierarchy": len(h1_matches) > 0 and (len(h2_matches) > 0 or len(h3_matches) > 0),
        },
        "answer_first": {
            "first_120_words": first_120_words,
            # Just returning the raw text for the scorer to evaluate, 
            # or we could compute "keyword density" here if we had the keyword.
            # For now, just the window.
        },
        "authority": {
            "link_count": len(outbound_links),
            "numeric_data_points": len(numeric_facts),
            "years_cited": list(set(years)),  # Unique years
        },
        "quality": {
            "fluff_phrase_hits": total_fluff_hits,
            "fluff_details": fluff_counts,
            "long_paragraph_count": len(long_paragraphs),
        }
    }

def _empty_signals() -> Dict[str, Any]:
    """Return zeroed signal structure for empty content."""
    return {
        "meta": {"word_count": 0, "sentence_count": 0, "avg_sentence_length": 0},
        "structure": {"h1_count": 0, "h2_count": 0, "h3_count": 0, "list_item_count": 0, "has_proper_hierarchy": False},
        "answer_first": {"first_120_words": ""},
        "authority": {"link_count": 0, "numeric_data_points": 0, "years_cited": []},
        "quality": {"fluff_phrase_hits": 0, "fluff_details": {}, "long_paragraph_count": 0},
    }
