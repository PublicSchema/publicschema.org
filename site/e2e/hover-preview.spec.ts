import { test, expect } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test.describe("Hover preview card", () => {
  test("preview attribute is attached to schema entity links", async ({ page }) => {
    await page.goto("/Household/");

    // Concept detail pages must surface at least one preview-enabled link
    // (property rows, supertypes, subtypes, etc.).
    const preview = page.locator("[data-preview-key]");
    const n = await preview.count();
    expect(n).toBeGreaterThan(0);

    // Property rows in the concept table carry preview keys with a leading slash.
    const first = preview.first();
    const key = await first.getAttribute("data-preview-key");
    expect(key).toMatch(/^\//);
  });

  test("hovering a link opens a preview panel, leaving closes it", async ({ page }) => {
    await page.goto("/Household/");

    const anchor = page.locator("[data-preview-key]").first();
    const label = (await anchor.textContent())?.trim() ?? "";
    await anchor.hover();

    const panel = page.locator(".hover-card-panel");
    await expect(panel).toBeVisible({ timeout: 3000 });

    // Panel should carry the anchor's label.
    if (label) {
      await expect(panel).toContainText(label);
    }

    // Move away and the panel should close.
    await page.mouse.move(0, 0);
    await expect(panel).toBeHidden({ timeout: 3000 });
  });

  test("pressing Escape closes an open preview", async ({ page }) => {
    await page.goto("/Household/");

    const anchor = page.locator("[data-preview-key]").first();
    await anchor.hover();

    const panel = page.locator(".hover-card-panel");
    await expect(panel).toBeVisible({ timeout: 3000 });

    await page.keyboard.press("Escape");
    await expect(panel).toBeHidden({ timeout: 3000 });
  });
});
