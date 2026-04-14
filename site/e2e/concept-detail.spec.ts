import { test, expect } from "@playwright/test";

test.describe("Concept detail: property groups", () => {
  test("Household page shows category separators in single table", async ({ page }) => {
    await page.goto("/Household/");

    // Single properties table with one header
    const table = page.locator("#properties table.data-table");
    await expect(table).toHaveCount(1);
    const theads = table.locator("thead");
    await expect(theads).toHaveCount(1);

    // Category separator rows present
    const separators = page.locator(".category-separator");
    const count = await separators.count();
    expect(count).toBeGreaterThanOrEqual(5);

    // Specific categories present
    await expect(page.locator("#group-identity .category-separator")).toContainText("Identity");
    await expect(page.locator("#group-housing .category-separator")).toContainText("Housing");
    await expect(page.locator("#group-wash .category-separator")).toContainText("Water & Sanitation");
    await expect(page.locator("#group-energy .category-separator")).toContainText("Energy");

    // Inherited properties have badges
    const inheritedBadges = page.locator(".inherited-badge");
    const badgeCount = await inheritedBadges.count();
    expect(badgeCount).toBeGreaterThanOrEqual(1);
    await expect(inheritedBadges.first()).toContainText("from");
  });

  test("CRVSPerson page shows category separators", async ({ page }) => {
    await page.goto("/crvs/CRVSPerson/");

    const separators = page.locator(".category-separator");
    const count = await separators.count();
    expect(count).toBeGreaterThanOrEqual(4);

    await expect(page.locator("#group-demographics .category-separator")).toContainText("Demographics");
    await expect(page.locator("#group-education .category-separator")).toContainText("Education");
    await expect(page.locator("#group-employment .category-separator")).toContainText("Employment");
  });
});

test.describe("Concept detail: flat table fallback", () => {
  test("Address page shows flat property table without category separators", async ({ page }) => {
    await page.goto("/Address/");

    // Properties section exists with a table
    const table = page.locator("#properties table.data-table");
    await expect(table).toHaveCount(1);

    // No category separators
    const separators = page.locator(".category-separator");
    await expect(separators).toHaveCount(0);

    // Properties are rendered as rows
    const rows = table.locator("tbody tr");
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThanOrEqual(1);
  });
});
