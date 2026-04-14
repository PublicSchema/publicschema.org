import { test, expect } from "@playwright/test";

test.describe("Property detail: age_applicability badges", () => {
  test("difficulty_walking_100m shows both adult and child_5_17 badges", async ({ page }) => {
    await page.goto("/difficulty_walking_100m/");
    const metaLine = page.locator(".page-header .meta-line");
    await expect(metaLine.locator(".badge-age-adult")).toHaveText("adult");
    await expect(metaLine.locator(".badge-age-child_5_17")).toHaveText("child 5-17");
    await expect(metaLine.locator(".badge-age-child_2_4")).toHaveCount(0);
  });

  test("difficulty_playing shows only child_2_4 badge", async ({ page }) => {
    await page.goto("/difficulty_playing/");
    const metaLine = page.locator(".page-header .meta-line");
    await expect(metaLine.locator(".badge-age-child_2_4")).toHaveText("child 2-4");
    await expect(metaLine.locator(".badge-age-adult")).toHaveCount(0);
    await expect(metaLine.locator(".badge-age-child_5_17")).toHaveCount(0);
  });

  test("stunting_status shows infant_0_1 and child_2_4 badges only", async ({ page }) => {
    await page.goto("/stunting_status/");
    const metaLine = page.locator(".page-header .meta-line");
    await expect(metaLine.locator(".badge-age-infant_0_1")).toHaveText("infant 0-1");
    await expect(metaLine.locator(".badge-age-child_2_4")).toHaveText("child 2-4");
    await expect(metaLine.locator(".badge-age-adult")).toHaveCount(0);
    await expect(metaLine.locator(".badge-age-child_5_17")).toHaveCount(0);
  });

  test("pregnancy_status shows adult badge only", async ({ page }) => {
    await page.goto("/pregnancy_status/");
    const metaLine = page.locator(".page-header .meta-line");
    await expect(metaLine.locator(".badge-age-adult")).toHaveText("adult");
    await expect(metaLine.locator(".badge-age-child_2_4")).toHaveCount(0);
  });

  test("age band carries numeric range in title attribute", async ({ page }) => {
    await page.goto("/difficulty_walking_100m/");
    const adultBadge = page.locator(".page-header .meta-line .badge-age-adult");
    await expect(adultBadge).toHaveAttribute("title", "18+ years");
    const childBadge = page.locator(".page-header .meta-line .badge-age-child_5_17");
    await expect(childBadge).toHaveAttribute("title", "5-17 years");
  });

  test("French locale translates age band labels", async ({ page }) => {
    await page.goto("/fr/difficulty_walking_100m/");
    const metaLine = page.locator(".page-header .meta-line");
    await expect(metaLine.locator(".badge-age-adult")).toHaveText("adulte");
    await expect(metaLine.locator(".badge-age-child_5_17")).toHaveText("enfant 5-17");
  });

  test("property without age_applicability shows no age badge", async ({ page }) => {
    await page.goto("/given_name/");
    const metaLine = page.locator(".page-header .meta-line");
    await expect(metaLine.locator("[class*='badge-age-']")).toHaveCount(0);
  });
});
