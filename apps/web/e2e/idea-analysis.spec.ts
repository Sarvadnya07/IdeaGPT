import { test, expect } from '@playwright/test';

test.describe('AI Analysis Route Protection', () => {
  test('unauthenticated access to /ai-analysis redirects to sign-in', async ({ page }) => {
    await page.goto('/ai-analysis');
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
