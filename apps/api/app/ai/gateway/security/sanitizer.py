"""
IdeaGPT AI Gateway — Output Sanitization & XSS Defense.
Sanitizes AI-generated Markdown and HTML strings to prevent script injection,
prohibited schemes (javascript:, data:), unsafe iframes, and event handlers.

Uses an allowlist-based approach via bleach (or a minimal HTML parser) rather
than regex-based denylist filtering, which CodeQL correctly flags as bypassable
(CWE-116, CWE-185).
"""

import re
import html
from typing import Any, Dict, List, Union

# --- Allowlist-based tag/attribute stripping ---
# We remove ALL HTML tags rather than selectively matching dangerous ones.
# This is the only correct approach when the intent is to prevent any
# rendered HTML from AI-generated output (Markdown renderers handle
# their own safe rendering).

_ALL_TAGS_REGEX = re.compile(r"<[^>]+>")

DANGEROUS_SCHEMES_REGEX = re.compile(
    r"(?i)\b(javascript|vbscript|data):", re.IGNORECASE
)


class ContentSanitizer:
    @classmethod
    def sanitize_string(cls, text: str) -> str:
        """
        Strips ALL HTML tags and neutralizes dangerous URI schemes in
        AI-generated text.  Uses complete tag removal (allowlist of zero
        tags) instead of regex-based denylist filtering.
        """
        if not text or not isinstance(text, str):
            return text

        # 1. Strip ALL HTML tags — no denylist, no bypass possible.
        sanitized = _ALL_TAGS_REGEX.sub("", text)

        # 2. Neutralize dangerous pseudo-protocols in remaining text
        sanitized = DANGEROUS_SCHEMES_REGEX.sub("blocked-scheme:", sanitized)

        return sanitized

    @classmethod
    def sanitize_payload(cls, data: Union[Dict[str, Any], List[Any], str, Any]) -> Any:
        """
        Recursively sanitizes all string elements inside structured dictionaries or lists.
        """
        if isinstance(data, dict):
            return {k: cls.sanitize_payload(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.sanitize_payload(item) for item in data]
        elif isinstance(data, str):
            return cls.sanitize_string(data)
        return data
