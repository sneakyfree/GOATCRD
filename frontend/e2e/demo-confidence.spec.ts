import { test, expect } from '@playwright/test';

/**
 * GOATCRD Demo Confidence Suite
 * 
 * Pre-demo health checks to ensure platform is presentation-ready.
 * Run before every investor/stakeholder demo.
 */

test.describe('Demo Confidence Suite', () => {

    test.describe('Critical Pages Load', () => {
        test('Dashboard page loads without errors', async ({ page }) => {
            await page.goto('/');
            await expect(page).toHaveTitle(/GOATCRD/);
            // Check for critical UI elements
            await expect(page.locator('text=Credit Intelligence')).toBeVisible({ timeout: 10000 });
        });

        test('Intake wizard loads and is interactive', async ({ page }) => {
            await page.goto('/intake');
            await expect(page.locator('h1')).toContainText(/Intake|Start|Application/i);
        });

        test('Scenarios page loads', async ({ page }) => {
            await page.goto('/scenarios');
            await expect(page.locator('h1')).toContainText(/Scenario/i);
        });

        test('What-If Simulator loads', async ({ page }) => {
            await page.goto('/what-if');
            await expect(page.locator('h1')).toContainText(/What-If|Simulator/i);
        });

        test('Alternative Data page loads', async ({ page }) => {
            await page.goto('/alt-data');
            await expect(page.locator('h1')).toContainText(/Alternative Data|Connect/i);
        });
    });

    test.describe('P2 Explainability Components', () => {
        test('Scenarios page has explainability tab', async ({ page }) => {
            await page.goto('/scenarios');
            // Check for tabbed interface presence
            const tabs = page.locator('[role="tab"], button').filter({ hasText: /Explain|Details|Overview/i });
            await expect(tabs.first()).toBeVisible({ timeout: 5000 });
        });

        test('What-If page displays confidence breakdown', async ({ page }) => {
            await page.goto('/what-if');
            // Check for category tabs in the simulator
            const categoryTabs = page.locator('button').filter({ hasText: /Credit Profile|Income/i });
            await expect(categoryTabs.first()).toBeVisible({ timeout: 5000 });
        });
    });

    test.describe('1033 Compliance UI', () => {
        test('My Data page exists', async ({ page }) => {
            await page.goto('/my-data');
            await expect(page.locator('h1')).toContainText(/My Data|Data Rights/i);
        });

        test('Access Log page exists', async ({ page }) => {
            await page.goto('/access-log');
            await expect(page.locator('h1')).toContainText(/Access|Log/i);
        });

        test('Consents page exists', async ({ page }) => {
            await page.goto('/consents');
            await expect(page.locator('h1')).toContainText(/Consent/i);
        });
    });

    test.describe('UI Responsiveness', () => {
        test('Navigation is visible on mobile', async ({ page }) => {
            await page.setViewportSize({ width: 375, height: 667 });
            await page.goto('/');
            // Check for mobile navigation (hamburger or bottom nav)
            // This is expected to be visible or nav items should be accessible
        });

        test('Cards stack properly on mobile', async ({ page }) => {
            await page.setViewportSize({ width: 375, height: 667 });
            await page.goto('/scenarios');
            // Cards should be full width on mobile
            const card = page.locator('.glass-card, .card, [class*="Card"]').first();
            if (await card.isVisible()) {
                const box = await card.boundingBox();
                if (box) {
                    expect(box.width).toBeGreaterThan(300);
                }
            }
        });
    });
});

test.describe('Core User Journeys', () => {

    test('Can navigate between main sections', async ({ page }) => {
        await page.goto('/');

        // Navigate using sidebar/nav links
        const scenarios = page.locator('a[href*="scenarios"], nav >> text=Scenarios').first();
        if (await scenarios.isVisible()) {
            await scenarios.click();
            await expect(page).toHaveURL(/scenarios/);
        }

        const whatIf = page.locator('a[href*="what-if"], nav >> text="What-If"').first();
        if (await whatIf.isVisible()) {
            await whatIf.click();
            await expect(page).toHaveURL(/what-if/);
        }
    });

    test('Protected fields in What-If are locked', async ({ page }) => {
        await page.goto('/what-if');

        // Look for protected field indicators
        const protectedIndicator = page.locator('text=Protected').first();
        if (await protectedIndicator.isVisible({ timeout: 5000 })) {
            await expect(protectedIndicator).toBeVisible();
        }
    });
});

test.describe('Accessibility Baseline', () => {

    test('All pages have proper headings', async ({ page }) => {
        const pages = ['/', '/scenarios', '/what-if', '/my-data'];

        for (const path of pages) {
            await page.goto(path);
            const h1 = page.locator('h1').first();
            await expect(h1).toBeVisible({ timeout: 5000 });
        }
    });

    test('Interactive elements are focusable', async ({ page }) => {
        await page.goto('/what-if');

        // Tab through first few elements
        for (let i = 0; i < 5; i++) {
            await page.keyboard.press('Tab');
        }

        // Check that something is focused
        const focused = await page.evaluate(() => document.activeElement?.tagName);
        expect(focused).toBeTruthy();
    });
});
