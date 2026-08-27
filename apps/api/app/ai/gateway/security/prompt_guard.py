"""
IdeaGPT AI Gateway — Prompt & Research Data Isolation Guard.
Enforces strict boundaries separating SYSTEM instructions from UNTRUSTED USER INPUT
and UNTRUSTED RETRIEVED RESEARCH/WEB DATA.
"""

from typing import List, Dict, Any, Optional

class PromptGuard:
    @staticmethod
    def wrap_untrusted_user_input(text: str) -> str:
        """Wraps user input in an explicit untrusted boundary tag."""
        return (
            "--- BEGIN UNTRUSTED USER INPUT ---\n"
            f"{text}\n"
            "--- END UNTRUSTED USER INPUT ---"
        )

    @staticmethod
    def wrap_untrusted_research_data(source_title: str, url: str, content: str) -> str:
        """Wraps external retrieved web content in an untrusted evidence envelope."""
        return (
            f"--- BEGIN UNTRUSTED EXTERNAL EVIDENCE (Source: {source_title} | URL: {url}) ---\n"
            f"{content}\n"
            "--- END UNTRUSTED EXTERNAL EVIDENCE ---"
        )

    @classmethod
    def construct_secure_prompt(
        cls,
        system_instruction: str,
        user_input: str,
        research_sources: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Constructs standard multi-role messages where system instruction is protected
        and untrusted content is strictly encapsulated.
        """
        messages = [
            {"role": "system", "content": system_instruction}
        ]

        body = cls.wrap_untrusted_user_input(user_input)

        if research_sources:
            evidence_blocks = []
            for s in research_sources:
                title = s.get("title", "Web Source")
                url = s.get("url", "https://source.example")
                snippet = s.get("snippet", "")
                evidence_blocks.append(cls.wrap_untrusted_research_data(title, url, snippet))
            body += "\n\n" + "\n\n".join(evidence_blocks)

        messages.append({"role": "user", "content": body})
        return messages
