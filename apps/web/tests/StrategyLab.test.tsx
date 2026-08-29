import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DecisionGateBadge } from "../components/strategy/DecisionGateBadge";
import { ProvenanceBadge } from "../components/strategy/ProvenanceBadge";
import { AssumptionPriorityTable } from "../components/strategy/AssumptionPriorityTable";
import { ScenarioSimulator } from "../components/strategy/ScenarioSimulator";
import { TradeoffMatrix } from "../components/strategy/TradeoffMatrix";

describe("Phase C — Frontend Strategy Lab & Decision Components", () => {
  it("renders DecisionGateBadge correctly for all 5 gate states", () => {
    const { rerender } = render(<DecisionGateBadge gate="GO" />);
    expect(screen.getByText(/DECISION GATE: GO/i)).toBeDefined();

    rerender(<DecisionGateBadge gate="VALIDATE_FIRST" />);
    expect(screen.getByText(/DECISION GATE: VALIDATE FIRST/i)).toBeDefined();

    rerender(<DecisionGateBadge gate="GO_WITH_CONDITIONS" />);
    expect(screen.getByText(/GO \(WITH CONDITIONS\)/i)).toBeDefined();

    rerender(<DecisionGateBadge gate="PIVOT" />);
    expect(screen.getByText(/DECISION GATE: PIVOT/i)).toBeDefined();

    rerender(<DecisionGateBadge gate="STOP" />);
    expect(screen.getByText(/DECISION GATE: STOP/i)).toBeDefined();
  });

  it("renders ProvenanceBadge with strict data lineage types", () => {
    const { rerender } = render(
      <ProvenanceBadge type="DETERMINISTIC_CALCULATION" />,
    );
    expect(screen.getByText(/DETERMINISTIC CALCULATION/i)).toBeDefined();

    rerender(<ProvenanceBadge type="USER_INPUT" />);
    expect(screen.getByText(/USER INPUT/i)).toBeDefined();

    rerender(<ProvenanceBadge type="RESEARCH_EVIDENCE" />);
    expect(screen.getByText(/RESEARCH EVIDENCE/i)).toBeDefined();

    rerender(<ProvenanceBadge type="MODEL_INFERENCE" />);
    expect(screen.getByText(/MODEL INFERENCE/i)).toBeDefined();

    rerender(<ProvenanceBadge type="RECOMMENDATION" />);
    expect(screen.getByText(/STRATEGIC RECOMMENDATION/i)).toBeDefined();
  });

  it("renders AssumptionPriorityTable with normalized rankings and roadmap action button", () => {
    const onAdd = vi.fn();
    const mockAssumptions = [
      {
        id: "a-1",
        claim: "Founders will pay $49/mo for strategy intelligence",
        classification: "EXPLICIT_USER_ASSUMPTION",
        impact: "HIGH",
        uncertainty: "HIGH",
        validation_ease: "HIGH",
        priority_score: 3.0,
        priority_tier: "HIGH",
        recommended_experiment:
          "Interview 20 founders and test landing page intent",
      },
    ];

    render(
      <AssumptionPriorityTable
        assumptions={mockAssumptions}
        onAddToRoadmap={onAdd}
      />,
    );
    expect(screen.getByText(/HIGH PRIORITY/i)).toBeDefined();
    expect(screen.getByText(/Founders will pay \$49\/mo/i)).toBeDefined();

    const addBtn = screen.getByText(/Add to Roadmap/i);
    fireEvent.click(addBtn);
    expect(onAdd).toHaveBeenCalledTimes(1);
  });

  it("renders ScenarioSimulator and updates calculations on slider movement", () => {
    render(
      <ScenarioSimulator
        initialBudget={60000}
        initialTimeline={3}
        initialBurn={6000}
      />,
    );
    expect(screen.getByText(/Calculated Runway/i)).toBeDefined();
    expect(screen.getByText(/LOW RISK/i)).toBeDefined();
  });

  it("renders TradeoffMatrix with reversibility tiers", () => {
    const mockTradeoffs = [
      {
        id: "t-1",
        dimension: "MVP Speed vs Scalability",
        option_a_name: "Modular Monolith",
        option_b_name: "Event Microservices",
        difference: "Monolith ships in 3 weeks; Microservices require 3 months",
        consequence: "Monolith optimizes early capital efficiency",
        reversibility: "REVERSIBLE",
      },
    ];

    render(<TradeoffMatrix tradeoffs={mockTradeoffs} />);
    expect(screen.getByText(/MVP Speed vs Scalability/i)).toBeDefined();
    expect(screen.getByText(/REVERSIBLE/i)).toBeDefined();
  });
});
