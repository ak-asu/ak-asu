import pytest
from pathlib import Path
from readme import replace_section, update_readme

def test_replace_section_replaces_content():
    content = "before\n<!-- FOO:START -->\nold\n<!-- FOO:END -->\nafter"
    result = replace_section(content, "FOO", "new content")
    assert "new content" in result
    assert "old" not in result
    assert "before" in result
    assert "after" in result

def test_replace_section_markers_preserved():
    content = "<!-- FOO:START -->\nold\n<!-- FOO:END -->"
    result = replace_section(content, "FOO", "new")
    assert "<!-- FOO:START -->" in result
    assert "<!-- FOO:END -->" in result

def test_replace_section_multiline_content():
    content = "<!-- BAR:START -->\nline1\nline2\nline3\n<!-- BAR:END -->"
    result = replace_section(content, "BAR", "single line")
    assert "single line" in result
    assert "line1" not in result

def test_replace_section_no_match_returns_original():
    content = "no markers here"
    result = replace_section(content, "MISSING", "new")
    assert result == content

def test_update_readme_returns_false_when_unchanged(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("<!-- FOO:START -->\ncontent\n<!-- FOO:END -->", encoding="utf-8")
    changed = update_readme(str(readme), {"FOO": "content"})
    assert changed is False

def test_update_readme_returns_true_when_changed(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("<!-- FOO:START -->\nold\n<!-- FOO:END -->", encoding="utf-8")
    changed = update_readme(str(readme), {"FOO": "new"})
    assert changed is True
    assert "new" in readme.read_text(encoding="utf-8")

def test_update_readme_does_not_write_when_unchanged(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("<!-- FOO:START -->\ncontent\n<!-- FOO:END -->", encoding="utf-8")
    mtime_before = readme.stat().st_mtime
    update_readme(str(readme), {"FOO": "content"})
    assert readme.stat().st_mtime == mtime_before

def test_update_readme_handles_multiple_sections(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(
        "<!-- A:START -->\na_old\n<!-- A:END -->\n"
        "<!-- B:START -->\nb_old\n<!-- B:END -->",
        encoding="utf-8",
    )
    update_readme(str(readme), {"A": "a_new", "B": "b_new"})
    text = readme.read_text(encoding="utf-8")
    assert "a_new" in text
    assert "b_new" in text
    assert "a_old" not in text
