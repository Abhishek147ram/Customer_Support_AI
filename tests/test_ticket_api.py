from app.config.settings import settings
from app.schemas.llm import LLMReply


async def fake_generate_reply(self, *args, **kwargs):
    return LLMReply(
        recommended_reply="Thank you for reporting your issue. We are looking into it.",
        confidence_score=0.9,
        escalation_recommendation="no",
        escalation_reason="",
        follow_up_actions="Please monitor your account and wait for updates.",
        raw_text="{\"recommended_reply\":\"Thank you\"}",
    )


def test_ticket_process_and_retrieve(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.ticket_service.OllamaClient.generate_reply",
        fake_generate_reply,
    )

    payload = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "subject": "Login issue",
        "description": "I cannot sign in to my account and need assistance.",
    }

    response = client.post("/ticket/process", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Jane Doe"
    assert data["status"]["predicted_category"] in {"account", "other"}
    assert "ai_response" in data

    ticket_id = data["id"]
    get_response = client.get(f"/ticket/{ticket_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == ticket_id

    list_response = client.get("/tickets")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] >= 1
    assert any(ticket["id"] == ticket_id for ticket in list_data["tickets"])
