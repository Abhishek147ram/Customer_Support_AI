from app.services.classifier import classify_ticket


def test_classify_ticket_billing():
    category, confidence = classify_ticket(
        "Payment problem",
        "I was charged twice for my subscription and need a refund.",
    )
    assert category == "billing"
    assert 0.35 <= confidence <= 0.95


def test_classify_ticket_other():
    category, confidence = classify_ticket(
        "Hello",
        "I just wanted to say thank you for the product.",
    )
    assert category == "other"
    assert confidence == 0.45


def test_classify_ticket_empty():
    category, confidence = classify_ticket("", "")
    assert category == "other"
    assert confidence == 0.45
