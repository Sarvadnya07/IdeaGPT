"""
IdeaGPT AI Gateway — Source Normalizer, Deduplicator & Trust Classifier.
Sanitizes raw web search results, canonicalizes URLs, extracts trust metadata, and deduplicates sources.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from datetime import datetime, timezone

from app.ai.gateway.evidence.models import NormalizedSource, SourceType


class SourceNormalizer:
    """
    Normalizes web search results into clean, deduplicated, trust-classified NormalizedSource objects.
    """

    # Query params to strip for canonical URL matching
    STRIP_QUERY_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "ref", "fbclid", "gclid", "source", "ref_src", "trk"
    }

    # Domain patterns for source classification
    GOV_PATTERNS = [".gov", ".mil", ".gov.uk", ".gov.in", ".europa.eu"]
    EDU_PATTERNS = [".edu", ".ac.uk", ".edu.in", "arxiv.org", "nature.com", "researchgate.net", "sciencedirect.com"]
    INDUSTRY_DOMAINS = [
        "gartner.com", "statista.com", "forrester.com", "mckinsey.com",
        "bain.com", "bcg.com", "cbinsights.com", "pitchbook.com", "crunchbase.com",
        "grandviewresearch.com", "marketsandmarkets.com", "fortunebusinessinsights.com"
    ]
    NEWS_DOMAINS = [
        "techcrunch.com", "bloomberg.com", "reuters.com", "wsj.com", "ft.com",
        "forbes.com", "cnbc.com", "theverge.com", "venturebeat.com", "wired.com"
    ]
    COMMUNITY_DOMAINS = [
        "reddit.com", "ycombinator.com", "quora.com", "medium.com", "substack.com", "dev.to"
    ]

    @classmethod
    def canonicalize_url(cls, raw_url: str) -> str:
        """
        Cleans tracking params, fragments, and standardizes scheme and host.
        """
        if not raw_url:
            return ""
        try:
            parsed = urlparse(raw_url.strip())
            scheme = (parsed.scheme or "https").lower()
            netloc = parsed.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]

            # Filter query params
            filtered_query = []
            if parsed.query:
                pairs = parse_qsl(parsed.query)
                filtered_query = [
                    (k, v) for k, v in pairs
                    if k.lower() not in cls.STRIP_QUERY_PARAMS and not k.startswith("utm_")
                ]

            clean_query = urlencode(filtered_query)
            path = parsed.path.rstrip("/")

            return urlunparse((scheme, netloc, path, "", clean_query, ""))
        except Exception:
            return raw_url.strip()

    @classmethod
    def extract_domain(cls, url: str) -> str:
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                return netloc[4:]
            return netloc
        except Exception:
            return ""

    @classmethod
    def classify_source_type(cls, url: str, domain: str) -> SourceType:
        d = domain.lower()
        u = url.lower()

        for pat in cls.GOV_PATTERNS:
            if d.endswith(pat):
                return SourceType.GOVERNMENT

        for pat in cls.EDU_PATTERNS:
            if d.endswith(pat) or pat in d:
                return SourceType.ACADEMIC

        for ind in cls.INDUSTRY_DOMAINS:
            if ind in d:
                return SourceType.INDUSTRY

        for news in cls.NEWS_DOMAINS:
            if news in d:
                return SourceType.NEWS

        for comm in cls.COMMUNITY_DOMAINS:
            if comm in d:
                return SourceType.COMMUNITY

        return SourceType.COMPANY if "." in d else SourceType.UNKNOWN

    @classmethod
    def sanitize_snippet(cls, text: str) -> str:
        """Removes script tags and normalizes whitespace."""
        if not text:
            return ""
        clean = re.sub(r"<[^>]+>", " ", text)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def normalize_sources(
        cls,
        raw_sources: List[Dict[str, Any]],
        max_sources: int = 8
    ) -> List[NormalizedSource]:
        """
        Deduplicates and normalizes raw search results into structured NormalizedSource models.
        """
        seen_urls: Set[str] = set()
        normalized_list: List[NormalizedSource] = []

        citation_index = 1
        for item in raw_sources:
            raw_url = item.get("url") or item.get("link") or ""
            canonical_url = cls.canonicalize_url(raw_url)
            if not canonical_url or canonical_url in seen_urls:
                continue

            seen_urls.add(canonical_url)
            domain = cls.extract_domain(canonical_url)
            source_type = cls.classify_source_type(canonical_url, domain)

            title = item.get("title") or domain or "Web Resource"
            snippet = cls.sanitize_snippet(item.get("snippet") or item.get("content") or "")
            score = float(item.get("score") or item.get("relevance") or 0.85)

            source_id = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()[:12]
            citation_label = f"[{citation_index}]"

            is_authoritative = source_type in (SourceType.GOVERNMENT, SourceType.ACADEMIC, SourceType.INDUSTRY)

            normalized_list.append(
                NormalizedSource(
                    id=source_id,
                    citation_id=citation_label,
                    title=title[:200],
                    url=canonical_url,
                    domain=domain,
                    snippet=snippet[:500],
                    content=snippet[:2000],
                    published_at=item.get("published_date") or item.get("published_at"),
                    retrieved_at=datetime.now(timezone.utc),
                    source_type=source_type,
                    relevance_score=min(max(score, 0.0), 1.0),
                    is_authoritative=is_authoritative,
                )
            )
            citation_index += 1

            if len(normalized_list) >= max_sources:
                break

        return normalized_list
