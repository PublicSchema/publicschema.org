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

  test("crvs/Person page shows category separators", async ({ page }) => {
    await page.goto("/crvs/Person/");

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

test.describe("Concept detail: profile hierarchy smoke tests", () => {
  test("Profile abstract page renders with QuestionnaireResponse FHIR peer", async ({ page }) => {
    await page.goto("/Profile/");
    await expect(page.locator("h1").first()).toContainText(/Profile/);
    await expect(page.locator("body")).toContainText(/QuestionnaireResponse/);
    await expect(page.locator("#properties")).toContainText(/instrument_used/);
  });

  test("FunctioningProfile page lists WG/CFM items and administrative context", async ({ page }) => {
    await page.goto("/FunctioningProfile/");
    const body = page.locator("body");
    await expect(body).toContainText(/Washington Group|WG-SS|CFM/);
    await expect(page.locator("#properties")).toContainText(/difficulty_seeing/);
    await expect(page.locator("#properties")).toContainText(/administration_mode/);
  });

  test("AnthropometricProfile page lists measurements and growth reference", async ({ page }) => {
    await page.goto("/AnthropometricProfile/");
    await expect(page.locator("#properties")).toContainText(/muac/);
    await expect(page.locator("#properties")).toContainText(/growth_reference/);
    await expect(page.locator("#properties")).toContainText(/oedema_present/);
  });

  test("Instrument registry page renders with version and publisher fields", async ({ page }) => {
    await page.goto("/Instrument/");
    await expect(page.locator("#properties")).toContainText(/version/);
    await expect(page.locator("#properties")).toContainText(/publisher/);
    await expect(page.locator("#properties")).toContainText(/item_set/);
  });

  test("ScoringRule page renders with scoring_method and cutoff_score", async ({ page }) => {
    await page.goto("/ScoringRule/");
    await expect(page.locator("#properties")).toContainText(/scoring_method/);
    await expect(page.locator("#properties")).toContainText(/cutoff_score/);
  });

  test("ScoringEvent page renders with rule_applied and raw_score", async ({ page }) => {
    await page.goto("/ScoringEvent/");
    await expect(page.locator("#properties")).toContainText(/rule_applied/);
    await expect(page.locator("#properties")).toContainText(/raw_score/);
    await expect(page.locator("#properties")).toContainText(/assessment_band/);
  });
});
