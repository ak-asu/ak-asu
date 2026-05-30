import base64
import re
from html import escape

import requests

_GH_API = "https://api.github.com"

_GUESTBOOK_QUERY = """
query GuestbookComments($owner: String!, $number: Int!) {
  repository(owner: $owner, name: $owner) {
    discussion(number: $number) {
      comments(last: 5) {
        nodes {
          body
          author { login }
          createdAt
        }
      }
    }
  }
}
"""


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_repos(owner: str, token: str) -> list[dict]:
    """Return all public repos for owner, excluding the profile repo."""
    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"{_GH_API}/users/{owner}/repos",
            headers=_headers(token),
            params={"type": "public", "per_page": 100, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        repos.extend(r for r in batch if r["name"] != owner)
        if len(batch) < 100:
            break
        page += 1
    return repos


def fetch_readme_file(owner: str, repo_name: str, token: str) -> dict | None:
    """Return {content: str, sha: str} or None if the repo has no README."""
    resp = requests.get(
        f"{_GH_API}/repos/{owner}/{repo_name}/readme",
        headers=_headers(token),
        timeout=30,
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return {"content": content, "sha": data["sha"]}


def fetch_languages(owner: str, repo_name: str, token: str) -> dict:
    """Return {language: byte_count} for a repo."""
    resp = requests.get(
        f"{_GH_API}/repos/{owner}/{repo_name}/languages",
        headers=_headers(token),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _sanitize_comment(body: str) -> str:
    """Strip markdown/HTML, collapse whitespace, escape HTML, truncate to 120 chars."""
    text = re.sub(r"[*_`#>~\[\]()!]", "", body)
    text = re.sub(r"<[^>]+>", "", text)
    text = " ".join(text.split())
    text = escape(text)
    if len(text) > 120:
        text = text[:117] + "…"
    return text


def fetch_guestbook_comments(
    discussion_number: int | None, token: str, owner: str
) -> list[dict]:
    """Return list of {body, login, createdAt} dicts. Returns [] on any failure."""
    if discussion_number is None:
        return []
    try:
        resp = requests.post(
            f"{_GH_API}/graphql",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "query": _GUESTBOOK_QUERY,
                "variables": {"owner": owner, "number": int(discussion_number)},
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            return []
        nodes = data["data"]["repository"]["discussion"]["comments"]["nodes"]
        return [
            {
                "body": _sanitize_comment(n["body"]),
                "login": n["author"]["login"] if n["author"] else "ghost",
                "createdAt": n["createdAt"],
            }
            for n in nodes
        ]
    except Exception:
        return []
