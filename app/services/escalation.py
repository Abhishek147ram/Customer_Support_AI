from typing import Optional, Tuple

from app.config.logger import logger
from app.config.settings import settings


def should_escalate_ticket(
    llm_confidence: float,
    priority: str,
    priority_score: float,
    predicted_category: Optional[str] = None,
) -> Tuple[bool, str]:
    """Decide whether a ticket should be escalated to a human operator."""
    logger.debug(
        f"Evaluating escalation: confidence={llm_confidence}, priority={priority}, priority_score={priority_score}, category={predicted_category}"
    )

    if llm_confidence < settings.escalation_confidence_threshold:
        reason = (
            f"Low AI confidence ({llm_confidence}) below threshold "
            f"{settings.escalation_confidence_threshold}."
        )
        logger.warning(f"Escalation triggered due to low confidence: {reason}")
        return True, reason

    if priority == "critical" or priority_score >= 0.85:
        reason = (
            f"High priority ticket detected (priority={priority}, score={priority_score}). "
            "Escalation recommended for human review."
        )
        logger.warning(f"Escalation triggered due to priority: {reason}")
        return True, reason

    if predicted_category is None or predicted_category == "other":
        reason = "Ticket category could not be classified with confidence; human review recommended."
        logger.warning(f"Escalation triggered due to category uncertainty: {reason}")
        return True, reason

    logger.info("No escalation needed for ticket at current thresholds")
    return False, ""


def build_escalation_payload(
    ticket_id: int,
    customer_email: str,
    subject: str,
    priority: str,
    predicted_category: Optional[str],
    escalation_reason: str,
) -> dict:
    """Build a structured payload for human escalation workflows."""
    payload = {
        "ticket_id": ticket_id,
        "customer_email": customer_email,
        "subject": subject,
        "priority": priority,
        "predicted_category": predicted_category or "unknown",
        "escalation_reason": escalation_reason,
        "action_required": "Review ticket and provide human response.",
    }
    logger.debug(f"Escalation payload constructed: {payload}")
    return payload
