import { test, expect } from "@playwright/test";

test.describe("Empty States Protection", () => {
  test("unauthenticated access to dashboard empty states is blocked", async ({
    page,
  }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
