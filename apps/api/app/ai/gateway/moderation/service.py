"""
IdeaGPT AI Gateway v1 — Moderation & Safety Boundary Service.
Checks prompt inputs and generated outputs against safety guidelines.
"""

from typing import Dict, Any, List

HARMFUL_PATTERNS = [
    "bomb", "weapon", "child exploitation", "credit card dump", "malware injection", "ransomware attack"
]


class ModerationService:
    @staticmethod
    def check_text(text: str) -> Dict[str, Any]:
        """
        Performs fast heuristic / keyword safety boundary check.
        Returns flagged (bool), reason (str|None), categories (List[str]).
        """
        if not text:
            return {"flagged": False, "categories": []}

        lower_t = text.lower()
        matched = []
        for pat in HARMFUL_PATTERNS:
            if pat in lower_t:
                matched.append(pat)

        if matched:
            return {
                "flagged": True,
                "reason": f"Content violates safety guidelines: {', '.join(matched)}",
                "categories": matched,
            }

        return {"flagged": False, "categories": []}
