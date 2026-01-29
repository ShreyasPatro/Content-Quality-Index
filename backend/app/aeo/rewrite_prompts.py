"""
AEO Rewrite Prompt Generator.

This module purely generates deterministic rewrite instructions based on AEO score deficits.
It maps low pillar scores to specific, actionable editing directives.
No AI execution here; just prompt construction.
"""

from typing import List, Dict, Any
from app.aeo.scorer import AEOScoreResult

# -------------------------------------------------------------------------
# PROMPT TEMPLATES (1:1 with Rubric Pillars)
# -------------------------------------------------------------------------

PILLAR_PROMPTS = {
    "aeo_answerability": [
        "**Action:** Move the direct answer to the very first paragraph.",
        "**Why:** The core answer was not found in the first 120 words (Pillar 1).",
        "**Fix:** Start immediately with 'The answer is X' or 'X is Y'. Remove introductory fluff."
    ],
    "aeo_structure": [
        "**Action:** Restructure content using H2/H3 headers and lists.",
        "**Why:** Structural extractability score is low (Pillar 2).",
        "**Fix:** Break long text into bullet points. Ensure a clear hierarchy of headers."
    ],
    "aeo_specificity": [
        "**Action:** Add specific data points, numbers, and entities.",
        "**Why:** Specificity and factual density is insufficient (Pillar 3).",
        "**Fix:** Replace generic terms ("many", "some") with exact numbers, percentages, or proper nouns."
    ],
    "aeo_trust": [
        "**Action:** Add citations and remove filler content.",
        "**Why:** Trust signals are weak or fluff is high (Pillar 4).",
        "**Fix:** Cite reputable external sources. Delete phrases like 'In today's world' or 'It is important to note'."
    ],
    "aeo_coverage": [
        "**Action:** Expand depth of coverage.",
        "**Why:** Content length suggests shallow coverage (Pillar 5).",
        "**Fix:** Expand on key subtopics. Target a higher word count with substantive analysis."
    ],
    "aeo_freshness": [
        "**Action:** Add explicit temporal anchoring.",
        "**Why:** No specific years or timelines detected (Pillar 6).",
        "**Fix:** Mention relevant years (e.g., 2024, 2025) to signal currency."
    ],
    "aeo_readability": [
        "**Action:** Simplify sentence structure.",
        "**Why:** Machine readability score is low (Pillar 7).",
        "**Fix:** Shorten sentences to 10-20 words. Split complex compound sentences."
    ]
}

def generate_rewrite_instructions(score_result: AEOScoreResult) -> List[str]:
    """
    Generate a list of rewrite prompts based on weak pillars.
    
    Args:
        score_result: The calculated AEO score and pillar breakdown.
        
    Returns:
        List of strings, each being a rewrite instruction block.
    """
    instructions = []
    
    # Iterate through pillars in importance order
    priority_order = [
         ("aeo_answerability", score_result.pillars["aeo_answerability"]),
         ("aeo_structure", score_result.pillars["aeo_structure"]),
         ("aeo_specificity", score_result.pillars["aeo_specificity"]),
         ("aeo_trust", score_result.pillars["aeo_trust"]),
         ("aeo_coverage", score_result.pillars["aeo_coverage"]),
         ("aeo_freshness", score_result.pillars["aeo_freshness"]),
         ("aeo_readability", score_result.pillars["aeo_readability"]),
    ]

    for pillar_key, pillar_data in priority_order:
        # Threshold: If score is less than max, generate prompt.
        # We can be stricter: e.g. score < 80% of max?
        # For now, any deduction triggers advice, filtered by severity in the UI if needed.
        if pillar_data.score < pillar_data.max_score:
            prompts = PILLAR_PROMPTS.get(pillar_key)
            if prompts:
                # Format the block
                instruction_block = "\n".join(prompts)
                # Append score context
                instruction_block += f"\n(Score: {pillar_data.score}/{pillar_data.max_score})"
                instructions.append(instruction_block)

    if not instructions:
        return ["**Status:** Content meets all AEO requirements. No rewriting necessary."]

    return instructions
