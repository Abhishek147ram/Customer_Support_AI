import pytest

from app.schemas.llm import LLMReply
from app.services.llm_service import OllamaClient


def test_extract_json_snippet():
    client = OllamaClient()
    sample = "Some text before {\"recommended_reply\": \"Hello\", \"confidence_score\": 0.8} trailing text"
    snippet = client._extract_json_snippet(sample)
    assert snippet is not None
    assert "recommended_reply" in snippet


def test_parse_structured_response():
    client = OllamaClient()
    sample = '{"recommended_reply":"Thanks","confidence_score":0.7,"escalation_recommendation":"no","escalation_reason":"","follow_up_actions":"Please wait."}'
    reply = client._parse_structured_response(sample)
    assert isinstance(reply, LLMReply)
    assert reply.recommended_reply == "Thanks"
    assert reply.confidence_score == 0.7
    assert reply.escalation_recommendation == "no"


def test_extract_json_snippet_failure():
    client = OllamaClient()
    assert client._extract_json_snippet("no json here") is None


def test_completion_has_text():
    client = OllamaClient()

    assert client._completion_has_text({"text": "Hello"})
    assert client._completion_has_text({"choices": [{"text": "World"}]})
    assert client._completion_has_text({"choices": [{"message": {"content": "Hi"}}]})
    assert client._completion_has_text({"results": [{"content": "Ok"}]})
    assert not client._completion_has_text({"choices": [{"text": ""}]})
