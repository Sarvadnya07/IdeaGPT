import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { EvidenceBadge } from "../components/research/EvidenceBadge";
import { ConfidenceIndicator } from "../components/research/ConfidenceIndicator";
import { CitationsDrawer } from "../components/research/CitationsDrawer";
import { ResearchStatusBanner } from "../components/research/ResearchStatusBanner";

describe("Phase B — Frontend Research & Evidence Components", () => {
  it("renders EvidenceBadge correctly for FACT, ESTIMATE, INFERENCE, UNKNOWN", () => {
    const { rerender } = render(<EvidenceBadge type="FACT" />);
    expect(screen.getByText(/FACT \(VERIFIED\)/i)).toBeDefined();

    rerender(<EvidenceBadge type="ESTIMATE" />);
    expect(screen.getByText(/ESTIMATE/i)).toBeDefined();

    rerender(<EvidenceBadge type="INFERENCE" />);
    expect(screen.getByText(/INFERENCE/i)).toBeDefined();

    rerender(<EvidenceBadge type="UNKNOWN" />);
    expect(screen.getByText(/UNKNOWN \/ UNRESOLVED/i)).toBeDefined();
  });

  it("renders ConfidenceIndicator with High, Medium, Low states", () => {
    const { rerender } = render(<ConfidenceIndicator level="HIGH" />);
    expect(screen.getByText(/High Confidence/i)).toBeDefined();

    rerender(<ConfidenceIndicator level="LOW" />);
    expect(screen.getByText(/Low Confidence/i)).toBeDefined();

    rerender(<ConfidenceIndicator level="MEDIUM" />);
    expect(screen.getByText(/Medium Confidence/i)).toBeDefined();
  });

  it("renders CitationsDrawer and expandable sources", () => {
    const mockCitations = [
      {
        id: "cite-1",
        citation_id: "[1]",
        title: "Gartner 2025 Market Guide",
        url: "https://gartner.com/report",
        domain: "gartner.com",
        snippet: "Global software security market overview",
        is_authoritative: true,
      },
    ];

    render(<CitationsDrawer citations={mockCitations} />);
    expect(
      screen.getByText(/Verified Sources & Citations \(1\)/i),
    ).toBeDefined();
  });

  it("renders ResearchStatusBanner for active and fallback states", () => {
    const { rerender } = render(<ResearchStatusBanner status="RESEARCHING" />);
    expect(screen.getByText(/Conducting Deep Web Research/i)).toBeDefined();

    rerender(<ResearchStatusBanner status="RESEARCH_UNAVAILABLE" />);
    expect(screen.getByText(/Research Provider Offline/i)).toBeDefined();

    rerender(<ResearchStatusBanner status="COMPLETED" sourceCount={4} />);
    expect(
      screen.getByText(/Evidence-Grounded Analysis Active/i),
    ).toBeDefined();
    expect(screen.getByText(/4 Verified Sources Cited/i)).toBeDefined();
  });
});
