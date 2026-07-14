"""Score SxS comparative rationales for technical specificity and rubric alignment."""
from typing import Dict

TECHNICAL_MARKERS = {
    "complexity", "edge case", "runtime", "syntax", "exception",
    "typeerror", "valueerror", "memory", "test", "refactor", "diff"
}

def compute_rationale_metrics(rationale: str) -> Dict[str, object]:
    words = rationale.strip().split()
    lower_text = rationale.lower()
    matched_terms = sorted(term for term in TECHNICAL_MARKERS if term in lower_text)
    return {
        "word_count": len(words),
        "technical_term_count": len(matched_terms),
        "matched_terms": matched_terms,
    }
