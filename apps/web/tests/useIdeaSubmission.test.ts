import { describe, it, expect } from "vitest";
import { normalizeIdeaPayload, IdeaData } from "../hooks/useIdeaSubmission";

describe("Idea Payload Normalization (CQ-01)", () => {
  it("normalizes client-side form data into canonical backend schema structure", () => {
    const inputData: Partial<IdeaData> = {
      title: "AI Co-Founder Platform",
      problem_statement: "Validating technical ideas takes weeks of manual work.",
      solution_description: "Automated feasibility evaluations and architectural blueprints.",
      target_audience: "Startup Founders & Solo Engineers",
      business_model: "Subscription SaaS",
      unique_selling_proposition: "Instant deterministic scoring and AI multi-model analysis",
      technology_stack: "Next.js, FastAPI, PostgreSQL",
      budget: "$20,000",
      timeline: "Q4 2026",
    };

    const normalized = normalizeIdeaPayload(inputData);

    // Canonical fields
    expect(normalized.title).toBe("AI Co-Founder Platform");
    expect(normalized.problem_statement).toBe("Validating technical ideas takes weeks of manual work.");
    expect(normalized.solution_description).toBe("Automated feasibility evaluations and architectural blueprints.");
    expect(normalized.target_users).toBe("Startup Founders & Solo Engineers");
    expect(normalized.business_model).toBe("Subscription SaaS");
    expect(normalized.is_draft).toBe(true);

    // Structured metadata in notes
    expect(normalized.notes).toBeDefined();
    const parsedNotes = JSON.parse(normalized.notes);
    expect(parsedNotes.usp).toBe("Instant deterministic scoring and AI multi-model analysis");
    expect(parsedNotes.tech_stack).toBe("Next.js, FastAPI, PostgreSQL");
    expect(parsedNotes.budget).toBe("$20,000");
    expect(parsedNotes.timeline).toBe("Q4 2026");
  });

  it("provides safe fallback defaults for mandatory schema properties", () => {
    const minimalData: Partial<IdeaData> = {};
    const normalized = normalizeIdeaPayload(minimalData);

    expect(normalized.title).toBe("Untitled Idea");
    expect(normalized.problem_statement).toBe("No problem statement provided.");
    expect(normalized.solution_description).toBe("No solution description provided.");
    expect(normalized.is_draft).toBe(true);
    expect(normalized.notes).toBeNull();
  });
});
