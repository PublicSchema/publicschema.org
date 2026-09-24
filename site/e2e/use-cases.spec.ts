import { test, expect } from '@playwright/test';
import { localePath } from '../src/i18n/utils';
import type { Locale } from '../src/i18n/languages';

for (const locale of ['en', 'fr', 'es'] as Locale[]) {
  test(`${locale} use cases cover sector registries and every contents link has a target`, async ({ page }) => {
    await page.goto(localePath('/docs/use-cases/', locale));
    const anchors = await page.locator('main a[href^="#"]').evaluateAll((els) =>
      els.map((el) => decodeURIComponent(el.getAttribute('href')!.slice(1))).filter(Boolean));
    expect(anchors.length).toBeGreaterThanOrEqual(14);
    for (const id of anchors) {
      await expect(page.locator(`[id="${id}"]`), `#${id}`).toHaveCount(1);
    }

    for (const concept of ['/agri/Farm', '/land/LandSpatialUnit', '/tax/TaxRegistration', '/agri/FarmerRegistration']) {
      await expect(page.locator(`main a[href^="${localePath(concept, locale)}"]`).first()).toBeVisible();
    }
  });

  test(`${locale} use cases internal links all resolve`, async ({ page, request }) => {
    await page.goto(localePath('/docs/use-cases/', locale));
    const hrefs = await page.locator('main a[href^="/"]').evaluateAll((els) =>
      els.map((el) => el.getAttribute('href')!));
    const unique = [...new Set(hrefs.map((h) => h.split('#')[0]))];
    expect(unique.length).toBeGreaterThan(0);
    for (const href of unique) {
      const response = await request.get(href);
      expect(response.status(), href).toBe(200);
    }
  });
}
