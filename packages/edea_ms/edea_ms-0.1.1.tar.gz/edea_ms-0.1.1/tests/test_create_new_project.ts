import { test, expect } from '@playwright/test';

test('create a new project with default-group', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Projects' }).click();
    await page.getByRole('button', { name: 'New' }).click();
    await page.getByPlaceholder('Enter internal project designator...').click();
    await page.getByPlaceholder('Enter internal project designator...').fill('T1234');
    await page.getByPlaceholder('Enter internal project designator...').press('Tab');
    await page.getByPlaceholder('Enter name...').fill('Playwright Test Project');
    await page.getByPlaceholder('Enter name...').press('Tab');
    await page.getByLabel('Group Nonedefault-grouptest-groupsecret-group').press('ArrowDown');
    await page.getByLabel('Group Nonedefault-grouptest-groupsecret-group').press('ArrowDown');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.getByRole('gridcell', { name: 'T1234' }).click();

    expect(await page.getByText('No testruns available.'));
});
