"""Extract fenced code blocks by language from model outputs."""
import re
from typing import Dict, List

FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)
LANGUAGE_ALIASES = {
    "py": "python", "python": "python", "python3": "python",
    "sh": "bash", "bash": "bash", "shell": "bash",
    "js": "javascript", "javascript": "javascript",
    "ts": "typescript", "typescript": "typescript",
}

def extract_blocks_by_language(markdown_text: str) -> Dict[str, List[str]]:
    grouped = {}
    for raw_lang, code in FENCE_RE.findall(markdown_text or ""):
        norm_lang = LANGUAGE_ALIASES.get(raw_lang.strip().lower(), "other")
        grouped.setdefault(norm_lang, []).append(code)
    return grouped
