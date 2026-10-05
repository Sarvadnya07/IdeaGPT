import { test, expect } from "@playwright/test";
import { authenticateAsTestUser, TEST_USER_A } from "./helpers/test-auth";

test.describe("Evaluation Version Comparison (Stage 4A)", () => {
  test.beforeEach(async ({ context, page }) => {
    await authenticateAsTestUser(context, page, TEST_USER_A);
  });

  test("allows user to select two evaluation runs and inspect delta comparison", async ({
    page,
  }) => {
    const mockProject = {
      id: "proj-cmp-01",
      user_id: 101,
      title: "FinMatrix AI",
      slug: "finmatrix-ai",
      category: "FinTech",
      description: "Automated financial intelligence",
      status: "active",
      visibility: "private",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const mockIdea = {
      id: "idea-cmp-01",
      project_id: "proj-cmp-01",
      title: "FinMatrix AI Core",
      problem_statement: "Manual financial workflows are slow and prone to errors.",
      solution_description: "Automated pipeline for financial statement extraction and modeling.",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    const mockEvaluations = [
      {
        id: "eval-run-v2",
        idea_id: "idea-cmp-01",
        status: "COMPLETED",
        score: 84,
        created_at: "2026-09-02T10:00:00Z",
        completed_at: "2026-09-02T10:01:00Z",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 950,
        result_payload: { score: 84 },
      },
      {
        id: "eval-run-v1",
        idea_id: "idea-cmp-01",
        status: "COMPLETED",
        score: 72,
        created_at: "2026-09-01T10:00:00Z",
        completed_at: "2026-09-01T10:01:00Z",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 1200,
        result_payload: { score: 72 },
      },
    ];

    const mockComparisonResult = {
      idea_id: "idea-cmp-01",
      evaluation_a: {
        id: "eval-run-v1",
        created_at: "2026-09-01T10:00:00Z",
        completed_at: "2026-09-01T10:01:00Z",
        status: "COMPLETED",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 1200,
        token_usage: 1400,
        estimated_cost: 0.002,
        score: 72.0,
      },
      evaluation_b: {
        id: "eval-run-v2",
        created_at: "2026-09-02T10:00:00Z",
        completed_at: "2026-09-02T10:01:00Z",
        status: "COMPLETED",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 950,
        token_usage: 1550,
        estimated_cost: 0.0024,
        score: 84.0,
      },
      overall_score: {
        key: "overall_score",
        label: "Overall Readiness Score",
        value_a: 72.0,
        value_b: 84.0,
        delta: 12.0,
        formatted_delta: "+12.00",
        status: "improved",
        direction: "higher_is_better",
      },
      dimensions: [
        {
          key: "innovation",
          label: "Innovation",
          value_a: 70.0,
          value_b: 85.0,
          delta: 15.0,
          formatted_delta: "+15.00",
          status: "improved",
          direction: "higher_is_better",
        },
        {
          key: "execution_complexity",
          label: "Execution Complexity",
          value_a: 85.0,
          value_b: 65.0,
          delta: -20.0,
          formatted_delta: "-20.00",
          status: "improved",
          direction: "lower_is_better",
        },
      ],
      swot: {
        strengths: {
          added: ["Validated revenue model"],
          removed: [],
          retained: ["Clear problem statement"],
        },
        weaknesses: {
          added: [],
          removed: ["Undefined pricing"],
          retained: [],
        },
      },
      sections: [
        {
          section_key: "architecture_breakdown",
          label: "Technical Architecture",
          present_in_a: true,
          present_in_b: true,
          status: "changed",
          diff_summary: "Migrated to distributed async processing",
        },
      ],
      provenance_comparison: {
        provider_transition: "groq -> groq",
        model_transition: "llama-3.3-70b-versatile -> llama-3.3-70b-versatile",
        duration_ms_delta: -250,
        token_usage_delta: 150,
        estimated_cost_delta: 0.0004,
      },
      summary: "Overall score changed by +12.00 points (72.00 -> 84.00, Improved). Dimensions: 2 improved, 0 declined, 0 unchanged.",
      generated_at: new Date().toISOString(),
    };

    // Route Mocks
    await page.route("**/api/v1/projects**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [mockProject], total: 1 }),
      });
    });

    await page.route("**/api/v1/projects/proj-cmp-01/ideas**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([mockIdea]),
      });
    });

    await page.route("**/api/v1/ideas/idea-cmp-01/evaluations**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockEvaluations),
      });
    });

    await page.route("**/api/v1/evaluations/idea-cmp-01/compare**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockComparisonResult),
      });
    });

    // 1. Navigate to Project Evaluation History
    await page.goto("/projects/finmatrix-ai/history");

    // Verify page loads and displays Timeline History
    await expect(page.getByRole("heading", { name: "Evaluation History", exact: true })).toBeVisible();
    await expect(page.getByTestId("tab-timeline")).toBeVisible();
    await expect(page.getByTestId("tab-compare")).toBeVisible();

    // 2. Click "Compare Runs" tab
    await page.getByTestId("tab-compare").click();
    await expect(page).toHaveURL(/.*tab=compare.*/);

    // 3. Verify comparison view rendered
    await expect(page.getByTestId("evaluation-version-comparison-view")).toBeVisible();
    await expect(page.getByTestId("selector-evaluation-a")).toBeVisible();
    await expect(page.getByTestId("selector-evaluation-b")).toBeVisible();

    // Verify Overall Delta value and accessible semantic badge
    await expect(page.getByTestId("overall-delta-value")).toHaveText("+12.00");
    await expect(page.getByTestId("overall-delta-badge")).toHaveText("[Improved]");

    // Verify Dimension Deltas
    await expect(page.getByTestId("dimension-card-innovation")).toBeVisible();
    await expect(page.getByTestId("dimension-card-execution_complexity")).toBeVisible();

    // Verify SWOT Evolution
    await expect(page.getByText("Validated revenue model")).toBeVisible();
    await expect(page.getByText("RESOLVED", { exact: true })).toBeVisible();
    await expect(page.getByText("Undefined pricing")).toBeVisible();

    // Verify Provenance
    await expect(page.getByText("Execution Provenance (Read-Only Metadata)")).toBeVisible();
  });

  test("unauthenticated access to evaluation history redirects to sign-in", async ({
    browser,
  }) => {
    // Unauthenticated context
    const cleanContext = await browser.newContext();
    const cleanPage = await cleanContext.newPage();
    await cleanPage.goto("/projects/finmatrix-ai/history");
    await expect(cleanPage).toHaveURL(/.*sign-in.*/);
    await cleanContext.close();
  });
});
