import { test, expect } from "@playwright/test";

test.describe("Analytics Route Protection & Interface", () => {
  test("unauthenticated access to /analytics redirects to sign-in", async ({
    page,
  }) => {
    await page.goto("/analytics");
    await expect(page).toHaveURL(/.*sign-in.*/);
  });
});
