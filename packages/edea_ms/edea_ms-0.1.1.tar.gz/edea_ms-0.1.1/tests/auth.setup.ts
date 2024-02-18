import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  // Perform authentication steps. Replace these actions with your own.
  await page.goto('/api/login');
  await page.getByPlaceholder('email address').fill('alice@example.com');
  await page.getByPlaceholder('password').fill('alice');
  await page.getByRole('button', { name: 'Login' }).click();
  
  await page.getByRole('button', { name: 'Grant Access' }).click();
  
  await page.waitForURL('/');
  // Alternatively, you can wait until the page reaches a state where all cookies are set.
  await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();

  // End of authentication steps.

  await page.context().storageState({ path: authFile });
});