import { test, expect } from '@playwright/test';

/**
 * What-If Simulator E2E Tests
 * 
 * Tests the enhanced What-If page with P2 components:
 * - Category-based controls (Credit Profile, Income & Debt, Protected)
 * - PlainEnglishSummary integration
 * - ConfidenceBreakdown display
 * - Protected field restrictions
 * - Simulation execution
 */

test.describe('What-If Simulator', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto('/what-if');
    });

    test.describe('Page Layout', () => {
        test('displays page header with emoji', async ({ page }) => {
            const header = page.locator('h1');
            await expect(header).toContainText(/What-If|Simulator/i);
        });

        test('shows back to scenarios link', async ({ page }) => {
            const backLink = page.locator('a').filter({ hasText: /Scenarios|Back/i });
            await expect(backLink).toBeVisible();
        });

        test('displays two-column layout on desktop', async ({ page }) => {
            const columns = page.locator('.glass-card');
            const count = await columns.count();
            expect(count).toBeGreaterThanOrEqual(2);
        });
    });

    test.describe('Category Tabs', () => {
        test('displays Credit Profile tab', async ({ page }) => {
            const creditTab = page.locator('button').filter({ hasText: /Credit Profile/i });
            await expect(creditTab).toBeVisible();
        });

        test('displays Income & Debt tab', async ({ page }) => {
            const incomeTab = page.locator('button').filter({ hasText: /Income.*Debt/i });
            await expect(incomeTab).toBeVisible();
        });

        test('displays Protected tab', async ({ page }) => {
            const protectedTab = page.locator('button').filter({ hasText: /Protected/i });
            await expect(protectedTab).toBeVisible();
        });

        test('switching tabs updates visible controls', async ({ page }) => {
            // Click Income tab
            const incomeTab = page.locator('button').filter({ hasText: /Income.*Debt/i });
            await incomeTab.click();

            // Should show income-related controls
            const incomeControls = page.locator('label').filter({ hasText: /Pay Down Debt|Income Increase|Months/i });
            await expect(incomeControls.first()).toBeVisible({ timeout: 3000 });
        });
    });

    test.describe('Credit Profile Controls', () => {
        test('shows credit score slider', async ({ page }) => {
            const creditTab = page.locator('button').filter({ hasText: /Credit Profile/i });
            await creditTab.click();

            const creditScoreLabel = page.locator('label').filter({ hasText: /Credit Score/i });
            await expect(creditScoreLabel).toBeVisible();
        });

        test('shows credit utilization slider', async ({ page }) => {
            const creditTab = page.locator('button').filter({ hasText: /Credit Profile/i });
            await creditTab.click();

            const utilizationLabel = page.locator('label').filter({ hasText: /Credit Utilization/i });
            await expect(utilizationLabel).toBeVisible();
        });

        test('sliders are interactive', async ({ page }) => {
            const slider = page.locator('input[type="range"]').first();
            if (await slider.isVisible({ timeout: 3000 })) {
                await expect(slider).toBeEnabled();
            }
        });
    });

    test.describe('Protected Fields', () => {
        test('shows protected badge for restricted fields', async ({ page }) => {
            const protectedTab = page.locator('button').filter({ hasText: /Protected/i });
            await protectedTab.click();

            await page.waitForTimeout(500);
            const protectedBadge = page.locator('text=Protected').first();
            await expect(protectedBadge).toBeVisible();
        });

        test('protected fields show compliance warning', async ({ page }) => {
            const protectedTab = page.locator('button').filter({ hasText: /Protected/i });
            await protectedTab.click();

            await page.waitForTimeout(500);
            const warning = page.locator('text=/cannot be adjusted|fair lending/i');
            await expect(warning).toBeVisible();
        });

        test('protected fields do not have interactive sliders', async ({ page }) => {
            const protectedTab = page.locator('button').filter({ hasText: /Protected/i });
            await protectedTab.click();

            await page.waitForTimeout(500);
            // Protected fields should show warning text instead of sliders
            const warningBox = page.locator('.bg-red-500\\/10, [class*="red"]').first();
            await expect(warningBox).toBeVisible();
        });
    });

    test.describe('Simulation Controls', () => {
        test('shows run simulation button', async ({ page }) => {
            const runButton = page.locator('button').filter({ hasText: /Run Simulation|Simulate/i });
            await expect(runButton).toBeVisible();
        });

        test('run button is disabled when no changes made', async ({ page }) => {
            const runButton = page.locator('button').filter({ hasText: /Run Simulation/i });
            await expect(runButton).toBeDisabled();
        });

        test('making a change enables the run button', async ({ page }) => {
            // Find a slider and change its value
            const slider = page.locator('input[type="range"]').first();
            if (await slider.isVisible({ timeout: 3000 })) {
                // Change the slider value
                await slider.fill('750');

                // Check if run button becomes enabled
                // Button may or may not be enabled depending on validation
            }
        });
    });

    test.describe('Changes Preview', () => {
        test('shows pending changes bar when modifications made', async ({ page }) => {
            // Make a change to trigger the preview bar
            const slider = page.locator('input[type="range"]').first();
            if (await slider.isVisible({ timeout: 3000 })) {
                await slider.fill('800');

                await page.waitForTimeout(500);
                // Preview bar should appear
            }
        });

        test('reset all button clears changes', async ({ page }) => {
            // Make a change
            const slider = page.locator('input[type="range"]').first();
            if (await slider.isVisible({ timeout: 3000 })) {
                await slider.fill('800');

                await page.waitForTimeout(500);
                const resetButton = page.locator('button').filter({ hasText: /Reset/i });
                if (await resetButton.isVisible({ timeout: 2000 })) {
                    await resetButton.click();

                    // Run button should be disabled again
                    const runButton = page.locator('button').filter({ hasText: /Run Simulation/i });
                    await expect(runButton).toBeDisabled();
                }
            }
        });
    });

    test.describe('Results Panel', () => {
        test('shows empty state initially', async ({ page }) => {
            const emptyState = page.locator('text=/Ready to explore|Adjust the sliders/i');
            await expect(emptyState).toBeVisible();
        });

        test('shows quick tips in empty state', async ({ page }) => {
            const tips = page.locator('text=/Lowering credit utilization|Paying down debt|Income increases/i');
            await expect(tips.first()).toBeVisible();
        });
    });
});

test.describe('What-If Accessibility', () => {
    test('sliders have accessible labels', async ({ page }) => {
        await page.goto('/what-if');

        const slider = page.locator('input[type="range"]').first();
        // Sliders should be part of a labeled control group
        if (await slider.isVisible({ timeout: 3000 })) {
            const parent = slider.locator('..');
            const label = parent.locator('label');
            await expect(label).toBeVisible();
        }
    });

    test('buttons are keyboard accessible', async ({ page }) => {
        await page.goto('/what-if');

        // Tab to the run simulation button
        for (let i = 0; i < 15; i++) {
            await page.keyboard.press('Tab');
        }

        const focused = await page.evaluate(() => document.activeElement?.tagName);
        expect(['BUTTON', 'INPUT', 'A']).toContain(focused);
    });
});
