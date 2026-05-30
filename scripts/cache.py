import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

_EMPTY_CACHE = {
    "last_updated": None,
    "guestbook_discussion_number": None,
    "repos": {},
}


def load_cache(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return dict(_EMPTY_CACHE)
    return json.loads(p.read_text(encoding="utf-8"))


def save_cache(cache: dict, path: str) -> None:
    cache["last_updated"] = datetime.now(timezone.utc).isoformat()
    Path(path).write_text(
        json.dumps(cache, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def diff_repos(current_repos: list[dict], cache: dict) -> tuple[set, set]:
    """Return (new_ids, removed_ids) as sets of string repo IDs."""
    cached_ids = set(cache.get("repos", {}).keys())
    current_ids = {str(r["id"]) for r in current_repos}
    return current_ids - cached_ids, cached_ids - current_ids


def compute_topics_hash(topics: list[str]) -> str:
    sorted_topics = ",".join(sorted(topics))
    return hashlib.sha256(sorted_topics.encode()).hexdigest()


def make_display_name(repo_name: str) -> str:
    return repo_name.replace("-", " ").replace("_", " ").title()
