import json
import requests

_ENDPOINT = "https://models.github.ai/inference/chat/completions"
_MODEL = "openai/gpt-4o-mini"

_SYSTEM_PROMPT = """\
You are writing project descriptions for a software engineer's GitHub profile.
Audience: technical recruiters scanning quickly.
Tone: human, plain English, no jargon overload. Sound like a person, not a product page.
Lead with what the project does. End with the impact or what makes it interesting.
Target approximately 18 words. Never exceed 25 words.

Category definitions — pick exactly one:
- ai-ml: AI/ML is the core feature: LLMs, chatbots, computer vision, NLP, recommendation engines, generative AI, model training. Even if it has a web frontend, choose ai-ml if AI drives the value.
- web: Web apps or REST APIs where the primary value is the UI or backend service, with no AI/ML core.
- tools: CLI tools, compilers, parsers, dev tools, infrastructure automation, DevOps utilities.
- data: Data pipelines, analytics dashboards, data processing, scientific computing.
- mobile: Android/iOS apps, Flutter apps (Dart), React Native — anything primarily targeting a mobile device.
- other: Games, Arduino/hardware projects, learning exercises, course assignments, miscellaneous.

Return JSON only, no markdown, no explanation:
{"summary": "...", "category": "ai-ml|web|tools|data|mobile|other", "tags": ["Tag1", "Tag2"]}
Tags should be 2-4 concept-level labels like "Machine Learning", "REST API", "CLI Tool".\
"""


def generate_summary(repo: dict, readme_excerpt: str | None, token: str) -> dict:
    """Call GitHub Models API to generate summary, category, and tags for a repo."""
    parts = [
        f"Repo: {repo['name']}",
        f"Description: {repo.get('description') or 'None'}",
        f"Topics: {', '.join(repo.get('topics', [])) or 'None'}",
        f"Primary language: {repo.get('language') or 'Unknown'}",
    ]
    if readme_excerpt:
        parts.append(f"README excerpt (first 1500 chars):\n{readme_excerpt[:1500]}")

    resp = requests.post(
        _ENDPOINT,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "model": _MODEL,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(parts)},
            ],
            "temperature": 0.3,
            "max_tokens": 200,
            "response_format": {"type": "json_object"},
        },
        timeout=30,
    )
    resp.raise_for_status()
    result = json.loads(resp.json()["choices"][0]["message"]["content"])
    if not all(k in result for k in ("summary", "category", "tags")):
        raise ValueError(f"Unexpected AI response structure: {result}")
    return result


def make_fallback_summary(repo: dict) -> dict:
    """Return a best-effort summary without an AI call."""
    desc = repo.get("description") or ""
    lang = repo.get("language") or ""
    name = repo.get("name", "project")
    display = name.replace("-", " ").replace("_", " ").title()

    if desc:
        words = desc.split()
        summary = " ".join(words[:18]) + ("…" if len(words) > 18 else "")
    elif lang:
        summary = f"{display} — a {lang} project by ak-asu."
    else:
        summary = f"{display} — an open-source project by ak-asu."

    return {"summary": summary, "category": "other", "tags": []}
