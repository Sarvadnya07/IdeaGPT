import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { UnitEconomicsCalculator } from "../components/decision/UnitEconomicsCalculator";
import { InvestorRedFlags } from "../components/decision/InvestorRedFlags";
import { RegulatoryRadar } from "../components/decision/RegulatoryRadar";
import { MoatAssessor } from "../components/decision/MoatAssessor";
import { VentureMatrix2D } from "../components/decision/VentureMatrix2D";
import { TamSamSomVisualizer } from "../components/decision/TamSamSomVisualizer";
import { ElevatorPitchVariants } from "../components/decision/ElevatorPitchVariants";
import { MermaidViewer } from "../components/execution/MermaidViewer";
import { CloudCostEstimator } from "../components/execution/CloudCostEstimator";
import { CriticalPathVisualizer } from "../components/execution/CriticalPathVisualizer";
import { AICreditTokenGauge } from "../components/ops/AICreditTokenGauge";
import { ProviderPerformanceTelemetry } from "../components/ops/ProviderPerformanceTelemetry";
import { ReportVersionDiff } from "../components/reports/ReportVersionDiff";

describe("IdeaGPT — 30 Feature Workspace Components", () => {
  it("renders Unit Economics Calculator correctly", () => {
    render(<UnitEconomicsCalculator />);
    expect(screen.getByText(/Unit Economics & Cash Flow Calculator/i)).toBeDefined();
    expect(screen.getByText(/LTV \/ CAC Ratio/i)).toBeDefined();
    expect(screen.getByText(/Gross Margin/i)).toBeDefined();
  });

  it("renders Investor Red-Flag Scanner correctly", () => {
    render(<InvestorRedFlags />);
    expect(screen.getByText(/Investor Red-Flag Scanner/i)).toBeDefined();
    expect(screen.getByText(/Statutory Compliance Barrier/i)).toBeDefined();
  });

  it("renders Regulatory & Compliance Radar correctly", () => {
    render(<RegulatoryRadar />);
    expect(screen.getByText(/Regulatory & Compliance Radar/i)).toBeDefined();
    expect(screen.getByText(/GDPR \(General Data Protection Regulation\)/i)).toBeDefined();
  });

  it("renders Defensibility & Moat Assessor correctly", () => {
    render(<MoatAssessor />);
    expect(screen.getByText(/Defensibility & Moat Assessor/i)).toBeDefined();
    expect(screen.getByText(/Switching Costs & Workflow Lock-in/i)).toBeDefined();
  });

  it("renders 2D Venture Matrix correctly", () => {
    render(<VentureMatrix2D />);
    expect(screen.getByText(/2D Venture Matrix/i)).toBeDefined();
    expect(screen.getByText(/IdeaGPT Platform/i)).toBeDefined();
  });

  it("renders TAM / SAM / SOM Visualizer correctly", () => {
    render(<TamSamSomVisualizer />);
    expect(screen.getByText(/TAM \/ SAM \/ SOM Market Sizing/i)).toBeDefined();
    expect(screen.getByText(/Total Addressable \(TAM\)/i)).toBeDefined();
  });

  it("renders Elevator Pitch Variants correctly", () => {
    render(<ElevatorPitchVariants />);
    expect(screen.getByText(/Elevator Pitch Variants/i)).toBeDefined();
    expect(screen.getByText(/10-Word Teaser/i)).toBeDefined();
  });

  it("renders Live Mermaid Viewer correctly", () => {
    render(<MermaidViewer chart="graph TD; A-->B;" title="Test Diagram" />);
    expect(screen.getByText(/Test Diagram/i)).toBeDefined();
    expect(screen.getByText(/Live Mermaid/i)).toBeDefined();
  });

  it("renders Cloud Cost Estimator correctly", () => {
    render(<CloudCostEstimator />);
    expect(screen.getByText(/Cloud Infrastructure Cost Estimator/i)).toBeDefined();
    expect(screen.getByText(/Vercel \(Pro Edge\)/i)).toBeDefined();
  });

  it("renders Critical Path Visualizer correctly", () => {
    render(<CriticalPathVisualizer />);
    expect(screen.getByText(/Critical Path & Dependency Graph/i)).toBeDefined();
    expect(screen.getByText(/STEP 1/i)).toBeDefined();
  });

  it("renders AI Credit & Token Gauge correctly", () => {
    render(<AICreditTokenGauge />);
    expect(screen.getByText(/AI Credit & Token Gauge/i)).toBeDefined();
    expect(screen.getByText(/Total Tokens/i)).toBeDefined();
  });

  it("renders Provider Performance Telemetry correctly", () => {
    render(<ProviderPerformanceTelemetry />);
    expect(screen.getByText(/AI Provider Latency & Reliability Telemetry/i)).toBeDefined();
    expect(screen.getByText(/Cache Hit-Rate & Latency Reduction/i)).toBeDefined();
  });

  it("renders Report Version Diff correctly", () => {
    render(<ReportVersionDiff />);
    expect(screen.getByText(/Evaluation Version Comparison & Audit Diff/i)).toBeDefined();
    expect(screen.getByText(/Score Progression/i)).toBeDefined();
  });
});
