"""
Summarization service: extractive (rule-based) summarization.

Provides: summary, key points, and action item extraction.
This is a simple, fast, deterministic approach — no heavy ML models needed.
"""

import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

# Common English stop words
STOP_WORDS = set(
    "i me my myself we our ours ourselves you your yours yourself yourselves "
    "he him his himself she her hers herself it its itself they them their "
    "theirs themselves what which who whom this that these those am is are was "
    "were be been being have has had having do does did doing a an the and but "
    "if or because as until while of at by for with about against between through "
    "during before after above below to from up down in out on off over under "
    "again further then once here there when where why how all both each few more "
    "most other some such no nor not only own same so than too very s t can will "
    "just don should now d ll m o re ve y ain aren couldn didn doesn hadn hasn "
    "haven isn ma mightn mustn needn shan shouldn wasn weren won wouldn "
    "also would could may might shall well really actually going got let "
    "like thing things know think go get make right um uh yeah okay".split()
)

# Patterns that indicate action items
ACTION_PATTERNS = [
    r"\baction item[s]?\b[:\s]*(.*?)(?:\.|$)",
    r"\bneed[s]? to\b(.*?)(?:\.|$)",
    r"\bshould\b(.*?)(?:\.|$)",
    r"\bwill\b(.*?)(?:\.|$)",
    r"\bmust\b(.*?)(?:\.|$)",
    r"\btodo\b[:\s]*(.*?)(?:\.|$)",
    r"\bto[\s-]?do\b[:\s]*(.*?)(?:\.|$)",
    r"\bfollow[\s-]?up\b(.*?)(?:\.|$)",
    r"\bdeadline\b(.*?)(?:\.|$)",
    r"\bby (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next week|end of)\b(.*?)(?:\.|$)",
    r"\bassign(?:ed)?\b(.*?)(?:\.|$)",
    r"\bschedule\b(.*?)(?:\.|$)",
    r"\bmake sure\b(.*?)(?:\.|$)",
]


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Simple sentence splitting on . ! ? followed by space or end
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    # Filter out very short sentences
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _score_sentences(sentences: list[str]) -> list[tuple[float, int, str]]:
    """Score sentences by word importance (TF-based)."""
    # Build word frequency from all sentences
    all_words = []
    for sentence in sentences:
        words = re.findall(r"\b[a-z]+\b", sentence.lower())
        all_words.extend(w for w in words if w not in STOP_WORDS and len(w) > 2)

    word_freq = Counter(all_words)
    if not word_freq:
        return [(0.0, i, s) for i, s in enumerate(sentences)]

    max_freq = max(word_freq.values())

    # Normalize frequencies
    for word in word_freq:
        word_freq[word] /= max_freq

    # Score each sentence
    scored = []
    for i, sentence in enumerate(sentences):
        words = re.findall(r"\b[a-z]+\b", sentence.lower())
        if not words:
            scored.append((0.0, i, sentence))
            continue

        score = sum(word_freq.get(w, 0) for w in words) / len(words)

        # Boost first and last sentences slightly (often contain key info)
        if i == 0:
            score *= 1.2
        elif i == len(sentences) - 1:
            score *= 1.1

        scored.append((score, i, sentence))

    return scored


def extract_summary(text: str, num_sentences: int = 5) -> str:
    """
    Generate an extractive summary by selecting the most important sentences.

    Args:
        text: The full transcript text.
        num_sentences: Number of sentences to include in summary.

    Returns:
        Summary string (selected sentences in original order).
    """
    if not text or not text.strip():
        return ""

    sentences = _split_sentences(text)

    if len(sentences) <= num_sentences:
        return text.strip()

    scored = _score_sentences(sentences)

    # Select top sentences
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:num_sentences]

    # Return in original order
    top_in_order = sorted(top, key=lambda x: x[1])

    return " ".join(s[2] for s in top_in_order)


def extract_key_points(text: str, max_points: int = 7) -> list[str]:
    """
    Extract key points from text.

    Uses sentence importance scoring to identify the most significant statements.
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return []

    scored = _score_sentences(sentences)
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:max_points]
    top_in_order = sorted(top, key=lambda x: x[1])

    # Clean up and format as bullet points
    points = []
    for _, _, sentence in top_in_order:
        # Remove trailing period for cleaner bullet points
        point = sentence.rstrip(".")
        if point and len(point) > 15:
            points.append(point)

    return points


def extract_action_items(text: str) -> list[str]:
    """
    Extract action items from text using pattern matching.

    Looks for phrases like "need to", "should", "action item:", "will", etc.
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    action_items = []
    seen = set()

    for sentence in sentences:
        for pattern in ACTION_PATTERNS:
            if re.search(pattern, sentence, re.IGNORECASE):
                # Clean up the sentence
                item = sentence.strip().rstrip(".")
                # Deduplicate
                item_lower = item.lower()
                if item_lower not in seen and len(item) > 15:
                    seen.add(item_lower)
                    action_items.append(item)
                break  # Don't match same sentence with multiple patterns

    return action_items


def summarize_transcript(
    text: str, num_sentences: int = 5
) -> dict:
    """
    Full summarization pipeline: summary + key points + action items.

    For long transcripts (>50 sentences), uses a map-reduce approach:
    1. Split into segments
    2. Summarize each segment
    3. Combine and re-summarize

    Args:
        text: Full transcript text.
        num_sentences: Target number of summary sentences.

    Returns:
        dict with 'summary', 'key_points', 'action_items'
    """
    if not text or not text.strip():
        return {"summary": "", "key_points": [], "action_items": []}

    sentences = _split_sentences(text)

    # Map-reduce for long transcripts
    if len(sentences) > 50:
        logger.info(f"Long transcript ({len(sentences)} sentences), using map-reduce.")
        return _map_reduce_summarize(text, sentences, num_sentences)

    summary = extract_summary(text, num_sentences)
    key_points = extract_key_points(text, max_points=7)
    action_items = extract_action_items(text)

    return {
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
    }


def _map_reduce_summarize(
    text: str, sentences: list[str], num_sentences: int
) -> dict:
    """Map-reduce summarization for long transcripts."""
    # Split into segments of ~20 sentences
    segment_size = 20
    segments = []
    for i in range(0, len(sentences), segment_size):
        segment = " ".join(sentences[i : i + segment_size])
        segments.append(segment)

    # Map: extract summary from each segment
    segment_summaries = []
    for segment in segments:
        segment_summary = extract_summary(segment, num_sentences=3)
        segment_summaries.append(segment_summary)

    # Reduce: summarize the combined segment summaries
    combined = " ".join(segment_summaries)
    summary = extract_summary(combined, num_sentences)

    # Extract action items from full text (patterns are local)
    action_items = extract_action_items(text)

    # Key points from combined summaries
    key_points = extract_key_points(combined, max_points=7)

    return {
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
    }
