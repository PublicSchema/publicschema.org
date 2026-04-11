import { test, expect } from "@playwright/test";

test.describe("Search: build verification", () => {
  test("search index has correct structure and count", async ({ request }) => {
    const response = await request.get("/search-index.json");
    expect(response.ok()).toBe(true);

    const docs = await response.json();
    expect(Array.isArray(docs)).toBe(true);
    expect(docs.length).toBeGreaterThanOrEqual(200);

    // Check required fields on every document
    for (const doc of docs) {
      expect(doc).toHaveProperty("id");
      expect(doc).toHaveProperty("type");
      expect(doc).toHaveProperty("title");
      expect(doc).toHaveProperty("body");
      expect(doc).toHaveProperty("path");
    }

    // Check all four types are present
    const types = new Set(docs.map((d: { type: string }) => d.type));
    expect(types).toContain("concept");
    expect(types).toContain("property");
    expect(types).toContain("vocabulary");
    expect(types).toContain("doc");
  });
});

test.describe("Search: desktop", () => {
  test("search input is visible and focusable", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await expect(input).toBeVisible();
    await input.focus();
    await expect(input).toBeFocused();
  });

  test("typing a concept name shows results", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("Person");

    // Wait for debounce + search
    const results = page.locator("#search-results");
    await expect(results).not.toHaveAttribute("hidden", "");
    await expect(results.locator('[role="option"]').first()).toBeVisible();

    // Should show a concept result for "Person"
    const personResult = results.locator('a[href="/Person"]');
    await expect(personResult).toBeVisible();
    await expect(personResult.locator(".badge")).toHaveText("concept");
  });

  test("clicking a result navigates to the correct page", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("Person");

    const results = page.locator("#search-results");
    await expect(results.locator('[role="option"]').first()).toBeVisible();

    await results.locator('a[href="/Person"]').click();
    await expect(page).toHaveURL(/\/Person\/?$/);
  });

  test("typing a property name shows a property result", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("date_of_birth");

    const results = page.locator("#search-results");
    await expect(results.locator('[role="option"]').first()).toBeVisible();

    const propResult = results.locator('a[href="/date_of_birth"]');
    await expect(propResult).toBeVisible();
    await expect(propResult.locator(".badge")).toHaveText("property");
  });

  test("searching a vocabulary value finds the parent vocabulary", async ({
    page,
  }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("married");

    const results = page.locator("#search-results");
    await expect(results.locator('[role="option"]').first()).toBeVisible();

    // The marital-status vocabulary should appear with a matched-value hint
    const vocabResult = results.locator('a[href="/vocab/marital-status"]');
    await expect(vocabResult).toBeVisible();
    const context = vocabResult.locator(".search-result-context");
    await expect(context).toContainText("Matched");
  });

  test("keyboard shortcut hint is displayed", async ({ page }) => {
    await page.goto("/");
    const hint = page.locator(".search-shortcut");
    await expect(hint).toBeVisible();
    // Should contain either Ctrl+K or the Mac command key symbol
    const text = await hint.textContent();
    expect(text === "Ctrl+K" || text === "\u2318K").toBe(true);
  });

  test("no results for nonsense query", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("xyzzy_nonsense_query_12345");

    const noResults = page.locator(".search-no-results");
    await expect(noResults).toBeVisible();
  });

  test("single character shows min-chars message", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("a");

    const minChars = page.locator(".search-min-chars");
    await expect(minChars).toBeVisible();

    // No result options should be present
    const options = page.locator("#search-results [role='option']");
    await expect(options).toHaveCount(0);
  });

  test("Escape closes the dropdown", async ({ page }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("Person");

    const results = page.locator("#search-results");
    await expect(results.locator('[role="option"]').first()).toBeVisible();

    await page.keyboard.press("Escape");
    await expect(results).toHaveAttribute("hidden", "");
  });

  test("keyboard navigation: ArrowDown + Enter navigates", async ({
    page,
  }) => {
    await page.goto("/");
    const input = page.locator(".search-container .search-input");
    await input.focus();
    await input.fill("Person");

    const results = page.locator("#search-results");
    await expect(results.locator('[role="option"]').first()).toBeVisible();

    // Arrow down to first result
    await page.keyboard.press("ArrowDown");
    const firstOption = results.locator('[role="option"]').first();
    await expect(firstOption).toHaveAttribute("aria-selected", "true");

    // Get the href of the first selected option
    const href = await firstOption.getAttribute("href");
    expect(href).toBeTruthy();

    // Enter to navigate
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(new RegExp(href!.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  });
});

test.describe("Search: keyboard shortcut", () => {
  test("Ctrl+K focuses the search input", async ({ page }) => {
    await page.goto("/");

    // Click somewhere else first to ensure input is not focused
    await page.locator("body").click();

    const input = page.locator(".search-container .search-input");
    await expect(input).not.toBeFocused();

    // Use Ctrl+K (works on all platforms in Playwright)
    await page.keyboard.press("Control+k");
    await expect(input).toBeFocused();
  });
});

test.describe("Search: mobile", () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test("search icon is visible, desktop input is hidden", async ({ page }) => {
    await page.goto("/");
    const desktopInput = page.locator(".search-container .search-input");
    await expect(desktopInput).not.toBeVisible();

    const mobileToggle = page.locator(".search-mobile-toggle");
    await expect(mobileToggle).toBeVisible();
  });

  test("search icon opens overlay and search works", async ({ page }) => {
    await page.goto("/");
    const mobileToggle = page.locator(".search-mobile-toggle");
    await mobileToggle.click();

    // Overlay should appear
    const overlay = page.locator(".search-overlay");
    await expect(overlay).toBeVisible();

    // Type in the overlay input
    const overlayInput = overlay.locator(".search-input");
    await expect(overlayInput).toBeFocused();
    await overlayInput.fill("Enrollment");

    // Results should appear in the overlay
    const results = overlay.locator('[role="option"]');
    await expect(results.first()).toBeVisible();
  });

  test("close button dismisses overlay", async ({ page }) => {
    await page.goto("/");
    const mobileToggle = page.locator(".search-mobile-toggle");
    await mobileToggle.click();

    const overlay = page.locator(".search-overlay");
    await expect(overlay).toBeVisible();

    const closeBtn = overlay.locator(".search-overlay-close");
    await closeBtn.click();

    await expect(overlay).not.toBeVisible();
  });

  test("Escape dismisses overlay", async ({ page }) => {
    await page.goto("/");
    const mobileToggle = page.locator(".search-mobile-toggle");
    await mobileToggle.click();

    const overlay = page.locator(".search-overlay");
    await expect(overlay).toBeVisible();

    await page.keyboard.press("Escape");
    await expect(overlay).not.toBeVisible();
  });
});
