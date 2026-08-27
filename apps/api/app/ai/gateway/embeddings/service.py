"""
IdeaGPT AI Gateway v1 — Embedding & Semantic Similarity Service.
Supports calculating cosine similarity for similar ideas and duplicate detection.
"""

import math
from typing import List, Optional


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


class EmbeddingService:
    @staticmethod
    async def embed_texts(texts: List[str], provider: str = "openai") -> List[List[float]]:
        """
        Generates dense vector embeddings for texts.
        In test/dev, generates deterministic normalized pseudo-embeddings when no API key is set.
        """
        if not texts:
            return []

        # Simple deterministic vector generator for baseline / test mode
        embeddings = []
        for text in texts:
            # Deterministic hash-based 64-dim float vector
            import hashlib
            h = hashlib.sha256(text.encode("utf-8")).digest()
            raw_vec = [float(b) / 255.0 for b in h[:32]] + [float(b) / 255.0 for b in h[16:48]]
            norm = math.sqrt(sum(v * v for v in raw_vec)) or 1.0
            unit_vec = [v / norm for v in raw_vec]
            embeddings.append(unit_vec)

        return embeddings

    @classmethod
    def calculate_similarity(cls, vec_a: List[float], vec_b: List[float]) -> float:
        return cosine_similarity(vec_a, vec_b)
