import { test, expect } from "@playwright/test";

test.describe("i18n: locale-scoped chrome", () => {
  test("French home has lang=fr and translated nav labels", async ({ page }) => {
    await page.goto("/fr/");
    await expect(page.locator("html")).toHaveAttribute("lang", "fr");
    await expect(page.locator(".nav-links")).toContainText("Propriétés");
    await expect(page.locator(".nav-links")).toContainText("Vocabulaires");
    await expect(page.locator(".nav-links")).toContainText("À propos");
  });

  test("Spanish home has lang=es and translated nav labels", async ({ page }) => {
    await page.goto("/es/");
    await expect(page.locator("html")).toHaveAttribute("lang", "es");
    await expect(page.locator(".nav-links")).toContainText("Propiedades");
    await expect(page.locator(".nav-links")).toContainText("Vocabularios");
    await expect(page.locator(".nav-links")).toContainText("Acerca de");
  });

  test("English home has lang=en and English nav labels", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("html")).toHaveAttribute("lang", "en");
    await expect(page.locator(".nav-links")).toContainText("Properties");
  });
});

test.describe("i18n: hreflang + og:locale", () => {
  const paths = ["/", "/concepts/", "/docs/use-cases/", "/vocab/country/"];

  for (const base of paths) {
    test(`${base} exposes alternate hreflang for all three locales`, async ({ page }) => {
      await page.goto(base);
      const hreflangs = await page
        .locator('link[rel="alternate"][hreflang]')
        .evaluateAll((els) =>
          els.map((el) => ({
            hreflang: el.getAttribute("hreflang"),
            href: el.getAttribute("href"),
          }))
        );
      const langs = hreflangs.map((h) => h.hreflang);
      expect(langs).toEqual(expect.arrayContaining(["en", "fr", "es", "x-default"]));

      // The canonical EN page must list the FR and ES equivalents under
      // the matching locale prefixes.
      const fr = hreflangs.find((h) => h.hreflang === "fr")?.href ?? "";
      const es = hreflangs.find((h) => h.hreflang === "es")?.href ?? "";
      expect(fr).toContain("/fr/");
      expect(es).toContain("/es/");
    });
  }

  test("FR page has og:locale=fr_FR and lists en_US / es_ES as alternates", async ({ page }) => {
    await page.goto("/fr/");
    await expect(
      page.locator('meta[property="og:locale"]')
    ).toHaveAttribute("content", "fr_FR");

    const alternates = await page
      .locator('meta[property="og:locale:alternate"]')
      .evaluateAll((els) => els.map((el) => el.getAttribute("content")));
    expect(alternates).toEqual(expect.arrayContaining(["en_US", "es_ES"]));
  });
});

test.describe("i18n: language switcher preserves path", () => {
  test("EN -> FR from a vocab page keeps the slug", async ({ page }) => {
    await page.goto("/vocab/country/");
    const frLink = page
      .locator(".lang-switcher-desktop a[hreflang='fr']")
      .first();
    await expect(frLink).toHaveAttribute("href", "/fr/vocab/country/");
  });

  test("FR -> ES from a concept page keeps the slug", async ({ page }) => {
    await page.goto("/fr/concepts/");
    const esLink = page
      .locator(".lang-switcher-desktop a[hreflang='es']")
      .first();
    await expect(esLink).toHaveAttribute("href", "/es/concepts/");
  });
});

test.describe("i18n: per-locale search index", () => {
  for (const { prefix, label } of [
    { prefix: "", label: "root" },
    { prefix: "/fr", label: "fr" },
    { prefix: "/es", label: "es" },
  ]) {
    test(`${label} search index is served and has doc entries`, async ({ request }) => {
      const response = await request.get(`${prefix}/search-index.json`);
      expect(response.ok()).toBe(true);
      const docs = await response.json();
      expect(Array.isArray(docs)).toBe(true);
      expect(docs.length).toBeGreaterThanOrEqual(200);
      const types = new Set(docs.map((d: { type: string }) => d.type));
      expect(types).toContain("doc");
    });
  }

  test("FR search index uses translated doc titles", async ({ request }) => {
    const response = await request.get("/fr/search-index.json");
    const docs: Array<{ id: string; title: string; meta: string }> = await response.json();
    const integration = docs.find((d) => d.id === "doc:integration-patterns");
    expect(integration).toBeDefined();
    expect(integration!.title).toBe("Schémas d'intégration");
    expect(integration!.meta).toBe("Pour commencer");
  });
});

test.describe("i18n: translation banner", () => {
  test("does not appear on a fully translated FR doc", async ({ page }) => {
    await page.goto("/fr/docs/use-cases/");
    await expect(page.locator("[data-translation-banner]")).toHaveCount(0);
  });

  test("does not appear on a fully translated ES doc", async ({ page }) => {
    await page.goto("/es/docs/use-cases/");
    await expect(page.locator("[data-translation-banner]")).toHaveCount(0);
  });
});
