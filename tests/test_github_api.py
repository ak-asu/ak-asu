import base64
from unittest.mock import patch, Mock
import pytest
from github_api import (
    fetch_repos, fetch_readme_file, fetch_languages, fetch_guestbook_comments,
)

def _mock_get(pages):
    """Return a side_effect list of mock responses for paginated GET calls."""
    responses = []
    for page_data in pages:
        m = Mock()
        m.status_code = 200
        m.json.return_value = page_data
        m.raise_for_status = Mock()
        responses.append(m)
    return responses

def test_fetch_repos_returns_all_pages():
    page1 = [{"id": i, "name": f"repo{i}"} for i in range(100)]
    page2 = [{"id": i, "name": f"repo{i}"} for i in range(100, 140)]
    with patch("github_api.requests.get") as mock_get:
        mock_get.side_effect = _mock_get([page1, page2])
        result = fetch_repos("owner", "token")
    assert len(result) == 140

def test_fetch_repos_excludes_profile_repo():
    repos = [
        {"id": 1, "name": "owner"},       # profile repo — should be excluded
        {"id": 2, "name": "other-repo"},
    ]
    with patch("github_api.requests.get") as mock_get:
        mock_get.side_effect = _mock_get([repos])
        result = fetch_repos("owner", "token")
    assert len(result) == 1
    assert result[0]["name"] == "other-repo"

def test_fetch_repos_stops_when_page_less_than_100():
    page1 = [{"id": i, "name": f"repo{i}"} for i in range(50)]
    with patch("github_api.requests.get") as mock_get:
        mock_get.side_effect = _mock_get([page1])
        result = fetch_repos("owner", "token")
    assert len(result) == 50
    assert mock_get.call_count == 1

def test_fetch_readme_file_returns_content_and_sha():
    encoded = base64.b64encode(b"# Hello World").decode()
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"content": encoded + "\n", "sha": "abc123"}
    mock_resp.raise_for_status = Mock()
    with patch("github_api.requests.get", return_value=mock_resp):
        result = fetch_readme_file("owner", "repo", "token")
    assert result["sha"] == "abc123"
    assert result["content"] == "# Hello World"

def test_fetch_readme_file_returns_none_for_404():
    mock_resp = Mock()
    mock_resp.status_code = 404
    with patch("github_api.requests.get", return_value=mock_resp):
        result = fetch_readme_file("owner", "repo", "token")
    assert result is None

def test_fetch_languages_returns_dict():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"Python": 10000, "JavaScript": 5000}
    mock_resp.raise_for_status = Mock()
    with patch("github_api.requests.get", return_value=mock_resp):
        result = fetch_languages("owner", "repo", "token")
    assert result == {"Python": 10000, "JavaScript": 5000}

def test_fetch_guestbook_comments_returns_empty_when_number_is_none():
    result = fetch_guestbook_comments(None, "token", "owner")
    assert result == []

def test_fetch_guestbook_comments_returns_sanitized_nodes():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "repository": {
                "discussion": {
                    "comments": {
                        "nodes": [
                            {"body": "Great **profile**!", "author": {"login": "user1"}, "createdAt": "2026-05-01T00:00:00Z"},
                        ]
                    }
                }
            }
        }
    }
    mock_resp.raise_for_status = Mock()
    with patch("github_api.requests.post", return_value=mock_resp):
        result = fetch_guestbook_comments(1, "token", "owner")
    assert len(result) == 1
    assert result[0]["login"] == "user1"
    assert "**" not in result[0]["body"]  # markdown stripped

def test_fetch_guestbook_returns_empty_on_graphql_error():
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"errors": [{"message": "not found"}]}
    mock_resp.raise_for_status = Mock()
    with patch("github_api.requests.post", return_value=mock_resp):
        result = fetch_guestbook_comments(1, "token", "owner")
    assert result == []
