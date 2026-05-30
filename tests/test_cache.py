import json
import pytest
from pathlib import Path
from cache import (
    load_cache, save_cache, diff_repos,
    compute_topics_hash, make_display_name,
)

def test_load_cache_returns_default_when_missing(tmp_path):
    result = load_cache(str(tmp_path / "missing.json"))
    assert result == {"last_updated": None, "guestbook_discussion_number": None, "repos": {}}

def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "cache.json")
    cache = {
        "last_updated": "2026-05-29T00:00:00Z",
        "guestbook_discussion_number": 42,
        "repos": {"1": {"name": "test"}},
    }
    save_cache(cache, path)
    loaded = load_cache(path)
    assert loaded == cache

def test_diff_repos_identifies_new():
    cache = {"repos": {"1": {}, "2": {}}}
    current = [{"id": 2}, {"id": 3}]
    new_ids, removed_ids = diff_repos(current, cache)
    assert new_ids == {"3"}

def test_diff_repos_identifies_removed():
    cache = {"repos": {"1": {}, "2": {}}}
    current = [{"id": 2}, {"id": 3}]
    new_ids, removed_ids = diff_repos(current, cache)
    assert removed_ids == {"1"}

def test_diff_repos_empty_cache():
    cache = {"repos": {}}
    current = [{"id": 1}, {"id": 2}]
    new_ids, removed_ids = diff_repos(current, cache)
    assert new_ids == {"1", "2"}
    assert removed_ids == set()

def test_compute_topics_hash_deterministic():
    h = compute_topics_hash(["python", "ml"])
    assert compute_topics_hash(["python", "ml"]) == h

def test_compute_topics_hash_order_independent():
    assert compute_topics_hash(["b", "a"]) == compute_topics_hash(["a", "b"])

def test_compute_topics_hash_empty():
    assert compute_topics_hash([]) == compute_topics_hash([])

def test_make_display_name_hyphens():
    assert make_display_name("my-cool-repo") == "My Cool Repo"

def test_make_display_name_underscores():
    assert make_display_name("my_cool_repo") == "My Cool Repo"

def test_make_display_name_mixed():
    assert make_display_name("my-cool_repo") == "My Cool Repo"
