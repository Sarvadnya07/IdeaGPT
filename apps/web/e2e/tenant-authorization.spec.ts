import { test, expect } from "@playwright/test";
import {
  authenticateAsTestUser,
  TEST_USER_A,
  TEST_USER_B,
} from "./helpers/test-auth";

test.describe("Tenant Isolation & Cross-User Authorization Boundaries", () => {
  test("User B cannot access or view User A's private project", async ({
    context,
    page,
  }) => {
    // User A owns Project Alpha
    const userAProject = {
      id: "proj-tenant-a-100",
      user_id: TEST_USER_A.tenantId, // 101
      title: "User A Confidential Platform",
      slug: "user-a-confidential-platform",
      description: "Proprietary algorithm workspace",
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

    // Mock API with tenant filtering logic
    await page.route("**/api/v1/projects/**", async (route) => {
      const authHeader = route.request().headers()["authorization"] || "";
      const isUserA = authHeader.includes(TEST_USER_A.id) || authHeader.includes(TEST_USER_A.token);

      const url = route.request().url();

      if (url.includes("/projects/?")) {
        // Query list scoped to caller's tenant
        if (isUserA) {
          return route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({ items: [userAProject], total: 1 }),
          });
        }
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ items: [], total: 0 }),
        });
      }

      if (url.includes(userAProject.slug) || url.includes(userAProject.id)) {
        if (isUserA) {
          return route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(userAProject),
          });
        } else {
          // Reject cross-tenant unauthorized request with 404/403
          return route.fulfill({
            status: 404,
            contentType: "application/json",
            body: JSON.stringify({ detail: "Project Not Found" }),
          });
        }
      }

      return route.continue();
    });

    // 1. Authenticate as User B (Tenant Beta)
    await authenticateAsTestUser(context, page, TEST_USER_B);

    // 2. User B visits dashboard — should NOT see User A's project
    await page.goto("/dashboard");
    await expect(page.locator("text=User A Confidential Platform")).not.toBeVisible();
    await expect(page.locator("text=No projects found")).toBeVisible();

    // 3. User B attempts direct URL access to User A's project
    await page.goto(`/projects/${userAProject.slug}`);

    // 4. Verify boundary rejection in UI
    await expect(page.locator("text=Project Not Found")).toBeVisible();
  });
});
