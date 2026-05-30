# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

This is the `ak-asu/ak-asu` GitHub profile repository. The README is auto-updated daily by a Python script + GitHub Actions workflow that pulls live data from GitHub APIs and rewrites four bounded sections using HTML comment markers.

## Commands

```bash
# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_render.py -v

# Run a single test by name
pytest tests/test_render.py::test_render_card_links_to_repo -v

# Install runtime + dev dependencies
pip install requests pytest

# Run the update script locally (requires env vars)
GITHUB_TOKEN=ghp_... REPO_OWNER=ak-asu python scripts/update_profile.py
```

## Architecture

The update system is split into six focused modules under `scripts/` and orchestrated by `update_profile.py`:

```
scripts/
  lang_map.py       — Static mapping: GitHub language name → shields.io badge params
  cache.py          — Load/save profile/projects.json; diff repo sets; hash topics
  readme.py         — Replace content between <!-- KEY:START --> / <!-- KEY:END --> markers
  github_api.py     — Paginated REST repo fetch, README fetch, languages, Discussions GraphQL
  ai_summarize.py   — GitHub Models API (openai/gpt-4o-mini) → {summary, category, tags}
  render.py         — Pure render functions for all four README sections (no HTTP)
  update_profile.py — main() entry point; orchestrates all modules
```

**Data flow:** `fetch_repos` → diff against `profile/projects.json` cache → for changed/new repos: fetch README + languages → AI summarize → save cache → render all four sections → `update_readme`.

## Key Invariants

**Cache keyed by numeric repo ID** (not name) — survives renames. Cache is saved after every individual AI call, never batched — this lets the workflow survive GitHub Models API rate limits (~150 req/day free tier) across multiple daily runs.

**README sections** are bounded by `<!-- KEY:START -->` / `<!-- KEY:END -->` comment pairs. The four keys are `PROJECTS`, `CURRENT`, `TECHSTACK`, `GUESTBOOK`. `readme.py` only writes the file if content actually changed (SHA diff).

**GitHub README sanitizer strips `style=` attributes** on HTML elements. Cards use `align=`, `hspace=`, `clear=` instead. The `style=` query param in shields.io URLs (`?style=flat-square`) is fine — only inline HTML attributes are stripped.

**Profile repo excluded** — `fetch_repos` filters out the repo whose name matches the owner (`ak-asu/ak-asu`).

## Data Files

- `profile/projects.json` — Cache keyed by string repo ID. Fields: `summary`, `category`, `tags`, `readme_sha`, `topics_hash`, `languages`, `pushed_at`. Edit `readme_sha` to force re-summarization of a specific repo.
- `profile/tech_base.json` — Hardcoded tech groups shown in TECHSTACK section. Script reads this; never writes it. Edit directly to add skills not detectable from public repos.

## Workflows

- `update_profile.yml` — Runs at 2am UTC daily (offset from `stats.yml` at 3am to avoid commit conflicts). Requires `models: read` and `discussions: read` permissions. Commits with `[skip ci]` to prevent re-triggering.
- `stats.yml` — Generates `profile/stats.svg` and `profile/top-langs.svg` via github-readme-stats.
- `ci.yml` — Runs `pytest tests/ -v` on every push/PR to main.

## Guestbook

The guestbook pulls comments from GitHub Discussions via GraphQL. The discussion number is stored in `profile/projects.json` under `guestbook_discussion_number` (currently `4`). If `null`, the section shows a setup prompt instead of comments.
