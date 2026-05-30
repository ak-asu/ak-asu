import pytest
from lang_map import get_badge_key, make_badge_url, TECH_BADGE_MAP

def test_get_badge_key_known_language():
    assert get_badge_key("Python") == "Python"

def test_get_badge_key_html_maps_to_html5():
    assert get_badge_key("HTML") == "HTML5"

def test_get_badge_key_jupyter_notebook():
    assert get_badge_key("Jupyter Notebook") == "Jupyter"

def test_get_badge_key_filtered_returns_none():
    assert get_badge_key("Makefile") is None
    assert get_badge_key("Dockerfile") is None
    assert get_badge_key("YAML") is None
    assert get_badge_key("Shell") is None

def test_get_badge_key_unknown_returns_none():
    assert get_badge_key("SomeObscureLang") is None

def test_make_badge_url_flat_square():
    url = make_badge_url("Python", style="flat-square")
    assert "img.shields.io/badge" in url
    assert "3776AB" in url
    assert "flat-square" in url
    assert "python" in url

def test_make_badge_url_for_the_badge():
    url = make_badge_url("Docker", style="for-the-badge")
    assert "for-the-badge" in url
    assert "2496ED" in url

def test_make_badge_url_special_label_cpp():
    url = make_badge_url("C++", style="flat-square")
    assert "C%2B%2B" in url

def test_make_badge_url_unknown_key_returns_none():
    assert make_badge_url("NotAKey") is None

def test_tech_badge_map_covers_all_tech_base_items():
    import json
    from pathlib import Path
    tech_base = json.loads(
        (Path(__file__).parent.parent / "profile" / "tech_base.json").read_text()
    )
    missing = []
    for group, items in tech_base.items():
        for item in items:
            if item not in TECH_BADGE_MAP:
                missing.append(item)
    assert missing == [], f"Missing from TECH_BADGE_MAP: {missing}"
