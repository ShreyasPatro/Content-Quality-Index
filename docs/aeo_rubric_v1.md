# AEO Rubric Lock: Version 1.0.0

**Status:** FROZEN
**Version:** 1.0.0
**Date:** 2026-01-29

## 1. Executive Freeze Statement
This document defines the **Answer Engine Optimization (AEO)** scoring rubric Version 1.0.0.
All scoring logic implemented in Stage 6 MUST adhere strictly to this definition.
**Any deviation (changing weights, adding signals, modifying scoring ranges) requires a new version number (e.g., 1.1.0) and a full re-audit.**

---

## 2. Core Constraints
- **Total Possible Score:** 100
- **Scoring Output:** Float (0.00 - 100.00)
- **Primary Scorer:** Deterministic Rule-Based Engine (Stage 6)

---

## 3. Pillar Definitions & Weights

The total score is the weighted sum of the following fixed pillars:

| Pillar ID | Name | Weight | Max Points | Description |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **Answerability & Intent Match** | **25%** | 25 | Does the content provide an immediate, extraction-ready answer? |
| **P2** | **Structural Extractability** | **20%** | 20 | Use of H2/H3/Lists/Tables for machine parsing. |
| **P3** | **Specificity & Factual Density** | **20%** | 20 | Presence of entities, numbers, and concrete data points. |
| **P4** | **Trust & Authority Signals** | **15%** | 15 | Citations, outbound links, and absence of fluff. |
| **P5** | **Query Coverage Breadth** | **10%** | 10 | Comprehensive coverage of the topic. |
| **P6** | **Freshness & Temporal Clarity** | **5%** | 5 | Clear dates (Years) and timelines. |
| **P7** | **Machine Readability** | **5%** | 5 | Sentence length and paragraph structure efficiency. |

**Verification Rule:** Sum of Weights must equal 100%.

---

## 4. Detailed Signal Definitions (Fixed)

### P1: Answerability & Intent Match (25 pts)
- **Answer First (15 pts):** Core answer detected in first 120 words.
- **Intent Clarity (10 pts):** Clear subject detection.

### P2: Structural Extractability (20 pts)
- **Hierarchy (10 pts):** Proper H1 -> H2 -> H3 nesting.
- **List/Table Density (10 pts):** Presence of structured data formats.

### P3: Specificity & Factual Density (20 pts)
- **Numeric Facts (10 pts):** Usage of specific numbers/percentages.
- **Entity Density (10 pts):** Capitalized entity clusters.

### P4: Trust & Authority Signals (15 pts)
- **Citations (10 pts):** Outbound links to external domains.
- **Fluff Penalty (5 pts):** Deduction for generic filler phrases.

### P5: Query Coverage (10 pts)
- **Word Count/Depth (10 pts):** Sufficient length for depth (proxy).

### P6: Freshness (5 pts)
- **Dates (5 pts):** Explicit year mentions (1900-2099).

### P7: Machine Readability (5 pts)
- **Sentence Length (5 pts):** Average sentence length optimal for NLP (10-20 words).

---

## 5. Scoring Rules
- **Total Score** = Sum(P1...P7).
- **Max Score** = 100.00.
- **Min Score** = 0.00.
- **Rounding:** 2 decimal places.

---

## 6. Implementation Mandates
1.  **Input:** Extracted Signals (`app/aeo/signals.py`).
2.  **Output:** JSON object containing `total_score` and pillar breakdowns.
3.  **Determinism:** The same input set MUST yield the same score.
