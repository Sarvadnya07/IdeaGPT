import { test, expect } from '@playwright/test';

test.describe('Project Route Protection', () => {
  test('unauthenticated access to projects route redirects to sign-in', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
