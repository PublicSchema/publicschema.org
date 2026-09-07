import { test, expect } from '@playwright/test';
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const data: { catalogs: Record<string, { path: string }>; metrics: Record<string, { path: string }> } =
  JSON.parse(readFileSync(resolve('../dist/metrics_catalog.json'), 'utf8'));
const paths: string[] = [
  '/metrics/',
  ...Object.values(data.catalogs).map((catalog) => catalog.path),
  ...Object.values(data.metrics).map((metric) => metric.path),
  '/docs/metrics-spec/',
];

// Check every catalog and metric, so adding a catalog cannot silently leave
// its locale-switcher destinations absent from the deployed static output.
test('every metric and specification route exists in every supported locale', () => {
  for (const prefix of ['', '/fr', '/es']) {
    for (const path of paths) {
      const route = `${prefix}${path}`;
      expect(existsSync(resolve('dist', `.${route}`, 'index.html')), route).toBe(true);
    }
  }
});

for (const [locale, heading, calculation] of [
  ['fr', 'Indicateurs', 'Calcul'],
  ['es', 'Indicadores', 'Cálculo'],
]) {
  test(`${locale} metrics journey preserves locale and identifies untranslated content`, async ({ page }) => {
    await page.goto(`/${locale}/metrics/`);
    await expect(page.locator('h1')).toHaveText(heading);
    await expect(page.locator('[data-translation-banner]')).toBeVisible();
    const specLink = page.locator(`a[href="/${locale}/docs/metrics-spec/"]`);
    await expect(specLink).toHaveCount(1);
    await page.locator('.catalog-card').first().click();
    expect(new URL(page.url()).pathname).toMatch(new RegExp(`^/${locale}/metrics/[^/]+/$`));
    await expect(page.locator('[data-translation-banner]')).toBeVisible();
    await page.locator('tbody tr a').first().click();
    expect(new URL(page.url()).pathname).toMatch(new RegExp(`^/${locale}/metrics/[^/]+/[^/]+/$`));
    await expect(page.locator('#calculation h2')).toHaveText(calculation);
    await expect(page.locator('.breadcrumb a').nth(2)).toHaveAttribute('href', new RegExp(`^/${locale}/metrics/`));
    const alternate = locale === 'fr' ? 'es' : 'fr';
    await page.locator('.lang-switcher-desktop summary').click();
    await page.locator(`.lang-switcher-desktop a[hreflang="${alternate}"]`).click();
    await expect(page.locator('html')).toHaveAttribute('lang', alternate);
    await expect(page.locator('h1')).not.toHaveText('Page not found');
    await page.goto(`/${locale}/docs/metrics-spec/`);
    await expect(page.locator('[data-translation-banner]')).toBeVisible();
    await expect(page.locator('.doc-content')).toContainText('MetricCalculation');
  });
}
