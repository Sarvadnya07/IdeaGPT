import { test, expect } from "@playwright/test";
import { authenticateAsTestUser, TEST_USER_A } from "./helpers/test-auth";

test.describe("Authenticated Project, Idea & Evaluation Workflows", () => {
  test.beforeEach(async ({ context, page }) => {
    await authenticateAsTestUser(context, page, TEST_USER_A);
  });

  test("complete lifecycle: create project -> view project -> clean up project", async ({
    page,
  }) => {
    // In-memory mock store for deterministic browser test
    let projects: any[] = [];

    await page.route("**/api/v1/projects/**", async (route) => {
      const method = route.request().method();
      const url = route.request().url();

      if (method === "GET" && url.includes("/projects/?")) {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ items: projects, total: projects.length }),
        });
      }

      if (method === "POST" && url.endsWith("/projects/")) {
        const payload = route.request().postDataJSON();
        const newProject = {
          id: "proj-101",
          user_id: 101,
          title: payload.title,
          slug: payload.title.toLowerCase().replace(/\s+/g, "-"),
          description: payload.description || "",
          category: payload.category || "B2B SaaS",
          status: "active",
          visibility: "private",
          color: "#4f46e5",
          icon: "folder",
          is_pinned: false,
          is_archived: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        projects.push(newProject);
        return route.fulfill({
          status: 201,
          contentType: "application/json",
          body: JSON.stringify(newProject),
        });
      }

      if (method === "DELETE" && url.includes("/projects/proj-101")) {
        projects = projects.filter((p) => p.id !== "proj-101");
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ message: "Project deleted successfully" }),
        });
      }

      return route.continue();
    });

    // 1. Visit Dashboard with empty project list
    await page.goto("/dashboard");
    await expect(page.locator("h1")).toContainText(/Your Workspace/i);
    await expect(page.locator("text=No projects found")).toBeVisible();

    // 2. Navigate to Create Project page
    await page.click('a[href="/projects/new"]');
    await expect(page).toHaveURL("/projects/new");
    await expect(page.locator("h1")).toContainText(/Create New Project/i);

    // 3. Fill in Project creation form
    await page.fill('input[placeholder*="Nexus"]', "Autonomous Agent Framework");
    await page.fill('textarea[placeholder*="Briefly describe"]', "Scalable multi-agent execution platform");
    await page.click('button:has-text("Initialize Workspace")');

    // 4. Verify redirected back to dashboard with the new project rendered in the UI
    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("text=Autonomous Agent Framework")).toBeVisible();
    await expect(page.locator("text=Scalable multi-agent execution platform")).toBeVisible();

    // 5. Open Project overview page
    await page.click('a:has-text("Open")');
    await expect(page).toHaveURL("/projects/autonomous-agent-framework");
    await expect(page.locator("h1")).toContainText(/Autonomous Agent Framework/i);
    await expect(page.locator("text=Pending Actions")).toBeVisible();

    // 6. Clean up: Delete the project from Danger Zone
    page.on("dialog", (dialog) => dialog.accept());
    await page.click('button:has-text("Delete Project")');

    // 7. Verify redirected to dashboard and project is removed
    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("text=No projects found")).toBeVisible();
  });

  test("idea draft creation and submission workflow", async ({ page }) => {
    const project = {
      id: "proj-202",
      user_id: 101,
      title: "Fintech Risk Engine",
      slug: "fintech-risk-engine",
      description: "Real-time fraud intelligence",
      category: "Fintech",
      status: "active",
      visibility: "private",
      color: "#4f46e5",
      icon: "folder",
      is_pinned: false,
      is_archived: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    let savedIdea: any = null;

    await page.route("**/api/v1/projects/**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [project], total: 1 }),
      });
    });

    await page.route("**/api/v1/ideas/**", async (route) => {
      const method = route.request().method();
      if (method === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(savedIdea ? [savedIdea] : []),
        });
      }
      if (method === "POST" || method === "PUT" || method === "PATCH") {
        const data = route.request().postDataJSON();
        savedIdea = { id: "idea-999", project_id: "proj-202", ...data };
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(savedIdea),
        });
      }
      return route.continue();
    });

    // 1. Navigate directly to Idea submission for the project
    await page.goto("/projects/fintech-risk-engine/idea");
    await expect(page.locator("h1")).toContainText(/Idea Definition/i);

    // 2. Fill in Problem Statement & Solution Description
    await page.fill(
      'textarea[placeholder*="What specific problem"]',
      "High volume of deceptive transactions slipping past traditional rules."
    );
    await page.fill(
      'textarea[placeholder*="How does your product solve"]',
      "Deterministic graph analysis and real-time behavioral risk scoring."
    );

    // 3. Verify auto-save feedback in header
    await expect(page.locator("text=Saving...").or(page.locator("text=Saved just now"))).toBeVisible({ timeout: 5000 });
  });

  test("evaluation execution and lifecycle state transitions in browser", async ({ page }) => {
    const project = {
      id: "proj-303",
      user_id: 101,
      title: "AI Strategy Suite",
      slug: "ai-strategy-suite",
      description: "Automated business validation",
      category: "B2B SaaS",
      status: "active",
      visibility: "private",
      color: "#4f46e5",
      icon: "folder",
      is_pinned: false,
      is_archived: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    let pollCount = 0;

    await page.route("**/api/v1/projects/**", async (route) => {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [project], total: 1 }),
      });
    });

    await page.route("**/api/v1/evaluations/**", async (route) => {
      const url = route.request().url();
      if (url.includes("eval-job-test-303")) {
        pollCount++;
        const currentStatus = pollCount <= 1 ? "processing" : "completed";
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ id: "eval-job-test-303", status: currentStatus, progress: 100 }),
        });
      }
      return route.continue();
    });

    // 1. Visit processing page with test job ID
    await page.goto("/projects/ai-strategy-suite/processing?jobId=eval-job-test-303");

    // 2. Verify state transition UI rendered in DOM
    await expect(
      page.locator("text=Waiting in Queue...").or(page.locator("text=AI is Evaluating Your Idea..."))
    ).toBeVisible();

    // 3. Verify final completion state is reached
    await expect(page.locator("text=Evaluation Complete!")).toBeVisible({ timeout: 10000 });

    // 4. Verify automatic redirection to Analysis dashboard
    await expect(page).toHaveURL(/\/projects\/ai-strategy-suite\/analysis/, { timeout: 10000 });
  });
});
