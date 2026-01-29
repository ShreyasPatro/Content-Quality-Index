# AI Rubric Scoring Engine

## Overview

A deterministic, heuristic-based AI-likeness scoring engine that analyzes text for patterns commonly found in AI-generated content. No machine learning models required - uses statistical analysis and pattern matching only.

## Architecture

```
app/services/ai_rubric/
├── __init__.py          # Package exports
├── types.py             # Type definitions (CategoryScore, RubricResult)
├── scorer.py            # Main scoring engine
└── example.py           # Usage examples
```

## Rubric Categories

### 1. Predictability & Entropy (0-25 points)

**Measures**: Text diversity and randomness

**Signals**:
- **Lexical diversity** (10 pts): Ratio of unique words to total words
  - < 0.4 = 10 points (very repetitive)
  - 0.4-0.5 = 7 points (low diversity)
  - 0.5-0.6 = 4 points (moderate)
  - > 0.6 = 0 points (high diversity)

- **Word length variance** (8 pts): Standard deviation of word lengths
  - σ < 2.0 = 8 points (very uniform)
  - σ 2.0-2.5 = 5 points (low variance)
  - σ > 2.5 = 0 points (natural variance)

- **Repetition patterns** (7 pts): Most frequent word ratio
  - > 5% = 7 points (high repetition)
  - 3-5% = 4 points (moderate)
  - < 3% = 0 points (low repetition)

### 2. Sentence & Paragraph Uniformity (0-20 points)

**Measures**: Mechanical consistency

**Signals**:
- **Sentence length uniformity** (12 pts): Coefficient of variation
  - CV < 0.3 = 12 points (very uniform)
  - CV 0.3-0.5 = 7 points (moderately uniform)
  - CV > 0.5 = 0 points (natural variance)

- **Paragraph uniformity** (8 pts): Paragraph length consistency
  - CV < 0.3 = 8 points (very uniform)
  - CV 0.3-0.5 = 4 points (moderately uniform)
  - CV > 0.5 = 0 points (natural variance)

### 3. Generic Language & Clichés (0-20 points)

**Measures**: Overused AI phrases and buzzwords

**Signals**:
- **AI phrase detection** (15 pts): Count of common AI phrases
  - ≥ 5 phrases = 15 points
  - 3-4 phrases = 10 points
  - 1-2 phrases = 5 points
  - 0 phrases = 0 points

  **Common AI phrases**:
  - "it's important to note", "it's worth noting"
  - "in today's digital age", "in conclusion"
  - "delve into", "navigate the landscape"
  - "myriad of", "plethora of"
  - "leverage", "utilize", "facilitate"
  - "robust", "comprehensive", "holistic"

- **Adverb overuse** (5 pts): Ratio of -ly words
  - > 5% = 5 points (high usage)
  - 3-5% = 2 points (moderate)
  - < 3% = 0 points (normal)

### 4. Structural Template Signals (0-15 points)

**Measures**: Formulaic patterns

**Signals**:
- **Formulaic openings** (8 pts): Template-based introductions
  - "In this article/post/guide..."
  - "Let's explore/discuss/examine..."
  - "Have you ever/Are you..."

- **Numbered lists** (4 pts): Heavy list structure
  - ≥ 5 items = 4 points
  - 3-4 items = 2 points
  - < 3 items = 0 points

- **Transition phrases** (3 pts): Mechanical transitions
  - ≥ 4 transitions = 3 points
  - 2-3 transitions = 1.5 points
  - < 2 transitions = 0 points

### 5. Lack of Human Friction (0-10 points)

**Measures**: Absence of natural errors and informality

**Signals**:
- **Perfect capitalization** (4 pts): All sentences capitalized
  - 100% capitalized (≥3 sentences) = 4 points
  - < 100% = 0 points

- **Lack of contractions** (3 pts): Overly formal
  - < 1% contractions = 3 points
  - 1-2% = 1.5 points
  - > 2% = 0 points

- **Lack of informal markers** (3 pts): No casual language
  - 0 markers (>50 words) = 3 points
  - Any markers = 0 points

### 6. Over-Polish & Safety Tone (0-10 points)

**Measures**: Hedging and disclaimers

**Signals**:
- **Safety/hedging phrases** (7 pts): Excessive caution
  - ≥ 4 phrases = 7 points
  - 2-3 phrases = 4 points
  - 1 phrase = 2 points
  - 0 phrases = 0 points

  **Hedging phrases**:
  - "generally speaking", "in most cases"
  - "typically", "usually", "often"
  - "may be", "might be", "could be"
  - "consult a professional"

- **Disclaimer patterns** (3 pts): Warning language
  - ≥ 2 disclaimers = 3 points
  - 1 disclaimer = 1.5 points
  - 0 disclaimers = 0 points

## Usage

### Basic Usage

```python
from app.services.ai_rubric import score_text_rubric

text = "Your content here..."
result = score_text_rubric(text)

print(f"Total AI-likeness: {result.total_score:.2f}/100")
print(f"Predictability: {result.predictability_entropy['score']:.1f}/25")
print(f"Explanation: {result.predictability_entropy['explanation']}")
```

