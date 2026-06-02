import asyncio

import httpx


def test_ticket_process_load(client):
    payload = {
        "customer_name": "Load Test User",
        "customer_email": "load@example.com",
        "subject": "Performance test",
        "description": "I am testing the ticket processing endpoint under light load.",
    }

    def send_request(i: int):
        response = client.post("/ticket/process", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == payload["customer_name"]

    for i in range(5):
        send_request(i)


def test_llm_health_endpoint(client):
    response = client.get("/health/llm")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "llm_ready" in data
    assert "llm_health" in data
