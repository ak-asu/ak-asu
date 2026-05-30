"""
Entry point for the GitHub Actions profile update workflow.
Run: python scripts/update_profile.py
Env: GITHUB_TOKEN, REPO_OWNER
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ai_summarize import generate_summary, make_fallback_summary
from cache import (
    compute_topics_hash, diff_repos, load_cache,
    make_display_name, save_cache,
)
from github_api import (
    fetch_guestbook_comments, fetch_languages,
    fetch_readme_file, fetch_repos,
)
from readme import update_readme
from render import (
    aggregate_languages, render_current, render_guestbook,
    render_projects, render_techstack,
)

_CACHE_PATH = "profile/projects.json"
_TECH_BASE_PATH = "profile/tech_base.json"
_README_PATH = "README.md"


def main() -> None:
    token = os.environ["GITHUB_TOKEN"]
    owner = os.environ["REPO_OWNER"]

    cache = load_cache(_CACHE_PATH)
    tech_base = json.loads(Path(_TECH_BASE_PATH).read_text(encoding="utf-8"))

    print(f"Fetching public repos for {owner}...")
    all_repos = fetch_repos(owner, token)
    print(f"Found {len(all_repos)} public repos.")

    new_ids, removed_ids = diff_repos(all_repos, cache)
    print(f"New: {len(new_ids)}, Removed: {len(removed_ids)}")

    changed_ids: set[str] = set()
    for repo in all_repos:
        repo_id = str(repo["id"])
        if repo_id in new_ids:
            continue
        cached_repo = cache["repos"].get(repo_id, {})
        needs_retry = cached_repo.get("summary_source") == "fallback"
        if repo.get("pushed_at") != cached_repo.get("pushed_at") or needs_retry:
            changed_ids.add(repo_id)
    print(f"Potentially changed: {len(changed_ids)}")

    repos_by_id = {str(r["id"]): r for r in all_repos}
    for repo_id in new_ids | changed_ids:
        repo = repos_by_id[repo_id]
        name = repo["name"]
        topics = repo.get("topics") or []
        topics_hash = compute_topics_hash(topics)

        readme_data = fetch_readme_file(owner, name, token)
        readme_sha = readme_data["sha"] if readme_data else None
        readme_excerpt = readme_data["content"][:1500] if readme_data else None

        cached_repo = cache["repos"].get(repo_id, {})
        sha_changed = readme_sha != cached_repo.get("readme_sha")
        topics_changed = topics_hash != cached_repo.get("topics_hash")
        is_fallback = cached_repo.get("summary_source") == "fallback"

        languages = fetch_languages(owner, name, token)

        if repo_id in new_ids or sha_changed or topics_changed or is_fallback:
            print(f"  Summarizing: {name}")
            try:
                result = generate_summary(repo, readme_excerpt, token)
                summary_source = "ai"
            except Exception as exc:
                print(f"  WARNING: AI call failed for {name}: {exc}")
                result = make_fallback_summary(repo)
                summary_source = "fallback"

            cache["repos"][repo_id] = {
                "id": repo["id"],
                "name": name,
                "display_name": make_display_name(name),
                "description": repo.get("description") or "",
                "summary": result["summary"],
                "summary_source": summary_source,
                "readme_sha": readme_sha,
                "topics_hash": topics_hash,
                "category": result["category"],
                "tags": result["tags"],
                "languages": languages,
                "topics": topics,
                "stars": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "archived": repo.get("archived", False),
                "is_fork": repo.get("fork", False),
                "pushed_at": repo.get("pushed_at", ""),
                "url": repo.get("html_url", ""),
            }
            save_cache(cache, _CACHE_PATH)
        else:
            cache["repos"][repo_id]["stars"] = repo.get("stargazers_count", 0)
            cache["repos"][repo_id]["pushed_at"] = repo.get("pushed_at", "")
            cache["repos"][repo_id]["languages"] = languages

    for repo_id in removed_ids:
        print(f"  Removing: {cache['repos'][repo_id].get('name', repo_id)}")
        del cache["repos"][repo_id]
    save_cache(cache, _CACHE_PATH)

    all_langs = aggregate_languages(cache["repos"])

    guestbook_comments = fetch_guestbook_comments(
        cache.get("guestbook_discussion_number"), token, owner
    )

    sections = {
        "PROJECTS": render_projects(cache["repos"]),
        "CURRENT": render_current(cache["repos"], all_repos),
        "TECHSTACK": render_techstack(all_langs, tech_base),
        "GUESTBOOK": render_guestbook(
            guestbook_comments,
            cache.get("guestbook_discussion_number"),
            owner,
        ),
    }

    changed = update_readme(_README_PATH, sections)
    if changed:
        print("README updated.")
    else:
        print("No changes to README.")


if __name__ == "__main__":
    main()
