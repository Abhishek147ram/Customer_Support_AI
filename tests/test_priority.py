from app.services.priority import detect_priority


def test_detect_priority_critical():
    label, score = detect_priority(
        "System outage",
        "Our platform is down and customers cannot access the service.",
    )
    assert label == "critical"
    assert score >= 0.75


def test_detect_priority_normal():
    label, score = detect_priority(
        "Account help",
        "I need help updating my profile settings.",
    )
    assert label == "normal"
    assert 0.2 <= score <= 0.5


def test_detect_priority_low():
    label, score = detect_priority(
        "Feature suggestion",
        "I have an idea for a future update.",
    )
    assert label == "low"
    assert score < 0.35 or label == "low"
