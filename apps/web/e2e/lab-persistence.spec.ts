import { test, expect } from "@playwright/test";
import { authenticateAsTestUser, TEST_USER_A } from "./helpers/test-auth";

test.describe("AI Lab Artifact Persistence & History Rehydration (V1.1-MUST-01)", () => {
  test.beforeEach(async ({ context, page }) => {
    await authenticateAsTestUser(context, page, TEST_USER_A);
  });

  test("generates investor analysis, navigates away, and restores state on return", async ({
    page,
  }) => {
    const mockProject = {
      id: "proj-lab-101",
      user_id: 101,
      title: "FinMatrix AI",
      slug: "finmatrix-ai",
      category: "FinTech",
      description: "Automated institutional financial modeling",
      status: "active",
      visibility: "private",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    let persistedArtifacts: any[] = [];

    // Mock project list
    await page.route("**/api/v1/projects**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [mockProject], total: 1 }),
      });
    });

    // Mock artifacts listing endpoint
    await page.route("**/api/v1/ai/artifacts**", async (route) => {
      const url = new URL(route.request().url());
      const artType = url.searchParams.get("artifact_type");
      const matched = persistedArtifacts.filter(
        (a) => !artType || a.artifact_type === artType
      );
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(matched),
      });
    });

    // Mock investor lab generation endpoint
    await page.route("**/api/v1/ai/labs/investor", async (route) => {
      const generatedResult = {
        artifact_id: "art-inv-101",
        schema_version: 1,
        valuation_range: {
          pre_money_min_usd: 5000000,
          pre_money_max_usd: 8000000,
          target_raise_usd: 1500000,
          dilution_pct: 18.5,
          methodology: "Scorecard & VC Method",
        },
        investor_scorecard: {
          market_opportunity: 90,
          team_and_execution: 85,
          defensibility_moat: 80,
          unit_economics: 88,
          overall_investability: 86,
        },
        funding_stages: [
          {
            stage: "Seed",
            target_arr: "$500K",
            key_milestones: ["10 enterprise pilots"],
            valuation_benchmark: "$6M Post",
          },
        ],
        cap_table_simulation: [
          {
            stakeholder: "Founders",
            initial_equity_pct: 100,
            post_seed_equity_pct: 81.5,
            post_series_a_pct: 65,
          },
        ],
        risk_matrix: [
          {
            risk_factor: "Compliance onboarding friction",
            severity: "MEDIUM",
            mitigation_strategy: "Automated KYC/AML checks",
          },
        ],
        elevator_pitch: "Next-generation institutional treasury automation",
      };

      // Persist in mock store
      persistedArtifacts = [
        {
          id: "art-inv-101",
          artifact_type: "investor_lab",
          project_id: "proj-lab-101",
          title: "Investor Analysis: FinMatrix AI",
          created_at: new Date().toISOString(),
          content_payload: generatedResult,
        },
      ];

      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(generatedResult),
      });
    });

    // 1. Visit /investor
    await page.goto("/investor");
    await expect(page.getByText("FinMatrix AI").first()).toBeVisible();

    // 2. Click "Generate VC Report"
    const generateBtn = page.getByRole("button", {
      name: /Generate VC Report/i,
    });
    await expect(generateBtn).toBeVisible();
    await generateBtn.click();

    // 3. Verify generated analysis renders
    await expect(
      page.getByText("Next-generation institutional treasury automation")
    ).toBeVisible();
    await expect(page.getByText("$5,000,000")).toBeVisible();

    // 4. Navigate away to /analytics
    await page.goto("/analytics");
    await expect(page).toHaveURL(/.*analytics/);

    // 5. Navigate back to /investor
    await page.goto("/investor");

    // 6. Verify restored badge and rehydrated content
    await expect(
      page.getByText(/Saved Result Restored/i)
    ).toBeVisible({ timeout: 10000 });
    await expect(
      page.getByText("Next-generation institutional treasury automation")
    ).toBeVisible();
    await expect(page.getByText("$5,000,000")).toBeVisible();
  });
});
