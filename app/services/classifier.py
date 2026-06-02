import re
from typing import Dict, Tuple

from app.config.logger import logger
from app.services.cache import SimpleMemoryCache, build_cache_key

CACHE = SimpleMemoryCache()

CATEGORY_KEYWORDS = {
    "billing": [
        "invoice", "payment", "billing", "refund",
        "charge", "subscription", "receipt", "price",
        "money", "paid"
    ],

    "technical": [
        "error", "bug", "crash", "issue",
        "failure", "slow", "disconnect",
        "timeout", "not working", "problem",
        "broken", "exception"
    ],

    "account": [
        "login", "log in", "password",
        "account", "sign in", "signin",
        "authentication", "profile",
        "access", "credential",
        "reset password"
    ],

    "shipping": [
        "delivery", "shipment", "tracking",
        "package", "shipping", "received",
        "lost", "delay", "courier"
    ],

    "product": [
        "feature", "quality", "warranty",
        "replacement", "repair",
        "defect", "item", "product"
    ],

    "complaint": [
        "complaint", "angry",
        "unhappy", "poor",
        "frustrated", "disappointed",
        "unsatisfied", "terrible"
    ],
}

FALLBACK_CATEGORY = "other"

DEFAULT_CONFIDENCE = 0.45
MIN_CONFIDENCE = 0.35
MAX_CONFIDENCE = 0.95


def _normalize_text(text: str) -> str:

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def _score_matches(
    matches: int,
    total_words: int
) -> float:

    if matches <= 0:

        return DEFAULT_CONFIDENCE

    ratio = matches / max(
        total_words,
        1
    )

    confidence = (
        0.50 +
        (ratio * 2.5)
    )

    confidence = max(
        MIN_CONFIDENCE,
        min(
            confidence,
            MAX_CONFIDENCE
        )
    )

    return round(
        confidence,
        2
    )


def _count_keyword_hits(
    text: str,
    keywords: list
) -> int:

    hits = 0

    for keyword in keywords:

        if keyword in text:
            hits += 1

    return hits


def classify_ticket(
    subject: str,
    description: str
) -> Tuple[str, float]:

    cache_key = build_cache_key(
        "classify",
        subject,
        description
    )

    cached = CACHE.get(
        cache_key
    )

    if cached:

        return cached

    if not subject and not description:

        logger.warning(
            "Empty ticket text"
        )

        return (
            FALLBACK_CATEGORY,
            DEFAULT_CONFIDENCE
        )

    text = _normalize_text(
        f"{subject} {description}"
    )

    total_words = len(
        text.split()
    )

    category_scores: Dict[
        str,
        int
    ] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        category_scores[
            category
        ] = _count_keyword_hits(
            text,
            keywords
        )

    logger.info(
        f"Category scores={category_scores}"
    )

    best_category = max(
        category_scores,
        key=category_scores.get
    )

    best_score = category_scores[
        best_category
    ]

    if best_score <= 0:

        logger.warning(
            "Fallback category selected"
        )

        result = (
            FALLBACK_CATEGORY,
            DEFAULT_CONFIDENCE
        )

        CACHE.set(
            cache_key,
            result
        )

        return result

    confidence = _score_matches(
        best_score,
        total_words
    )

    result = (
        best_category,
        confidence
    )

    logger.info(
        f"Predicted={best_category}, confidence={confidence}"
    )

    CACHE.set(
        cache_key,
        result
    )

    return result