### Result Structure

```python
@dataclass
class RubricResult:
    total_score: float  # 0-100 (higher = more AI-like)
    predictability_entropy: CategoryScore  # 0-25
    sentence_uniformity: CategoryScore     # 0-20
    generic_language: CategoryScore        # 0-20
    structural_templates: CategoryScore    # 0-15
    lack_of_friction: CategoryScore        # 0-10
    over_polish: CategoryScore             # 0-10
    text_length: int                       # Character count
    word_count: int                        # Word count
```

### Category Score Structure

```python
class CategoryScore(TypedDict):
    score: float           # Actual score (0-max_score)
    max_score: float       # Maximum possible for category
    percentage: float      # score / max_score * 100
    explanation: str       # Human-readable explanation
```

### JSON Export

```python
result = score_text_rubric(text)
json_data = result.to_dict()

# Returns:
{
    "total_score": 45.5,
    "categories": {
        "predictability_entropy": {
            "score": 12.0,
            "max_score": 25.0,
            "percentage": 48.0,
            "explanation": "Low lexical diversity (0.45) | ..."
        },
        ...
    },
    "metadata": {
        "text_length": 1234,
        "word_count": 234
    }
}
```

## Determinism Guarantees

### ✅ Deterministic
- Same input text → Same output score (always)
- No randomness or probabilistic elements
- No external dependencies (no API calls, no DB)
- No I/O operations
- Pure function with no side effects

### ✅ Explainable
- Every score includes human-readable explanation
- Signals are transparent and auditable
- No "black box" ML models
- Easy to debug and validate

## Scoring Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| 0-20 | Very human-like (natural, informal, varied) |
| 21-40 | Likely human (some AI-like patterns) |
| 41-60 | Ambiguous (could be human or AI) |
| 61-80 | Likely AI (many AI-like patterns) |
| 81-100 | Very AI-like (formulaic, generic, polished) |

## Example Scores

### AI-Generated Text
```
Total: 68.5/100

Breakdown:
- Predictability: 15/25 (low diversity, uniform word lengths)
- Uniformity: 12/20 (very consistent sentence lengths)
- Generic Language: 15/20 (5 AI phrases, high adverb usage)
- Templates: 11/15 (formulaic opening, heavy lists)
- Friction: 8/10 (perfect capitalization, no contractions)
- Polish: 7.5/10 (heavy hedging, multiple disclaimers)
```

### Human-Written Text
```
Total: 18.0/100

Breakdown:
- Predictability: 4/25 (high diversity, natural variance)
- Uniformity: 0/20 (varied sentence lengths)
- Generic Language: 5/20 (1 AI phrase)
- Templates: 0/15 (natural opening, no lists)
- Friction: 0/10 (contractions, informal markers)
- Polish: 9/10 (some hedging)
```

## Limitations

### Not a Replacement for ML Detectors
- This is a **heuristic complement** to ML-based detectors
- Use alongside Originality.ai, GPTZero, etc.
- Provides explainable signals that ML models cannot

### False Positives
- Formal academic writing may score high
- Technical documentation may score high
- Well-edited human content may score moderately high

### False Negatives
- Heavily edited AI content may score lower
- AI prompted to "write casually" may score lower
- Short texts (< 100 words) may not have enough signals

## Integration with Evaluation Pipeline

```python
# In app/workflows/evaluation.py
from app.services.ai_rubric import score_text_rubric

async def run_rubric_scoring(run_id: UUID, content: dict) -> None:
    """Run AI rubric scoring as part of evaluation."""
    text = content.get("body", "")
    
    # Score the text
    result = score_text_rubric(text)
    
    # Store in ai_detector_scores table
    await conn.execute(
        ai_detector_scores.insert().values(
            run_id=run_id,
            provider="internal_rubric",
            score=result.total_score,
            details={
                "categories": result.to_dict()["categories"],
                "model_version": "1.0",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    )
```

## Testing

```python
# Test determinism
text = "Sample text here..."
result1 = score_text_rubric(text)
result2 = score_text_rubric(text)
assert result1.total_score == result2.total_score  # Always true

# Test minimum length
try:
    score_text_rubric("Hi")  # Too short
except ValueError as e:
    print(e)  # "Text too short (minimum 5 words required)"

# Test empty text
try:
    score_text_rubric("")
except ValueError as e:
    print(e)  # "Text cannot be empty"
```

## Performance

- **Speed**: Not optimized (focus on explainability)
- **Typical runtime**: 10-50ms for 1000-word text
- **Memory**: Minimal (no model loading)
- **Scalability**: Can process thousands of texts per second

## Future Enhancements

Potential improvements (not implemented):
- Sentiment analysis (AI tends to be neutral)
- Named entity patterns (AI uses generic examples)
- Readability scores (AI targets specific reading levels)
- Punctuation patterns (AI uses consistent punctuation)
- Emoji/emoticon usage (AI rarely uses these)

## References

Based on research into AI-generated content patterns:
- Common AI phrases from GPT-3/GPT-4 outputs
- Statistical analysis of AI vs human writing
- Linguistic markers of machine-generated text
- Content quality heuristics
