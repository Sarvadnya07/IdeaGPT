import { test, expect } from "@playwright/test";

test.describe("Roadmaps Route Protection", () => {
  test("unauthenticated access to /roadmap redirects to sign-in", async ({
    page,
  }) => {
    await page.goto("/roadmap");
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
