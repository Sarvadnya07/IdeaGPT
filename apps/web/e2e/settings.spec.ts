import { test, expect } from '@playwright/test';

test.describe('Settings Route Protection', () => {
  test('unauthenticated access to /settings redirects to sign-in', async ({ page }) => {
    await page.goto('/settings');
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
