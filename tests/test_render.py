import pytest
from render import (
    render_card, render_projects, render_current,
    render_techstack, render_guestbook, aggregate_languages,
)

_REPO = {
    "id": 1, "name": "test-repo", "display_name": "Test Repo",
    "description": "A test repo", "summary": "Does things well and makes life easier for everyone.",
    "readme_sha": "abc", "topics_hash": "def", "category": "tools",
    "tags": ["CLI Tool", "Testing"], "languages": {"Python": 10000, "JavaScript": 5000},
    "topics": ["testing"], "stars": 5, "forks_count": 1,
    "archived": False, "is_fork": False,
    "pushed_at": "2026-05-01T00:00:00Z",
    "url": "https://github.com/ak-asu/test-repo",
}

def test_render_card_links_to_repo():
    html = render_card(_REPO)
    assert "https://github.com/ak-asu/test-repo" in html

def test_render_card_shows_display_name():
    html = render_card(_REPO)
    assert "Test Repo" in html

def test_render_card_has_dicebear_icon():
    html = render_card(_REPO)
    assert "api.dicebear.com" in html
    assert "seed=test-repo" in html

def test_render_card_no_style_attribute():
    html = render_card(_REPO)
    # GitHub README sanitizer strips inline style= attributes on tags.
    # shields.io URLs contain ?style= as a query param — that's fine.
    import re
    assert not re.search(r'\s+style=', html), "Found inline style= attribute on an HTML element"

def test_render_card_has_clear_left():
    html = render_card(_REPO)
    assert 'clear="left"' in html

def test_render_card_archived_shows_badge():
    html = render_card({**_REPO, "archived": True})
    assert "archived" in html

def test_render_card_not_archived_no_badge():
    html = render_card({**_REPO, "archived": False})
    assert "<sup>archived</sup>" not in html

def test_render_card_shows_concept_tags():
    html = render_card(_REPO)
    assert "<code>CLI Tool</code>" in html

def test_render_card_shows_language_badges():
    html = render_card(_REPO)
    assert "img.shields.io" in html

def test_render_projects_groups_by_category():
    repos = {"1": {**_REPO, "category": "tools"}}
    html = render_projects(repos)
    assert "Tools" in html
    assert "Test Repo" in html

def test_render_projects_empty_category_skipped():
    repos = {"1": {**_REPO, "category": "tools"}}
    html = render_projects(repos)
    assert "AI / ML" not in html

def test_render_projects_odd_repos_has_empty_cell():
    repos = {"1": _REPO}  # single repo → odd count
    html = render_projects(repos)
    assert "<td" in html

def test_render_current_lists_top_4(monkeypatch):
    cache = {"1": _REPO}
    all_repos = [
        {"id": 1, "name": "test-repo", "html_url": "https://github.com/ak-asu/test-repo", "pushed_at": "2026-05-01T00:00:00Z", "description": "desc"},
        {"id": 2, "name": "repo2", "html_url": "https://github.com/ak-asu/repo2", "pushed_at": "2026-04-01T00:00:00Z", "description": "desc2"},
    ]
    md = render_current(cache, all_repos)
    assert "test-repo" in md.lower() or "Test Repo" in md

def test_render_current_heading():
    md = render_current({}, [])
    assert "Working On" in md

def test_aggregate_languages_sums_across_repos():
    repos = {
        "1": {"languages": {"Python": 100, "Go": 50}},
        "2": {"languages": {"Python": 200, "Rust": 30}},
    }
    result = aggregate_languages(repos)
    assert result["Python"] == 300
    assert result["Go"] == 50
    assert result["Rust"] == 30

def test_render_techstack_contains_top_languages():
    langs = {"Python": 5000, "JavaScript": 3000, "Go": 1000}
    tech_base = {"Backend": ["Node.js"], "Frontend": [], "Database": [],
                 "Cloud & DevOps": [], "Tools": [], "AI/ML": []}
    md = render_techstack(langs, tech_base)
    assert "Python" in md

def test_render_techstack_includes_hardcoded_items():
    langs = {}
    tech_base = {"Backend": ["Django"], "Frontend": [], "Database": [],
                 "Cloud & DevOps": [], "Tools": [], "AI/ML": []}
    md = render_techstack(langs, tech_base)
    assert "Django" in md

def test_render_guestbook_with_comments():
    comments = [
        {"body": "Great profile!", "login": "someone", "createdAt": "2026-05-01T00:00:00Z"},
    ]
    md = render_guestbook(comments, 1, "ak-asu")
    assert "Great profile!" in md
    assert "@someone" in md
    assert "discussions/1" in md

def test_render_guestbook_no_comments_shows_invite():
    md = render_guestbook([], 1, "ak-asu")
    assert "first" in md.lower() or "leave" in md.lower()

def test_render_guestbook_no_discussion_number():
    md = render_guestbook([], None, "ak-asu")
    assert "Discussions" in md or "enable" in md.lower() or "note" in md.lower()
