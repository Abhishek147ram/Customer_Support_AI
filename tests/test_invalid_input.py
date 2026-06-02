import pytest

from fastapi.testclient import TestClient


def test_ticket_process_missing_fields(client: TestClient):
    response = client.post("/ticket/process", json={"customer_name": "Jane"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_ticket_process_invalid_email(client: TestClient):
    payload = {
        "customer_name": "Jane Doe",
        "customer_email": "not-an-email",
        "subject": "Help",
        "description": "This is a valid description with enough length.",
    }
    response = client.post("/ticket/process", json=payload)
    assert response.status_code == 422
    error_messages = [err["msg"] for err in response.json()["detail"]]
    assert any("value is not a valid email address" in msg for msg in error_messages)


def test_ticket_process_subject_too_short(client: TestClient):
    payload = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "subject": "Hi",
        "description": "This is a valid description with enough length.",
    }
    response = client.post("/ticket/process", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()
