import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';
import { createDomainCatalog } from '../src/data/domains';
import { localePath } from '../src/i18n/utils';
import type { VocabularyData } from '../src/data/vocabulary';
import type { Locale } from '../src/i18n/languages';

const vocabulary = JSON.parse(
  readFileSync(new URL('../../dist/vocabulary.json', import.meta.url), 'utf8'),
) as VocabularyData;

test('domain metadata orders represented domains and falls back to English and unknown codes', () => {
  const catalog = createDomainCatalog({ meta: {
    name: 'test', base_uri: 'https://publicschema.org/', version: 'draft',
    domains: {
      land: { label: { en: 'Land', fr: 'Foncier' }, description: { en: 'Land records' } },
      health: { label: { en: 'Health' } },
      agri: { label: { en: 'Agriculture' } },
    },
  } }, 'fr');
  const entries = [
    { domain: 'agri', id: 'Farm' },
    { domain: 'unknown', id: 'Example' },
    { domain: null, id: 'Person' },
    { domain: 'land', id: 'Parcel' },
    { domain: 'land', id: 'Holding' },
  ];
  expect(catalog.present(entries).map(({ value, label }) => [value, label])).toEqual([
    ['root', 'Universel'], ['land', 'Foncier'], ['agri', 'Agriculture'], ['unknown', 'unknown'],
  ]);
  expect(catalog.get('land').description).toBe('Land records');
  expect(entries.sort(catalog.compare).map(({ id }) => id)).toEqual([
    'Person', 'Holding', 'Parcel', 'Farm', 'Example',
  ]);
});

test('historical exports retain translated domain labels and unknown domains', () => {
  const catalog = createDomainCatalog({ meta: {
    name: 'test', base_uri: 'https://publicschema.org/', version: 'draft',
  } }, 'es');
  expect(catalog.present([{ domain: 'metrics' }, { domain: 'crvs' }, { domain: 'sp' }])
    .map(({ value }) => value)).toEqual(['sp', 'crvs', 'metrics']);
  expect(catalog.get('sp').label).toBe('Protección social');
  expect(catalog.get('metrics').filterLabel).toBe('metrics');
});

const indexes = [
  { collection: 'concepts', path: '/concepts/', card: '.concept-card' },
  { collection: 'properties', path: '/properties/', card: '.concept-card' },
  { collection: 'vocabularies', path: '/vocab/', card: '.concept-card' },
] as const;

// Static preview on a case-insensitive filesystem cannot distinguish existing
// paths such as /metrics/Metric and /metrics/metric. Domain breadcrumb coverage
// uses unambiguous representatives; it does not verify every public route.
const pathSpellings = new Map<string, Set<string>>();
for (const { collection } of indexes) {
  for (const { path } of Object.values(vocabulary[collection])) {
    const folded = path.toLowerCase();
    const spellings = pathSpellings.get(folded) ?? new Set<string>();
    spellings.add(path);
    pathSpellings.set(folded, spellings);
  }
}

