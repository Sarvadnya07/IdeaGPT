import { test, expect } from '@playwright/test';

test.describe('Compare Ideas Route Protection & Interface', () => {
  test('unauthenticated access to /compare redirects to sign-in', async ({ page }) => {
    await page.goto('/compare');
    await expect(page).toHaveURL(/.*sign-in.*/);
  });
});
