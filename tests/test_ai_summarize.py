import json
from unittest.mock import patch, Mock
import pytest
from ai_summarize import generate_summary, make_fallback_summary

_SAMPLE_REPO = {
    "name": "cool-tool",
    "description": "A CLI tool for managing config files",
    "topics": ["cli", "config"],
    "language": "Python",
}

def _mock_ai_response(summary, category, tags):
    payload = json.dumps({"summary": summary, "category": category, "tags": tags})
    m = Mock()
    m.status_code = 200
    m.json.return_value = {"choices": [{"message": {"content": payload}}]}
    m.raise_for_status = Mock()
    return m

def test_generate_summary_returns_correct_fields():
    with patch("ai_summarize.requests.post", return_value=_mock_ai_response(
        "A tool that manages config files across projects with a single command.",
        "tools",
        ["CLI Tool", "Config Management"],
    )):
        result = generate_summary(_SAMPLE_REPO, "# Cool Tool\nManage configs.", "token")
    assert result["summary"] == "A tool that manages config files across projects with a single command."
    assert result["category"] == "tools"
    assert "CLI Tool" in result["tags"]

def test_generate_summary_omits_readme_excerpt_when_none():
    captured = {}
    def capture(*args, **kwargs):
        captured["json"] = kwargs.get("json", {})
        return _mock_ai_response("summary", "tools", ["CLI"])
    with patch("ai_summarize.requests.post", side_effect=capture):
        generate_summary(_SAMPLE_REPO, None, "token")
    user_msg = captured["json"]["messages"][1]["content"]
    assert "README" not in user_msg

def test_generate_summary_uses_correct_endpoint():
    captured = {}
    def capture(url, **kwargs):
        captured["url"] = url
        return _mock_ai_response("summary", "other", [])
    with patch("ai_summarize.requests.post", side_effect=capture):
        generate_summary(_SAMPLE_REPO, None, "token")
    assert captured["url"] == "https://models.github.ai/inference/chat/completions"

def test_generate_summary_uses_correct_model():
    captured = {}
    def capture(url, **kwargs):
        captured["json"] = kwargs["json"]
        return _mock_ai_response("summary", "other", [])
    with patch("ai_summarize.requests.post", side_effect=capture):
        generate_summary(_SAMPLE_REPO, None, "token")
    assert captured["json"]["model"] == "openai/gpt-4o-mini"

def test_make_fallback_with_description():
    repo = {"name": "my-tool", "description": "Does something useful", "language": "Go"}
    result = make_fallback_summary(repo)
    assert result["category"] == "other"
    assert result["tags"] == []
    assert len(result["summary"]) > 0

def test_make_fallback_no_description():
    repo = {"name": "my-tool", "description": None, "language": "Python"}
    result = make_fallback_summary(repo)
    assert "Python" in result["summary"] or "my-tool" in result["summary"].lower()

def test_make_fallback_no_description_no_language():
    repo = {"name": "my-tool", "description": "", "language": None}
    result = make_fallback_summary(repo)
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0
