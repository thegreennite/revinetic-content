"""Check a candidate post against recent history for repetition.

Five dimensions, matching the v2 spec:
  - topic duplication   (same subject matter)
  - hook duplication     (same opening structure/pattern)
  - angle duplication     (same argument/observation, reworded)
  - visual duplication    (same composition/subject/setting)
  - source duplication     (over-reliance on one creator inspiration)

This is deliberately simple, deterministic text-similarity, not a model call —
duplication checking should be fast, free, and not itself require an LLM or
API credits to run before every post.
"""

from __future__ import annotations

import difflib
import json
import re
from collections import Counter
from typing import Any

DEFAULT_LOOKBACK_DAYS = 10
# Calibrated 2026-08-11 against real session data: the two same-day HVAC
# voice-agent posts (a genuine duplicate, different numbers/wording) scored
# topic=1.0, hook=0.08, angle=0.29. A genuinely different pair scored
# topic=0.11, hook=0.0, angle=0.055. Hook overlap alone is too thin a
# margin (0.08 vs 0.0) to trust as a standalone trigger for this class of
# duplicate - topic and angle carry the real signal.
HOOK_SIMILARITY_THRESHOLD = 0.35
ANGLE_SIMILARITY_THRESHOLD = 0.2
TOPIC_KEYWORD_OVERLAP_THRESHOLD = 0.5
SOURCE_OVERSATURATION_RATIO = 0.6  # e.g. 3 of last 5 all from one creator


def load_history(path: str) -> list[dict[str, Any]]:
    with open(path) as f:
        return json.load(f)


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()


def _keywords(text: str, min_len: int = 4) -> set[str]:
    stopwords = {
        "that", "this", "with", "your", "have", "just", "from", "they",
        "them", "then", "than", "what", "when", "were", "here", "there",
        "been", "into", "about", "still", "some", "most", "will", "does",
    }
    words = [w for w in _normalize(text).split() if len(w) >= min_len and w not in stopwords]
    return set(words)


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def check_topic_duplication(candidate_topic: str, history: list[dict]) -> list[dict]:
    """Keyword-overlap check: catches 'same subject, different words' repeats."""
    candidate_kw = _keywords(candidate_topic)
    hits = []
    for record in history:
        past_kw = _keywords(record.get("topic", ""))
        if not candidate_kw or not past_kw:
            continue
        overlap = len(candidate_kw & past_kw) / max(1, len(candidate_kw | past_kw))
        if overlap >= TOPIC_KEYWORD_OVERLAP_THRESHOLD:
            hits.append({"date": record.get("date"), "topic": record.get("topic"), "overlap": round(overlap, 2)})
    return hits


def _keyword_overlap(a: str, b: str) -> float:
    """Jaccard overlap on keywords - robust to 'same idea, different specific
    numbers/wording', unlike character-sequence similarity. Two posts about
    the same concept with different stats/phrasing (e.g. '37 missed calls'
    vs '1 in 3 after hours calls', both about an HVAC voice agent) still
    share enough distinctive nouns to be caught here even though a
    character-level diff would call them almost entirely different strings.
    """
    kw_a, kw_b = _keywords(a), _keywords(b)
    if not kw_a or not kw_b:
        return 0.0
    return len(kw_a & kw_b) / max(1, len(kw_a | kw_b))


def check_hook_duplication(candidate_hook: str, history: list[dict]) -> list[dict]:
    hits = []
    for record in history:
        past_hook = record.get("hook", "")
        if not past_hook:
            continue
        overlap = _keyword_overlap(candidate_hook, past_hook)
        if overlap >= HOOK_SIMILARITY_THRESHOLD:
            hits.append({"date": record.get("date"), "hook": past_hook, "overlap": round(overlap, 2)})
    return hits


def check_angle_duplication(candidate_caption: str, history: list[dict]) -> list[dict]:
    """Keyword-overlap on the full caption body - catches 'same argument,
    reworded' repeats, which is exactly what the two HVAC-voice-agent posts
    on 2026-08-11 were (different numbers, same underlying story/argument)."""
    hits = []
    for record in history:
        past_caption = record.get("caption", "")
        if not past_caption or len(past_caption) < 20:
            continue
        overlap = _keyword_overlap(candidate_caption, past_caption)
        if overlap >= ANGLE_SIMILARITY_THRESHOLD:
            hits.append({"date": record.get("date"), "topic": record.get("topic"), "overlap": round(overlap, 2)})
    return hits


