import { test, expect } from "@playwright/test";
import { authenticateAsTestUser, TEST_USER_A } from "./helpers/test-auth";

test.describe("Authentication Boundary & Protected Routes", () => {
  test("unauthenticated user accessing /dashboard is redirected to sign-in", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/sign-in/);
  });

  test("unauthenticated user accessing /settings is redirected to sign-in", async ({
    page,
  }) => {
    await page.goto("/settings");
    await expect(page).toHaveURL(/\/sign-in/);
  });

  test("authenticated test user can access /dashboard without redirection", async ({
    context,
    page,
  }) => {
    // Intercept project API to return empty list for dashboard initial load
    await page.route("**/api/v1/projects/**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [], total: 0 }),
      });
    });

    await authenticateAsTestUser(context, page, TEST_USER_A);
    await page.goto("/dashboard");

    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("h1")).toContainText(/Your Workspace/i);
    await expect(page.locator("text=No projects found")).toBeVisible();
  });

  test("authenticated test user can access /settings without redirection", async ({
    context,
    page,
  }) => {
    await authenticateAsTestUser(context, page, TEST_USER_A);
    await page.goto("/settings");

    await expect(page).toHaveURL("/settings");
    await expect(page.locator("h1")).toContainText(/Settings/i);
  });
});
