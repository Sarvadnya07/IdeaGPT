import { test, expect } from '@playwright/test';

test.describe('Clerk Authentication & Route Protection', () => {
  test('public landing page is accessible when unauthenticated', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');
  });

  test('/sign-in page loads Clerk sign in interface', async ({ page }) => {
    await page.goto('/sign-in');
    await expect(page.locator('h1')).toContainText(/Sign in/i);
  });

  test('protected dashboard route redirects unauthenticated users to sign-in', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/sign-in/);
    await expect(page.locator('h1')).toContainText(/Sign in/i, { timeout: 15000 });
  });
});
