import re
from typing import List, Tuple

from app.config.logger import logger
from app.services.cache import SimpleMemoryCache, build_cache_key

CACHE = SimpleMemoryCache()

PRIORITY_KEYWORDS = {
    "critical": [
        "urgent",
        "immediately",
        "asap",
        "critical",
        "system down",
        "outage",
        "security",
        "data loss",
        "breach",
    ],
    "high": [
        "important",
        "priority",
        "problem",
        "failure",
        "unable",
        "cannot",
        "error",
        "issue",
        "delayed",
        "delay",
        "late",
    ],
    "normal": [
        "question",
        "help",
        "support",
        "request",
        "ask",
        "follow up",
    ],
    "low": [
        "suggestion",
        "feedback",
        "idea",
        "inquiry",
        "future",
        "schedule",
    ],
}

PRIORITY_LABELS = ["critical", "high", "normal", "low"]
MIN_SCORE = 0.0
MAX_SCORE = 1.0
BASE_SCORE = 0.2


def _normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def _count_keyword_matches(text: str, keywords: List[str]) -> int:
    matches = 0
    for keyword in keywords:
        if keyword in text:
            matches += 1
    return matches


def _normalize_score(score: float) -> float:
    return round(min(MAX_SCORE, max(MIN_SCORE, score)), 2)


def detect_priority(subject: str, description: str) -> Tuple[str, float]:
    """Calculate a ticket priority label and score from text signals."""
    key = build_cache_key("priority", subject, description)
    cached = CACHE.get(key)
    if cached is not None:
        logger.debug(f"Returning cached priority for key={key}")
        return cached

    if not subject and not description:
        logger.warning("Priority detection received empty content")
        return "normal", BASE_SCORE

    text = _normalize_text(f"{subject} {description}")
    logger.debug(f"Priority detection text normalized: {text[:120]}")

    scores = {label: 0 for label in PRIORITY_LABELS}
    for label, keywords in PRIORITY_KEYWORDS.items():
        count = _count_keyword_matches(text, keywords)
        logger.debug(f"Priority '{label}' matched {count} keywords")
        scores[label] += count

    if scores["critical"] > 0:
        score = _normalize_score(BASE_SCORE + 0.55 + scores["critical"] * 0.05)
        label = "critical"
    elif scores["high"] > 0:
        score = _normalize_score(BASE_SCORE + 0.35 + scores["high"] * 0.04)
        label = "high"
    elif scores["low"] > 0 and scores["low"] > scores["normal"]:
        score = _normalize_score(BASE_SCORE + 0.15 + scores["low"] * 0.03)
        label = "low"
    else:
        score = _normalize_score(BASE_SCORE + 0.25 + scores["normal"] * 0.03)
        label = "normal"

    logger.info(
        f"Detected priority={label} with score={score} for ticket text"
    )
    CACHE.set(key, (label, score))
    return label, score