def check_visual_duplication(candidate_visual: dict, history: list[dict]) -> list[dict]:
    """Compares subject+setting+style as a set - repeats of the same visual recipe."""
    hits = []
    candidate_signature = {
        candidate_visual.get("visual_subject"),
        candidate_visual.get("visual_setting"),
        candidate_visual.get("visual_style"),
    } - {None}
    if not candidate_signature:
        return hits
    for record in history:
        past_signature = {record.get("visual_subject"), record.get("visual_setting"), record.get("visual_style")} - {None}
        if not past_signature:
            continue
        overlap = len(candidate_signature & past_signature)
        if overlap >= 2:  # at least 2 of 3 visual dimensions match
            hits.append({"date": record.get("date"), "visual_subject": record.get("visual_subject"),
                         "visual_setting": record.get("visual_setting"), "visual_style": record.get("visual_style")})
    return hits


def check_source_saturation(candidate_source: str | None, history: list[dict], window: int = 5) -> dict | None:
    if not candidate_source:
        return None
    recent = history[-window:]
    sources = [r.get("creator_inspiration") for r in recent if r.get("creator_inspiration")]
    if not sources:
        return None
    counts = Counter(sources)
    counts[candidate_source] += 1
    total = len(recent) + 1
    ratio = counts[candidate_source] / total
    if ratio >= SOURCE_OVERSATURATION_RATIO:
        return {"source": candidate_source, "ratio": round(ratio, 2), "window": window}
    return None


def check_candidate(candidate: dict, history_path: str) -> dict:
    """Run all five checks. Returns a report with a simple pass/warn verdict."""
    history = load_history(history_path)

    report = {
        "topic_duplication": check_topic_duplication(candidate.get("topic", ""), history),
        "hook_duplication": check_hook_duplication(candidate.get("hook", ""), history),
        "angle_duplication": check_angle_duplication(candidate.get("caption", ""), history),
        "visual_duplication": check_visual_duplication(candidate, history),
        "source_saturation": check_source_saturation(candidate.get("creator_inspiration"), history),
    }
    flags = []
    if report["topic_duplication"]:
        flags.append(f"TOPIC_DUPLICATION: overlaps with {len(report['topic_duplication'])} recent post(s)")
    if report["hook_duplication"]:
        flags.append(f"HOOK_DUPLICATION: similar to {len(report['hook_duplication'])} recent hook(s)")
    if report["angle_duplication"]:
        flags.append(f"ANGLE_DUPLICATION: similar argument to {len(report['angle_duplication'])} recent post(s)")
    if report["visual_duplication"]:
        flags.append(f"VISUAL_DUPLICATION: same visual recipe as {len(report['visual_duplication'])} recent post(s)")
    if report["source_saturation"]:
        flags.append(f"SOURCE_SATURATION: {report['source_saturation']['source']} is {int(report['source_saturation']['ratio']*100)}% of recent posts")

    report["flags"] = flags
    report["verdict"] = "WARN" if flags else "PASS"
    return report


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 duplication_check.py <history.json>")
        raise SystemExit(1)

    # Self-test using the two known-duplicate HVAC posts already in history.
    history = load_history(sys.argv[1])
    hvac_v2 = next(r for r in history if "1 in 3 after hours" in r.get("hook", ""))
    earlier_history = [r for r in history if r is not hvac_v2]

    # Rebuild using only earlier records so hvac_v2 doesn't match itself
    import json as _json
    tmp_path = "/tmp/_history_test.json"
    with open(tmp_path, "w") as f:
        _json.dump(earlier_history, f)
    result = check_candidate(hvac_v2, tmp_path)

    print("--- Test 1: known real duplicate (should WARN) ---")
    print(json.dumps(result, indent=2))
    assert result["verdict"] == "WARN", "Expected the known HVAC duplicate to be flagged"
    assert any("TOPIC_DUPLICATION" in f or "ANGLE_DUPLICATION" in f for f in result["flags"]), \
        "Expected topic or angle duplication specifically"
    print("PASS: known duplicate correctly detected\n")

    # Negative control: a genuinely different post should NOT be flagged.
    genuinely_new = {
        "topic": "Seasonal Black Friday automation checklist for local service businesses",
        "hook": "Black Friday isn't just for retail. Here's what your inbox looks like if you're not ready.",
        "caption": "Black Friday isn't just for retail. Here's what your inbox looks like if you're not ready.\n\nLocal service businesses get a real spike in November too, quote requests, gift-card questions, end-of-year bookings. Most of that traffic hits after hours when nobody's watching the phone.\n\nSave this before the rush hits.",
        "creator_inspiration": None,
    }
    result2 = check_candidate(genuinely_new, sys.argv[1])
    print("--- Test 2: genuinely new post (should PASS) ---")
    print(json.dumps(result2, indent=2))
    assert result2["verdict"] == "PASS", f"Expected a genuinely new post to pass, got: {result2['flags']}"
    print("PASS: genuinely new content correctly NOT flagged")
