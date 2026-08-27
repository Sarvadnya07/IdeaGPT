"""
IdeaGPT AI Gateway v1 — Core Capability Contracts and Enums.
Defines provider-agnostic interfaces for all in-scope capabilities:
Text Generation, Deep Reasoning, Structured Output, Web Research,
Vision/Document Analysis, Embeddings, and Moderation.
"""

from enum import Enum
from typing import Protocol, runtime_checkable, Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AICapability(str, Enum):
    TEXT_GENERATION = "TEXT_GENERATION"
    REASONING = "REASONING"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"
    WEB_RESEARCH = "WEB_RESEARCH"
    VISION = "VISION"
    DOCUMENT_UNDERSTANDING = "DOCUMENT_UNDERSTANDING"
    EMBEDDING = "EMBEDDING"
    MODERATION = "MODERATION"


class ModelCategory(str, Enum):
    CHAT = "CHAT"
    REASONING = "REASONING"
    RESEARCH = "RESEARCH"
    VISION = "VISION"
    EMBEDDING = "EMBEDDING"
    MODERATION = "MODERATION"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"


class CapabilityConfidence(str, Enum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class ModelStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PREVIEW = "PREVIEW"
    DEPRECATED = "DEPRECATED"
    UNAVAILABLE = "UNAVAILABLE"


class ProviderState(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    UNAVAILABLE = "UNAVAILABLE"
    BYOK_CONNECTED = "BYOK_CONNECTED"
    DEGRADED = "DEGRADED"
    DISABLED = "DISABLED"


class EvidenceType(str, Enum):
    FACT = "FACT"
    ESTIMATE = "ESTIMATE"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Capability Protocols (Interfaces)
# ---------------------------------------------------------------------------

@runtime_checkable
class TextGenerationCapability(Protocol):
    async def generate_text(self, request: Any) -> Any:
        ...


@runtime_checkable
class ReasoningCapability(Protocol):
    async def generate_reasoning(self, request: Any) -> Any:
        ...


@runtime_checkable
class StructuredOutputCapability(Protocol):
    async def generate_structured(self, request: Any) -> Any:
        ...


@runtime_checkable
class ResearchCapability(Protocol):
    async def search_and_collect(self, request: Any) -> Any:
        ...


@runtime_checkable
class VisionCapability(Protocol):
    async def analyze_visual(self, request: Any) -> Any:
        ...


@runtime_checkable
class DocumentCapability(Protocol):
    async def analyze_document(self, request: Any) -> Any:
        ...


@runtime_checkable
class EmbeddingCapability(Protocol):
    async def generate_embeddings(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        ...


@runtime_checkable
class ModerationCapability(Protocol):
    async def check_moderation(self, content: str) -> Dict[str, Any]:
        ...
