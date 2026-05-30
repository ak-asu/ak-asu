import hashlib
import re
from pathlib import Path


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def replace_section(content: str, key: str, new_content: str) -> str:
    """Replace everything between <!-- KEY:START --> and <!-- KEY:END -->."""
    pattern = re.compile(
        rf"<!-- {re.escape(key)}:START -->.*?<!-- {re.escape(key)}:END -->",
        re.DOTALL,
    )
    replacement = f"<!-- {key}:START -->\n{new_content}\n<!-- {key}:END -->"
    return pattern.sub(replacement, content)


def update_readme(path: str, sections: dict[str, str]) -> bool:
    """Replace each section marker pair. Returns True if the file changed."""
    content = Path(path).read_text(encoding="utf-8")
    original_sha = _sha(content)
    for key, new_content in sections.items():
        content = replace_section(content, key, new_content)
    if _sha(content) == original_sha:
        return False
    Path(path).write_text(content, encoding="utf-8")
    return True
