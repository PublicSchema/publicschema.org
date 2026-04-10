import { test, expect } from "@playwright/test";

test.describe("Vocabulary page: external values", () => {
  test("country page hides values table and shows standard reference", async ({ page }) => {
    await page.goto("/vocab/country");

    // Should show the "external standard" message with standard name
    const externalMsg = page.getByText("defined by an external standard (ISO 3166-1)");
    await expect(externalMsg).toBeVisible();

    // Should link to the official standard page
    const standardLink = page.getByRole('link', { name: 'official standard page' });
    await expect(standardLink).toBeVisible();

    // Should NOT show a values data table
    const valuesTable = page.locator(".concept-section table.data-table.mobile-card-table");
    await expect(valuesTable).toHaveCount(0);

    // Download links should still be present
    await expect(page.locator('a[href="/vocab/country.csv"]')).toBeVisible();
    await expect(page.locator('a[href="/vocab/country.jsonld"]')).toBeVisible();
  });

  test("currency page hides values table", async ({ page }) => {
    await page.goto("/vocab/currency");
    await expect(page.getByText("defined by an external standard (ISO 4217)")).toBeVisible();
    const valuesTable = page.locator(".concept-section table.data-table.mobile-card-table");
    await expect(valuesTable).toHaveCount(0);
  });

  test("language page hides values table", async ({ page }) => {
    await page.goto("/vocab/language");
    await expect(page.getByText("defined by an external standard (ISO 639-3)")).toBeVisible();
    const valuesTable = page.locator(".concept-section table.data-table.mobile-card-table");
    await expect(valuesTable).toHaveCount(0);
  });

  test("script page hides values table", async ({ page }) => {
    await page.goto("/vocab/script");
    await expect(page.getByText("defined by an external standard (ISO 15924)")).toBeVisible();
    const valuesTable = page.locator(".concept-section table.data-table.mobile-card-table");
    await expect(valuesTable).toHaveCount(0);
  });
});

test.describe("Vocabulary page: inline values", () => {
  test("gender-type page shows values table", async ({ page }) => {
    await page.goto("/vocab/gender-type");

    // Should NOT show the "external standard" message
    await expect(page.getByText("defined by an external standard")).toHaveCount(0);

    // Should show a values data table with codes
    const valuesTable = page.locator(".concept-section table.data-table.mobile-card-table");
    await expect(valuesTable).toBeVisible();
    await expect(valuesTable.locator("tbody tr").first()).toBeVisible();
  });
});
