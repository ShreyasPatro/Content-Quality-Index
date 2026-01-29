"""Example usage of AI rubric scorer."""

from app.services.ai_rubric import score_text_rubric

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

result = score_text_rubric(ai_text)
print(f"Total AI-likeness score: {result.total_score:.2f}/100")
print(f"\nCategory Breakdown:")
print(f"  Predictability & Entropy: {result.predictability_entropy['score']:.1f}/25")
print(f"    → {result.predictability_entropy['explanation']}")
print(f"  Sentence Uniformity: {result.sentence_uniformity['score']:.1f}/20")
print(f"    → {result.sentence_uniformity['explanation']}")
print(f"  Generic Language: {result.generic_language['score']:.1f}/20")
print(f"    → {result.generic_language['explanation']}")
print(f"  Structural Templates: {result.structural_templates['score']:.1f}/15")
print(f"    → {result.structural_templates['explanation']}")
print(f"  Lack of Friction: {result.lack_of_friction['score']:.1f}/10")
print(f"    → {result.lack_of_friction['explanation']}")
print(f"  Over-Polish: {result.over_polish['score']:.1f}/10")
print(f"    → {result.over_polish['explanation']}")

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

result2 = score_text_rubric(human_text)
print(f"\n\nHuman text score: {result2.total_score:.2f}/100")
print(f"(Lower score = more human-like)")
