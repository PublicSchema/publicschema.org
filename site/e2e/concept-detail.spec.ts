import { test, expect } from "@playwright/test";

test.describe("Concept detail: property groups", () => {
  test("SocioEconomicProfile page shows category separators in single table", async ({ page }) => {
    await page.goto("/SocioEconomicProfile/");

    // Single properties table with one header
    const table = page.locator("#properties table.data-table");
    await expect(table).toHaveCount(1);
    const theads = table.locator("thead");
    await expect(theads).toHaveCount(1);

    // Category separator rows present (housing, wash, energy, assets, ict, economic, food_security,
    // demographics, administrative = 9 groups)
    const separators = page.locator(".category-separator");
    const count = await separators.count();
    expect(count).toBeGreaterThanOrEqual(5);

    // Specific categories present
    await expect(page.locator("#group-housing .category-separator")).toContainText("Housing");
    await expect(page.locator("#group-wash .category-separator")).toContainText("Water & Sanitation");
    await expect(page.locator("#group-energy .category-separator")).toContainText("Energy");
  });

  test("Household page lists location and food security after refactor", async ({ page }) => {
    await page.goto("/Household/");

    // Food security summary flag remains on Household; socio-economic items moved away
    const rows = page.locator("#properties table.data-table tbody tr");
    const rowCount = await rows.count();
    expect(rowCount).toBeGreaterThanOrEqual(1);
    await expect(page.locator("#properties")).toContainText(/food_security_level/);
    await expect(page.locator("#properties")).not.toContainText(/dwelling_type/);
    await expect(page.locator("#properties")).not.toContainText(/wall_material/);
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
  test("Enrollment page shows flat property table without category separators", async ({ page }) => {
    await page.goto("/sp/Enrollment/");

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
