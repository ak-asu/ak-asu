from datetime import datetime
from lang_map import get_badge_key, make_badge_url, TECH_BADGE_MAP, LANG_TO_GROUP

_CATEGORY_ORDER = ["ai-ml", "web", "tools", "data", "mobile", "other"]
_CATEGORY_META = {
    "ai-ml":  {"emoji": "🤖", "label": "AI / ML & Research"},
    "web":    {"emoji": "🌐", "label": "Web & Full-Stack"},
    "tools":  {"emoji": "🛠️", "label": "Tools & Utilities"},
    "data":   {"emoji": "📊", "label": "Data & Analytics"},
    "mobile": {"emoji": "📱", "label": "Mobile & Cross-Platform"},
    "other":  {"emoji": "📦", "label": "Other"},
}


def render_card(repo: dict) -> str:
    name = repo["name"]
    url = repo["url"]
    display = repo["display_name"]
    summary = repo.get("summary", "")
    archived = repo.get("archived", False)
    languages = repo.get("languages", {})
    tags = repo.get("tags", [])

    icon_url = (
        f"https://api.dicebear.com/9.x/identicon/svg"
        f"?seed={name}&size=48&backgroundColor=b6e3f4"
    )
    archived_badge = "&nbsp;<sup>archived</sup>" if archived else ""

    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    badge_imgs = []
    for lang, _ in sorted_langs:
        key = get_badge_key(lang)
        if key:
            badge_url = make_badge_url(key, style="flat-square")
            if badge_url:
                badge_imgs.append(f'<img src="{badge_url}"/>')
        if len(badge_imgs) == 3:
            break

    tags_html = " ".join(f"<code>{t}</code>" for t in tags[:4])
    badges_html = "&nbsp;".join(badge_imgs)
    footer = " &nbsp; ".join(filter(None, [badges_html, tags_html]))

    lines = [
        f'<a href="{url}">',
        f'  <img src="{icon_url}" width="48" height="48" align="left" hspace="10"/>',
        f'</a>',
        f'<h4><a href="{url}">{display}</a>{archived_badge}</h4>',
        f'<p>{summary}</p>',
    ]
    if footer:
        lines.append(f'<p>{footer}</p>')
    lines.append('<br clear="left"/>')
    return "\n".join(lines)


def render_projects(repos: dict) -> str:
    by_cat: dict[str, list] = {slug: [] for slug in _CATEGORY_ORDER}
    for repo in repos.values():
        cat = repo.get("category", "other")
        if cat not in by_cat:
            cat = "other"
        by_cat[cat].append(repo)

    for cat in by_cat:
        by_cat[cat].sort(key=lambda r: (-r.get("stars", 0), r.get("pushed_at", "")))

    parts = []
    for slug in _CATEGORY_ORDER:
        cat_repos = by_cat[slug]
        if not cat_repos:
            continue
        meta = _CATEGORY_META[slug]
        n = len(cat_repos)
        label = f'{n} project{"s" if n != 1 else ""}'
        parts.append(f'\n### <a name="{slug}"></a>{meta["emoji"]} {meta["label"]}')
        parts.append(f'<details open>\n<summary><b>{label}</b></summary>\n<br/>\n<table>')
        for i in range(0, n, 2):
            parts.append("  <tr>")
            parts.append(f'    <td width="50%" valign="top">\n{render_card(cat_repos[i])}\n    </td>')
            if i + 1 < n:
                parts.append(f'    <td width="50%" valign="top">\n{render_card(cat_repos[i + 1])}\n    </td>')
            else:
                parts.append('    <td width="50%"></td>')
            parts.append("  </tr>")
        parts.append("</table>\n</details>\n")
    return "\n".join(parts)


def render_current(repos_cache: dict, all_repos: list) -> str:
    sorted_repos = sorted(all_repos, key=lambda r: r.get("pushed_at", ""), reverse=True)[:4]
    lines = ["### 🔭 Working On"]
    for repo in sorted_repos:
        repo_id = str(repo["id"])
        cached = repos_cache.get(repo_id, {})
        summary = cached.get("summary") or repo.get("description") or "A project by ak-asu."
        display = cached.get("display_name") or repo["name"].replace("-", " ").replace("_", " ").title()
        url = repo["html_url"]
        lines.append(f"- **[{display}]({url})** — {summary}")
    return "\n".join(lines)


def aggregate_languages(repos_cache: dict) -> dict:
    """Sum language bytes across all repos."""
    totals: dict[str, int] = {}
    for repo in repos_cache.values():
        for lang, count in repo.get("languages", {}).items():
            totals[lang] = totals.get(lang, 0) + count
    return totals


def render_techstack(aggregated_langs: dict, tech_base: dict) -> str:
    detected_by_group: dict[str, list[str]] = {g: [] for g in tech_base}
    for lang, _ in sorted(aggregated_langs.items(), key=lambda x: x[1], reverse=True):
        key = get_badge_key(lang)
        if not key:
            continue
        group = LANG_TO_GROUP.get(key)
        if group and group in detected_by_group and key not in detected_by_group[group]:
            detected_by_group[group].append(key)

    top_langs = []
    for lang, _ in sorted(aggregated_langs.items(), key=lambda x: x[1], reverse=True):
        key = get_badge_key(lang)
        if key:
            top_langs.append(f"**{key}**")
        if len(top_langs) == 3:
            break

    parts = []
    if top_langs:
        parts.append(f"> Most used: {' · '.join(top_langs)}\n")

    for group, base_items in tech_base.items():
        detected = detected_by_group.get(group, [])
        all_items = list(dict.fromkeys(detected + base_items))
        badges = []
        for item in all_items:
            url = make_badge_url(item, style="for-the-badge")
            if url:
                badges.append(f"![{item}]({url})")
            else:
                encoded = item.replace(" ", "%20").replace("-", "--")
                badges.append(f"![{item}](https://img.shields.io/badge/{encoded}-555555?style=for-the-badge)")
        parts.append(f'<details open>\n<summary><b>{group}</b></summary>\n<br/>\n\n{" ".join(badges)}\n\n</details>\n')

    return "\n".join(parts)


def render_guestbook(comments: list, discussion_number: int | None, owner: str) -> str:
    if discussion_number is None:
        return (
            "## 💬 Guestbook\n\n"
            "👋 Enable Discussions on this repo and create a \"Guestbook 👋\" discussion to get started!"
        )

    disc_url = f"https://github.com/{owner}/{owner}/discussions/{discussion_number}"

    if not comments:
        return (
            "## 💬 Guestbook\n\n"
            f"👋 [Be the first to leave a note!]({disc_url})"
        )

    lines = ["## 💬 Guestbook\n"]
    for c in comments:
        month = datetime.fromisoformat(c["createdAt"].replace("Z", "+00:00")).strftime("%b %Y")
        lines.append(f'> "{c["body"]}" — **@{c["login"]}** · {month}')
    lines.append(f'\n👋 [Leave a note]({disc_url}) — I\'d love to hear from you!')
    return "\n".join(lines)