for (const locale of ['en', 'fr', 'es'] as Locale[]) {
  for (const { collection, path, card } of indexes) {
    test(`${locale} ${collection} filters every represented domain and restores its URL`, async ({ page }) => {
      const entries = Object.values(vocabulary[collection]);
      const catalog = createDomainCatalog(vocabulary, locale);
      const domains = catalog.present(entries);
      await page.goto(localePath(path, locale));
      const boxes = page.locator('input[name="domain"]');
      expect(await boxes.evaluateAll((elements) => elements.map((el) => (el as HTMLInputElement).value)))
        .toEqual(domains.map(({ value }) => value));

      for (const domain of domains) {
        const box = page.locator(`input[name="domain"][value="${domain.value}"]`);
        await expect(box.locator('..')).toContainText(domain.filterLabel);
        await box.check();
        const count = entries.filter((entry) => (entry.domain ?? 'root') === domain.value).length;
        await expect(page.locator(`${card}:visible`)).toHaveCount(count);
        await expect(page.locator(`${card}:visible:not([data-domain="${domain.value}"])`)).toHaveCount(0);
        await expect(page).toHaveURL(new RegExp(`domain=${domain.value}`));
        await page.reload();
        await expect(box).toBeChecked();
        await expect(page.locator(`${card}:visible`)).toHaveCount(count);
        await box.uncheck();
      }
    });
  }

  test(`${locale} domain breadcrumbs open the matching filtered index`, async ({ page }) => {
    for (const { collection, path, card } of indexes) {
      const entries = Object.values(vocabulary[collection]);
      const domains = createDomainCatalog(vocabulary, locale).present(entries).filter(({ code }) => code);
      for (const domain of domains) {
        const entry = entries.find((item) => item.domain === domain.code
          && pathSpellings.get(item.path.toLowerCase())?.size === 1);
        expect(entry, `${collection}: ${domain.value} needs a case-unambiguous breadcrumb representative`).toBeDefined();
        if (!entry) throw new Error(`No unambiguous ${collection} page for ${domain.value}`);
        const response = await page.goto(localePath(entry.path, locale));
        expect(response?.status()).toBe(200);
        await expect(page.locator('.page-header .uri')).toHaveText(entry.uri);
        const href = `${localePath(path, locale)}?domain=${encodeURIComponent(domain.value)}`;
        const breadcrumb = page.locator(`.breadcrumb a[href="${href}"]`);
        await expect(breadcrumb).toHaveText(domain.label);
        await breadcrumb.click();
        await expect(page).toHaveURL(new URL(href, page.url()).href);
        await expect(page.locator(`input[name="domain"][value="${domain.value}"]`)).toBeChecked();
        await expect(page.locator(`${card}:visible`))
          .toHaveCount(entries.filter((item) => item.domain === domain.code).length);
        await expect(page.locator(`${card}:visible:not([data-domain="${domain.value}"])`)).toHaveCount(0);
      }
    }
  });
}

test('visualization filters and domain map include every concept domain', async ({ page }) => {
  const domains = createDomainCatalog(vocabulary).present(Object.values(vocabulary.concepts));
  await page.goto('/viz/concepts-faceted/');
  expect(await page.locator('input[name="domain"]').evaluateAll((elements) =>
    elements.map((element) => (element as HTMLInputElement).value))).toEqual(domains.map(({ value }) => value));
  await page.goto('/viz/convergence-bar/');
  expect(await page.locator('.domain-toggle').evaluateAll((elements) =>
    elements.map((element) => (element as HTMLInputElement).value))).toEqual(domains.map(({ value }) => value));
  await expect(page.locator('.bar-item:visible')).toHaveCount(Object.keys(vocabulary.concepts).length);
  await page.goto('/viz/concept-matrix/');
  await page.locator('#toggle-sparse').click();
  for (const domain of domains) {
    await page.locator('#domain-filter').selectOption(domain.value);
    await expect(page.locator(`#matrix-body tr[data-domain="${domain.value}"]:visible`))
      .toHaveCount(Object.values(vocabulary.concepts).filter((entry) => (entry.domain ?? 'root') === domain.value).length);
    await expect(page.locator(`#matrix-body tr[data-domain]:visible:not([data-domain="${domain.value}"])`)).toHaveCount(0);
    await expect(page.locator(`#matrix-body tr[data-sep-domain]:visible:not([data-sep-domain="${domain.value}"])`)).toHaveCount(0);
  }
  await page.goto('/viz/domain-ring/');
  expect(await page.locator('.sidebar-section').evaluateAll((elements) =>
    elements.map((element) => (element as HTMLElement).dataset.domain))).toEqual(domains.map(({ value }) => value));
  await page.goto('/viz/supertype-tree/');
  for (const domain of domains) await expect(page.locator('.legend')).toContainText(domain.filterLabel);
  await expect(page.locator('.node-link[href^="/concepts/"]')).toHaveCount(0);
});
