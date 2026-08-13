import { test, expect } from '@playwright/test';

test.describe('IdeaGPT Security Boundary', () => {
  test('unauthenticated access to project analysis path is blocked and redirected', async ({ page }) => {
    const unauthorizedProjectId = '00000000-0000-0000-0000-000000000000';
    await page.goto(`/projects/${unauthorizedProjectId}/analysis`);
    await expect(page).toHaveURL(/\/sign-in/);
  });
});
