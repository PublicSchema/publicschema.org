import { test, expect } from "@playwright/test";

test.describe("Systems index page", () => {
  test("renders all known systems", async ({ page }) => {
    await page.goto("/systems/");
    await expect(page.locator("main h1")).toHaveText("Systems");

    // All system display names should appear. More entries may be added over
    // time, so assert presence rather than an exact row count.
    for (const name of ["OpenSPP", "openIMIS", "DCI", "FHIR R4", "DHIS2", "OpenCRVS"]) {
      await expect(page.getByText(name)).toBeVisible();
    }
  });

  test("each system links to its detail page", async ({ page }) => {
    await page.goto("/systems/");
    const opensppLink = page.locator('a[href="/systems/openspp/"]');
    await expect(opensppLink).toBeVisible();
  });

  test("shows review status badges", async ({ page }) => {
    await page.goto("/systems/");
    const badges = page.locator(".badge-unreviewed");
    await expect(badges.first()).toBeVisible();
  });
});

test.describe("System detail page", () => {
  test("OpenSPP page renders with correct content", async ({ page }) => {
    await page.goto("/systems/openspp/");

    // Header
    await expect(page.locator("main h1")).toContainText("OpenSPP");
    await expect(page.locator("main .badge-unreviewed")).toBeVisible();

    // Breadcrumb links back to systems index
    const breadcrumbLink = page.locator('.breadcrumb a[href="/systems/"]');
    await expect(breadcrumbLink).toBeVisible();

    // Description
    await expect(page.getByText("Open-source social protection platform")).toBeVisible();

    // Issue link
    const issueLink = page.locator('a[href*="issues/new"]');
    await expect(issueLink.first()).toBeVisible();
  });

  test("OpenSPP page shows vocabulary table with correct entries", async ({ page }) => {
    await page.goto("/systems/openspp/");

    // Should have a vocabularies table
    const table = page.locator("#vocabularies table");
    await expect(table).toBeVisible();

    // gender-type should be listed with value mapping
    const genderRow = page.locator("#vocabularies tr", { hasText: "gender-type" });
    await expect(genderRow).toBeVisible();
    await expect(genderRow.getByText("Value mapping")).toBeVisible();

    // education-level should be listed (has both value mapping and same standard,
    // but shows as value mapping per plan)
    const educationRow = page.locator("#vocabularies tr", { hasText: "education-level" });
    await expect(educationRow).toBeVisible();
  });

  test("OpenSPP page shows same-standard-only vocabs", async ({ page }) => {
    await page.goto("/systems/openspp/");

    // country is same-standard only for openspp
    const countryRow = page.locator("#vocabularies tr", { hasText: "country" });
    await expect(countryRow).toBeVisible();
    await expect(countryRow.getByText("Same standard")).toBeVisible();
    await expect(countryRow.getByText("All values")).toBeVisible();
  });

  test("DHIS2 page has fewer vocabularies than OpenSPP", async ({ page }) => {
    await page.goto("/systems/dhis2/");
    await expect(page.locator("main h1")).toContainText("DHIS2");

    const rows = page.locator("#vocabularies table tbody tr");
    const count = await rows.count();
    // DHIS2 has 3 vocabularies
    expect(count).toBeLessThanOrEqual(5);
    expect(count).toBeGreaterThanOrEqual(3);
  });

  test("vocabulary links point to vocab pages", async ({ page }) => {
    await page.goto("/systems/openspp/");
    // Links include a #system hash fragment pointing at the relevant mapping
    // section, so match by prefix.
    const vocabLink = page.locator('a[href^="/vocab/gender-type"]');
    await expect(vocabLink.first()).toBeVisible();
  });

  test("report issue button appears at bottom", async ({ page }) => {
    await page.goto("/systems/openspp/");
    const buttons = page.locator('a.btn', { hasText: "Report an issue" });
    await expect(buttons).toBeVisible();
  });

  test("DHIS2 page shows concept matches section", async ({ page }) => {
    await page.goto("/systems/dhis2/");
    const heading = page.locator("h2", { hasText: "Concept matches" });
    await expect(heading).toBeVisible();
    // Person row with a link to the concept page and a match-level badge.
    const personRow = page.locator("#concept-matches tr", { hasText: "Person" }).first();
    await expect(personRow).toBeVisible();
    await expect(personRow.locator('a[href="/Person/"]')).toBeVisible();
    await expect(personRow.locator(".badge")).toBeVisible();
  });

  test("OpenSPP page shows documented gaps section", async ({ page }) => {
    await page.goto("/systems/openspp/");
    const heading = page.locator("h2", { hasText: "Documented gaps" });
    await expect(heading).toBeVisible();
    // Each gap row links to the v2 item it references.
    const gapRows = page.locator("#documented-gaps tbody tr");
    const count = await gapRows.count();
    expect(count).toBeGreaterThan(0);
  });
});

test.describe("Vocab page links to system pages", () => {
  test("system mapping headings link to system pages", async ({ page }) => {
    await page.goto("/vocab/gender-type/");

    // System mapping headings should be links
    const opensppLink = page.locator('h3 a[href="/systems/openspp/"]');
    await expect(opensppLink).toBeVisible();
    await expect(opensppLink).toHaveText("OpenSPP");
  });

  test("same standard section links to system pages", async ({ page }) => {
    await page.goto("/vocab/gender-type/");

    // Same standard section should link to system pages
    const fhirLink = page.locator('a[href="/systems/fhir_r4/"]');
    await expect(fhirLink.first()).toBeVisible();
  });
});

test.describe("Footer", () => {
  test("footer includes systems link", async ({ page }) => {
    await page.goto("/");
    const footerLink = page.locator('footer a[href="/systems/"]');
    await expect(footerLink).toBeVisible();
    await expect(footerLink).toHaveText("Systems");
  });
});
