"""Example usage of audit-compliant AI rubric scorer."""

from app.ai_detection.rubric import score_ai_likeness

# Example 1: AI-like text
ai_text = """
In today's digital age, it's important to note that artificial intelligence is revolutionizing 
the landscape of content creation. Let's explore the key benefits of this paradigm shift.

Firstly, AI can streamline the content generation process. Secondly, it can optimize workflows 
and facilitate better outcomes. Moreover, it's worth noting that this technology offers a 
comprehensive solution for businesses.

In conclusion, leveraging AI for content creation is a game changer. However, it's essential 
to consult a professional before implementing these solutions in your ecosystem.
"""

print("=" * 80)
print("EXAMPLE 1: AI-GENERATED TEXT")
print("=" * 80)

result = score_ai_likeness(ai_text)

print(f"\nModel Version: {result['model_version']}")
print(f"Timestamp: {result['timestamp']}")
print(f"Total AI-likeness Score: {result['score']:.2f}/100")

subscores = result["raw_response"]["subscores"]

print(f"\n{'Category':<30} {'Score':<10} {'Evidence'}")
print("-" * 80)

for category_name, category_data in subscores.items():
    score_str = f"{category_data['score']:.1f}/{category_data['max_score']}"
    evidence_count = len(category_data['evidence'])
    evidence_preview = category_data['evidence'][0] if evidence_count > 0 else "None"
    
    print(f"{category_name:<30} {score_str:<10} {evidence_preview}")
    
    if evidence_count > 1:
        for ev in category_data['evidence'][1:3]:  # Show up to 3 evidence items
            print(f"{'':<41} {ev}")

print("\n" + "=" * 80)
print("EXAMPLE 2: HUMAN-WRITTEN TEXT")
print("=" * 80)

# Example 2: Human-like text
human_text = """
I've been thinking about this for a while now, and honestly? The whole AI content thing is 
kinda weird. Like, you can usually tell when something's been written by a bot - it just 
feels... off.

There's this uncanny valley thing happening. The sentences are too perfect, you know? Real 
people make mistakes, use contractions, throw in random thoughts. We're messy. That's what 
makes us human.

Anyway, just my two cents. What do you think?
"""

result2 = score_ai_likeness(human_text)

print(f"\nTotal AI-likeness Score: {result2['score']:.2f}/100")
print("(Lower score = more human-like)")

subscores2 = result2["raw_response"]["subscores"]

print(f"\n{'Category':<30} {'Score':<10} {'Explanation'}")
print("-" * 80)

for category_name, category_data in subscores2.items():
    score_str = f"{category_data['score']:.1f}/{category_data['max_score']}"
    explanation = category_data['explanation'][:50] + "..." if len(category_data['explanation']) > 50 else category_data['explanation']
    
    print(f"{category_name:<30} {score_str:<10} {explanation}")

print("\n" + "=" * 80)
print("EXAMPLE 3: DATABASE STORAGE SIMULATION")
print("=" * 80)

# Example 3: Show database-compatible output
print("\nDatabase-compatible output structure:")
print(f"""
INSERT INTO ai_detector_scores (run_id, provider, score, details)
VALUES (
    '<evaluation_run_id>',
    'internal_rubric',
    {result['score']},
    '{result}'::jsonb  -- Full result as JSONB
);

Details JSONB structure:
- model_version: {result['model_version']}
- timestamp: {result['timestamp']}
- score: {result['score']}
- raw_response.rubric_version: {result['raw_response']['rubric_version']}
- raw_response.total_score: {result['raw_response']['total_score']}
- raw_response.subscores: 6 categories with evidence
- raw_response.metadata: text_length, word_count
""")

print("\n" + "=" * 80)
print("EXAMPLE 4: ERROR HANDLING")
print("=" * 80)

# Example 4: Error handling
test_cases = [
    ("", "Empty text"),
    ("Hi", "Too short (< 5 words)"),
]

for test_text, description in test_cases:
    try:
        score_ai_likeness(test_text)
        print(f"✗ {description}: Should have raised ValueError")
    except ValueError as e:
        print(f"✓ {description}: {e}")

print("\n" + "=" * 80)
print("All examples completed successfully!")
print("=" * 80)
