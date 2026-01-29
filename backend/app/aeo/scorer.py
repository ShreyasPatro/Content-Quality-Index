"""
AEO Scoring Engine.

This module implements the deterministic scoring logic for the AEO Rubric V1.0.0.
It takes raw signals from `app.aeo.signals` and produces a scored result.
Pure python, no side effects.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from app.aeo.constants import AEO_RUBRIC_VERSION

@dataclass
class PillarScore:
    score: float
    max_score: float
    reason: List[str]

@dataclass
class AEOScoreResult:
    total_score: float
    rubric_version: str
    pillars: Dict[str, PillarScore]
    details: Dict[str, Any]

def score_aeo(signals: Dict[str, Any]) -> AEOScoreResult:
    """
    Calculate AEO score based on extracted signals.
    
    Rubric: AEO V1.0.0 (7 Pillars)
    Total Max: 100
    """
    rubric_version = AEO_RUBRIC_VERSION
    
    # -------------------------------------------------------------------------
    # PILLAR 1: Answerability & Intent Match (Max 25)
    # -------------------------------------------------------------------------
    p1_score = 0.0
    p1_reasons = []
    
    # P1.1 Answer First (15 pts) - Check first 120 words
    first_120 = signals.get("answer_first", {}).get("first_120_words", "")
    if len(first_120.split()) > 20: 
        # Heuristic: If we extracted > 20 words, we assume content exists.
        # Ideally we'd match query intent here, but this is signal-based.
        # We give partial credit just for having a substantive lead.
        p1_score += 15.0
        p1_reasons.append("Content present in 'Answer First' window (First 120 words).")
    else:
        p1_reasons.append("Introductory content is too sparse (< 20 words).")

    # P1.2 Intent/Lead Quality (10 pts) -> Proxy via fluff check in intro
    # If intro has no fluff, full points.
    intro_fluff = 0
    # (Simplified check: re-scan intro for fluff? Or just assume good faith for now)
    # We'll award full points for now as the "Intent Match" requires query context 
    # which we might not fully possess in this signal implementation. 
    # Conservatively award 10 if structure is sound.
    if signals.get("structure", {}).get("h1_count", 0) > 0:
        p1_score += 10.0
        p1_reasons.append("H1 detected, signaling clear topic intent.")
    else:
        p1_reasons.append("No H1 detected; topic intent unclear.")

    pillar_1 = PillarScore(score=min(25.0, p1_score), max_score=25.0, reason=p1_reasons)

    # -------------------------------------------------------------------------
    # PILLAR 2: Structural Extractability (Max 20)
    # -------------------------------------------------------------------------
    p2_score = 0.0
    p2_reasons = []
    
    struct = signals.get("structure", {})
    
    # Hierarchy (10 pts)
    if struct.get("has_proper_hierarchy"):
        p2_score += 10.0
        p2_reasons.append("Proper header hierarchy detected (H1 -> H2/H3).")
    else:
        p2_reasons.append("Weak header hierarchy.")

    # List/Table Density (10 pts)
    list_count = struct.get("list_item_count", 0)
    if list_count > 5:
        p2_score += 10.0
        p2_reasons.append(f"Strong use of lists ({list_count} items).")
    elif list_count > 0:
        p2_score += 5.0
        p2_reasons.append(f"Moderate use of lists ({list_count} items).")
    else:
        p2_reasons.append("No lists detected.")

    pillar_2 = PillarScore(score=min(20.0, p2_score), max_score=20.0, reason=p2_reasons)

    # -------------------------------------------------------------------------
    # PILLAR 3: Specificity & Factual Density (Max 20)
    # -------------------------------------------------------------------------
    p3_score = 0.0
    p3_reasons = []
    
    auth = signals.get("authority", {})
    
    # Numeric Facts (10 pts)
    num_facts = auth.get("numeric_data_points", 0)
    if num_facts >= 3:
        p3_score += 10.0
        p3_reasons.append(f"High density of numeric facts ({num_facts}).")
    elif num_facts > 0:
        p3_score += 5.0
        p3_reasons.append(f"Some numeric facts detected ({num_facts}).")
    else:
        p3_reasons.append("No numeric data points found.")

    # Entity Density (10 pts) - approximated by years or just granted for now
    # We utilize specific years or other data.
    if len(auth.get("years_cited", [])) > 0:
        p3_score += 10.0
        p3_reasons.append("Specific temporal entities (years) detected.")
    else:
        # Check numeric facts again as proxy? Or H3s?
        # Let's be strict: if no years, check for high word count > 500?
        meta = signals.get("meta", {})
        if meta.get("word_count", 0) > 600:
             p3_score += 5.0
             p3_reasons.append("Content length suggests detail, though specific entities low.")
        else:
             p3_reasons.append("Low specificity/entity density.")

    pillar_3 = PillarScore(score=min(20.0, p3_score), max_score=20.0, reason=p3_reasons)

    # -------------------------------------------------------------------------
    # PILLAR 4: Trust & Authority Signals (Max 15)
    # -------------------------------------------------------------------------
    p4_score = 0.0
    p4_reasons = []
    
    # Citations (10 pts)
    links = auth.get("link_count", 0)
    if links >= 2:
        p4_score += 10.0
        p4_reasons.append(f"Strong citation profile ({links} external links).")
    elif links == 1:
        p4_score += 5.0
        p4_reasons.append("Single citation detected.")
    else:
        p4_reasons.append("No external citations.")

    # Fluff Penalty (5 pts)
    qual = signals.get("quality", {})
    fluff_hits = qual.get("fluff_phrase_hits", 0)
    if fluff_hits == 0:
        p4_score += 5.0
        p4_reasons.append("Clean, concise language (0 fluff phrases).")
    else:
        p4_reasons.append(f"Fluff detected ({fluff_hits} instances). Penalty applied.")

    pillar_4 = PillarScore(score=min(15.0, p4_score), max_score=15.0, reason=p4_reasons)

    # -------------------------------------------------------------------------
    # PILLAR 5: Query Coverage Breadth (Max 10)
    # -------------------------------------------------------------------------
    p5_score = 0.0
    p5_reasons = []
    
    wc = signals.get("meta", {}).get("word_count", 0)
    if wc > 800:
        p5_score += 10.0
        p5_reasons.append("Comprehensive depth (>800 words).")
    elif wc > 400:
        p5_score += 6.0
        p5_reasons.append("Moderate depth (>400 words).")
    else:
        p5_score += 2.0
        p5_reasons.append(f"Shallow coverage ({wc} words).")

    pillar_5 = PillarScore(score=min(10.0, p5_score), max_score=10.0, reason=p5_reasons)

    # -------------------------------------------------------------------------
    # PILLAR 6: Freshness & Temporal Clarity (Max 5)
    # -------------------------------------------------------------------------
    p6_score = 0.0
    p6_reasons = []
    
    years = auth.get("years_cited", [])
    if len(years) > 0:
        p6_score += 5.0
        p6_reasons.append(f"Explicit temporal anchoring ({len(years)} years detected).")
    else:
        p6_reasons.append("No specific years mentioned.")

    pillar_6 = PillarScore(score=min(5.0, p6_score), max_score=5.0, reason=p6_reasons)

    # -------------------------------------------------------------------------
    # PILLAR 7: Machine Readability (Max 5)
    # -------------------------------------------------------------------------
    p7_score = 0.0
    p7_reasons = []
    
    avg_sl = signals.get("meta", {}).get("avg_sentence_length", 0)
    if 10 <= avg_sl <= 20:
        p7_score += 5.0
        p7_reasons.append(f"Optimal sentence length ({avg_sl} words).")
    elif 5 < avg_sl < 30:
        p7_score += 3.0
        p7_reasons.append(f"Acceptable sentence length ({avg_sl} words).")
    else:
        p7_score += 1.0
        p7_reasons.append(f"Sentence length suboptimal ({avg_sl} words).")

    pillar_7 = PillarScore(score=min(5.0, p7_score), max_score=5.0, reason=p7_reasons)

    # -------------------------------------------------------------------------
    # TOTAL & VALIDATION
    # -------------------------------------------------------------------------
    
    total = (
        pillar_1.score + 
        pillar_2.score + 
        pillar_3.score + 
        pillar_4.score + 
        pillar_5.score + 
        pillar_6.score + 
        pillar_7.score
    )
    
    total = round(total, 2)
    
    if total > 100.0:
        raise ValueError(f"Calculated AEO score {total} exceeds 100.0")

    return AEOScoreResult(
        total_score=total,
        rubric_version=rubric_version,
        pillars={
            "aeo_answerability": pillar_1,
            "aeo_structure": pillar_2,
            "aeo_specificity": pillar_3,
            "aeo_trust": pillar_4,
            "aeo_coverage": pillar_5,
            "aeo_freshness": pillar_6,
            "aeo_readability": pillar_7,
        },
        details={
            "signals": signals,
            "pillar_breakdown": {
                "p1": asdict(pillar_1),
                "p2": asdict(pillar_2),
                "p3": asdict(pillar_3),
                "p4": asdict(pillar_4),
                "p5": asdict(pillar_5),
                "p6": asdict(pillar_6),
                "p7": asdict(pillar_7),
            }
        }
    )
