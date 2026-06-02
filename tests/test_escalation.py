from app.services.escalation import should_escalate_ticket


def test_should_escalate_low_confidence():
    escalate, reason = should_escalate_ticket(
        llm_confidence=0.4,
        priority="normal",
        priority_score=0.3,
        predicted_category="billing",
    )
    assert escalate is True
    assert "Low AI confidence" in reason


def test_should_escalate_critical_priority():
    escalate, reason = should_escalate_ticket(
        llm_confidence=0.9,
        priority="critical",
        priority_score=0.9,
        predicted_category="technical",
    )
    assert escalate is True
    assert "High priority" in reason


def test_should_not_escalate():
    escalate, reason = should_escalate_ticket(
        llm_confidence=0.9,
        priority="normal",
        priority_score=0.3,
        predicted_category="billing",
    )
    assert escalate is False
    assert reason == ""
