"""
Evidence Taxonomy, Research Pipeline, Embedding, and Moderation Tests for IdeaGPT AI Gateway v1.
"""

import pytest
from app.ai.gateway.models import EvidenceItem, Citation, ResearchResult
from app.ai.gateway.contracts import EvidenceType
from app.ai.gateway.evidence.taxonomy import EvidenceValidator
from app.ai.gateway.evidence.pipeline import EvidenceAwareResearchPipeline
from app.ai.gateway.embeddings.service import EmbeddingService, cosine_similarity
from app.ai.gateway.moderation.service import ModerationService


def test_evidence_validator_item_rules():
    """Verify validation rules per evidence type."""
    # FACT without source is invalid
    invalid_fact = EvidenceItem(
        evidence_type=EvidenceType.FACT,
        claim="Market size is $10B",
        source_url=None,
        source_title=None
    )
    assert EvidenceValidator.validate_item(invalid_fact) is False

    # FACT with source is valid
    valid_fact = EvidenceItem(
        evidence_type=EvidenceType.FACT,
        claim="Market size is $10B",
        source_url="https://gartner.com/report",
        source_title="Gartner 2026 Report"
    )
    assert EvidenceValidator.validate_item(valid_fact) is True

    # ESTIMATE without assumptions is invalid
    invalid_estimate = EvidenceItem(
        evidence_type=EvidenceType.ESTIMATE,
        claim="Revenue will reach $5M in year 2",
        assumptions=None
    )
    assert EvidenceValidator.validate_item(invalid_estimate) is False

    # ESTIMATE with assumptions is valid
    valid_estimate = EvidenceItem(
        evidence_type=EvidenceType.ESTIMATE,
        claim="Revenue will reach $5M in year 2",
        assumptions="Assuming 1,000 customers at $5k ACV"
    )
    assert EvidenceValidator.validate_item(valid_estimate) is True


def test_sanitize_evidence_list_downgrades_unsubstantiated_facts():
    """Verify raw LLM factual claims without sources are downgraded to INFERENCE."""
    raw_list = [
        {
            "evidence_type": "FACT",
            "claim": "AI SaaS conversion rate is 4.2%",
            "source_url": "",
            "source_title": ""
        },
        {
            "evidence_type": "FACT",
            "claim": "Global SaaS market is $300B",
            "source_url": "https://statista.com/saas",
            "source_title": "Statista 2026"
        }
    ]

    sanitized = EvidenceValidator.sanitize_evidence_list(raw_list)
    assert len(sanitized) == 2
    # First item must be downgraded to INFERENCE
    assert sanitized[0].evidence_type == EvidenceType.INFERENCE
    # Second item remains FACT
    assert sanitized[1].evidence_type == EvidenceType.FACT
    assert sanitized[1].source_url == "https://statista.com/saas"


def test_format_evidence_prompt_context():
    """Verify research evidence formatting generates safe reference context."""
    res = ResearchResult(
        query="Competitor analysis for B2B CRM",
        sources=[
            Citation(title="CRM Leader", url="https://crm.example.com", snippet="Leading platform for sales teams.")
        ]
    )
    context_str = EvidenceAwareResearchPipeline.format_evidence_prompt_context(res)
    assert "EXTERNAL VERIFIED SOURCES" in context_str
    # Verify the exact source URL appears as a discrete reference line,
    # not as a substring of a larger URL (CWE-20 / CodeQL: incomplete URL sanitization).
    expected_url = "https://crm.example.com"
    context_lines = context_str.splitlines()
    assert any(
        line.strip() == expected_url or line.strip().endswith(expected_url)
        for line in context_lines
    ), f"Expected exact URL reference '{expected_url}' in evidence context"


def test_cosine_similarity():
    """Verify vector similarity calculation."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]

    assert pytest.approx(cosine_similarity(vec1, vec2), 0.001) == 1.0
    assert pytest.approx(cosine_similarity(vec1, vec3), 0.001) == 0.0


def test_moderation_service_checks():
    """Verify moderation safety boundary catches prohibited terms."""
    safe_res = ModerationService.check_text("A scalable AI platform for idea evaluation.")
    assert safe_res["flagged"] is False

    unsafe_res = ModerationService.check_text("How to create a ransomware attack.")
    assert unsafe_res["flagged"] is True
    assert "ransomware attack" in unsafe_res["categories"]
