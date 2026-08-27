"""
IdeaGPT AI Gateway — Output Sanitization & XSS Defense.
Sanitizes AI-generated Markdown and HTML strings to prevent script injection,
prohibited schemes (javascript:, data:), unsafe iframes, and event handlers.
"""

import re
import html
from typing import Any, Dict, List, Union

DANGEROUS_SCHEMES_REGEX = re.compile(
    r"(?i)\b(javascript|vbscript|data):", re.IGNORECASE
)
SCRIPT_TAG_REGEX = re.compile(
    r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.IGNORECASE
)
EVENT_HANDLER_REGEX = re.compile(
    r"(?i)\s+on[a-z]+\s*=\s*(?:'[^']*'|\"[^\"]*\"|[^\s>]+)", re.IGNORECASE
)
IFRAME_TAG_REGEX = re.compile(
    r"(?i)<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>", re.IGNORECASE
)
EMBED_OBJECT_REGEX = re.compile(
    r"(?i)<(embed|object|applet)\b[^>]*>.*?</\1>", re.IGNORECASE
)


class ContentSanitizer:
    @classmethod
    def sanitize_string(cls, text: str) -> str:
        """
        Strips active executable vectors (scripts, event handlers, unsafe protocols)
        from AI-generated text or Markdown.
        """
        if not text or not isinstance(text, str):
            return text

        # 1. Strip script tags
        sanitized = SCRIPT_TAG_REGEX.sub("", text)

        # 2. Strip iframes and embed/objects
        sanitized = IFRAME_TAG_REGEX.sub("", sanitized)
        sanitized = EMBED_OBJECT_REGEX.sub("", sanitized)

        # 3. Strip event handlers (e.g. onerror=..., onclick=...)
        sanitized = EVENT_HANDLER_REGEX.sub("", sanitized)

        # 4. Neutralize dangerous pseudo-protocols in links
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
