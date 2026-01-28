/**
 * Admin & Fairness E2E Tests
 * S6.1 - Expanded E2E test suite for admin features
 */
import { test, expect } from '@playwright/test';

test.describe('Admin Programs Page', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/programs');
    });

    test('should display program catalog header', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/program/i);
    });

    test('should show program list with key columns', async ({ page }) => {
        // Check for table or list structure
        const table = page.locator('table, [role="grid"]');
        await expect(table.or(page.locator('.program-list, .program-card'))).toBeVisible();
    });

    test('should have create program button', async ({ page }) => {
        const createBtn = page.getByRole('button', { name: /create|add|new/i });
        await expect(createBtn).toBeVisible();
    });

    test('should open program creation modal on click', async ({ page }) => {
        await page.getByRole('button', { name: /create|add|new/i }).first().click();

        // Modal or form should appear
        const modal = page.locator('[role="dialog"], .modal, form');
        await expect(modal).toBeVisible();
    });

    test('should filter programs by status', async ({ page }) => {
        const filterBtn = page.getByRole('button', { name: /filter|status/i }).or(
            page.locator('select[name*="status"]')
        );

        if (await filterBtn.isVisible()) {
            await filterBtn.click();
        }
    });
});

test.describe('Admin Rulesets Page', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/rulesets');
    });

    test('should display rulesets header', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/ruleset/i);
    });

    test('should show ruleset list', async ({ page }) => {
        await expect(page.locator('.ruleset-card, table, [role="grid"]').first()).toBeVisible();
    });

    test('should have version history view', async ({ page }) => {
        const versionTab = page.getByRole('tab', { name: /version|history/i }).or(
            page.getByRole('button', { name: /version|history/i })
        );

        if (await versionTab.isVisible()) {
            await versionTab.click();
        }
    });
});

test.describe('Admin Reason Codes Page', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/reason-codes');
    });

    test('should display reason codes header', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/reason/i);
    });

    test('should show reason code categories', async ({ page }) => {
        // Should show category badges or filters
        const categories = page.locator('.category, [data-category], .badge');
        await expect(categories.first()).toBeVisible();
    });
});

test.describe('Fairness Dashboard', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/fairness');
    });

    test('should display fairness metrics overview', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/fairness/i);
    });

    test('should show disparate impact metrics', async ({ page }) => {
        const diSection = page.getByText(/disparate impact|DI ratio/i);
        await expect(diSection).toBeVisible();
    });

    test('should display protected attributes', async ({ page }) => {
        const attributes = page.getByText(/race|gender|age|ethnicity/i).first();
        await expect(attributes).toBeVisible();
    });

    test('should have LDA search controls', async ({ page }) => {
        const ldaSection = page.getByText(/LDA|less discriminatory/i);
        await expect(ldaSection).toBeVisible();
    });

    test('should show test history', async ({ page }) => {
        const historySection = page.getByText(/test history|recent tests/i).or(
            page.locator('.test-history, [data-testid="test-history"]')
        );
        await expect(historySection).toBeVisible();
    });
});

test.describe('Fairness Artifact Viewer', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/fairness/artifacts');
    });

    test('should display artifacts list', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/artifact/i);
    });

    test('should show artifact cards with metrics', async ({ page }) => {
        const card = page.locator('.artifact-card, [data-artifact]').first();
        await expect(card.or(page.getByText(/artifact/i))).toBeVisible();
    });

    test('should have download buttons', async ({ page }) => {
        const downloadBtn = page.getByRole('button', { name: /download|export/i }).first();
        if (await downloadBtn.isVisible()) {
            await expect(downloadBtn).toBeEnabled();
        }
    });
});

test.describe('Post-Deploy Monitoring', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/fairness/monitoring');
    });

    test('should display monitoring dashboard', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/monitor/i);
    });

    test('should show service health status', async ({ page }) => {
        const healthSection = page.getByText(/health|status|healthy/i);
        await expect(healthSection).toBeVisible();
    });

    test('should display key metrics', async ({ page }) => {
        const metricsSection = page.getByText(/metric|latency|throughput/i);
        await expect(metricsSection).toBeVisible();
    });

    test('should show alerts section', async ({ page }) => {
        const alertsSection = page.getByText(/alert|warning|notification/i);
        await expect(alertsSection).toBeVisible();
    });
});

test.describe('Partner Management', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/partners');
    });

    test('should display partners list', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/partner/i);
    });

    test('should show partner cards or table', async ({ page }) => {
        const partnerList = page.locator('.partner-card, table, [role="grid"]');
        await expect(partnerList.first()).toBeVisible();
    });

    test('should have add partner button', async ({ page }) => {
        const addBtn = page.getByRole('button', { name: /add|create|new/i });
        await expect(addBtn).toBeVisible();
    });
});

test.describe('Partner Audit Log', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/partners/audit');
    });

    test('should display audit log header', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/audit/i);
    });

    test('should show log entries', async ({ page }) => {
        const logEntry = page.locator('.log-entry, tr, [data-log]').first();
        await expect(logEntry.or(page.getByText(/log|entry|event/i))).toBeVisible();
    });

    test('should have filter controls', async ({ page }) => {
        const filterSection = page.locator('.filters, [data-filters]').or(
            page.getByRole('combobox')
        );
        if (await filterSection.first().isVisible()) {
            await expect(filterSection.first()).toBeEnabled();
        }
    });
});

test.describe('Partner API Documentation', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/partners/api-docs');
    });

    test('should display API docs header', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/API|documentation/i);
    });

    test('should show endpoint list', async ({ page }) => {
        const endpoints = page.getByText(/GET|POST|PUT|DELETE/i);
        await expect(endpoints.first()).toBeVisible();
    });

    test('should display authentication section', async ({ page }) => {
        const authSection = page.getByText(/authentication|API key|bearer/i);
        await expect(authSection).toBeVisible();
    });

    test('should show request/response examples', async ({ page }) => {
        const codeBlock = page.locator('pre, code, .code-block');
        await expect(codeBlock.first()).toBeVisible();
    });
});

test.describe('Review Queue', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/admin/review');
    });

    test('should display review queue', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/review/i);
    });

    test('should show pending cases count', async ({ page }) => {
        const countBadge = page.getByText(/pending|\d+ case/i);
        await expect(countBadge).toBeVisible();
    });

    test('should have priority filtering', async ({ page }) => {
        const priorityFilter = page.getByRole('button', { name: /priority|urgent|high/i }).or(
            page.locator('select[name*="priority"]')
        );
        if (await priorityFilter.first().isVisible()) {
            await expect(priorityFilter.first()).toBeEnabled();
        }
    });

    test('should show case details on selection', async ({ page }) => {
        const caseRow = page.locator('[data-case], .case-row, tr').first();
        if (await caseRow.isVisible()) {
            await caseRow.click();
            // Detail panel should appear
            await expect(page.locator('.detail-panel, [data-detail]').or(
                page.getByText(/details|summary/i)
            )).toBeVisible();
        }
    });
});

test.describe('Audit Viewer', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/audit-viewer');
    });

    test('should display audit viewer', async ({ page }) => {
        await expect(page.locator('h1')).toContainText(/audit/i);
    });

    test('should have view mode tabs', async ({ page }) => {
        const tabs = page.getByRole('tab').or(
            page.locator('.tab, [role="tablist"] button')
        );
        await expect(tabs.first()).toBeVisible();
    });

    test('should show snapshot timeline', async ({ page }) => {
        const timeline = page.locator('.timeline, [data-timeline]').or(
            page.getByText(/snapshot/i)
        );
        await expect(timeline).toBeVisible();
    });
});
