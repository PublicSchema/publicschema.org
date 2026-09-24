import { readFileSync } from 'node:fs';
import { test, expect } from '@playwright/test';
import { createDomainCatalog } from '../src/data/domains';
import { localePath, useTranslations } from '../src/i18n/utils';
import type { VocabularyData } from '../src/data/vocabulary';
import type { Locale } from '../src/i18n/languages';

const vocabulary = JSON.parse(
  readFileSync(new URL('../../dist/vocabulary.json', import.meta.url), 'utf8'),
) as VocabularyData;

const concepts = Object.values(vocabulary.concepts);

for (const locale of ['en', 'fr', 'es'] as Locale[]) {
  test(`${locale} home lists the core and every sector domain with counts and maturity`, async ({ page }) => {
    const t = useTranslations(locale);
    const catalog = createDomainCatalog(vocabulary, locale);
    const domains = catalog.present(concepts);
    await page.goto(localePath('/', locale));

    const cards = page.locator('.h3-domain');
    await expect(cards).toHaveCount(domains.length);
    for (const [i, domain] of domains.entries()) {
      const card = cards.nth(i);
      const members = concepts.filter((c) => catalog.get(c.domain ?? null).value === domain.value);
      if (domain.code) {
        await expect(card.locator('h3')).toHaveText(domain.label);
        expect(domain.label, `domain ${domain.value} needs an authored label`).not.toBe(domain.value);
        await expect(card.locator('> p')).toHaveText(domain.description);
        if (locale !== 'en') {
          const english = createDomainCatalog(vocabulary, 'en').get(domain.code).description;
          expect(domain.description, `domain ${domain.value} needs a ${locale} description`).not.toBe(english);
        }
      } else {
        await expect(card.locator('h3')).toHaveText(t('home.domain_core'));
      }
      await expect(card.locator('.h3-domain-count')).toHaveText(String(members.length));
      await expect(card.locator('a.h3-domain-header'))
        .toHaveAttribute('href', `${localePath('/concepts/', locale)}?domain=${encodeURIComponent(domain.value)}`);

      const badgeTotal = await card.locator('.h3-domain-maturity .badge').evaluateAll((els) =>
        els.reduce((sum, el) => sum + Number.parseInt(el.textContent ?? '0', 10), 0));
      expect(badgeTotal).toBe(members.length);
    }
  });

  test(`${locale} home evidence section lists the same systems as the systems index, by name`, async ({ page }) => {
    await page.goto(localePath('/systems/', locale));
    const indexed = await page.locator('main table a[href*="/systems/"]').evaluateAll((els) =>
      els.map((el) => el.getAttribute('href')));
    const ids = indexed.map((href) => href!.split('/').filter(Boolean).pop());
    expect(ids.length).toBeGreaterThan(0);

    await page.goto(localePath('/', locale));
    const links = page.locator('.h3-systems a.h3-system');
    const hrefs = await links.evaluateAll((els) => els.map((el) => el.getAttribute('href')));
    expect(new Set(hrefs)).toEqual(new Set(indexed));
    for (const text of await links.allTextContents()) {
      expect(ids, `system "${text}" renders its raw id`).not.toContain(text.trim());
    }
  });

  test(`${locale} home internal links all resolve`, async ({ page, request }) => {
    await page.goto(localePath('/', locale));
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

test('fr home draft badges use the same term as the maturity docs', async ({ page }) => {
  await page.goto('/fr/');
  await expect(page.locator('.h3-domain .badge-draft').first()).toContainText('Brouillon');
});

test('en home closing line sits close under the personas with a single divider', async ({ page }) => {
  await page.goto('/');
  const personas = await page.locator('.h3-personas').boundingBox();
  const closing = await page.locator('.h3-closing').boundingBox();
  expect(closing!.y - (personas!.y + personas!.height)).toBeLessThanOrEqual(120);

  const dividers = await page.locator('.h3-closing').evaluate((el) =>
    [el, el.parentElement!].filter((node) => getComputedStyle(node).borderTopStyle !== 'none').length);
  expect(dividers).toBe(1);
});

test('en home personas point to handbook paths', async ({ page }) => {
  await page.goto('/');
  const hrefs = await page.locator('.h3-persona-links a').evaluateAll((els) =>
    els.map((el) => el.getAttribute('href')));
  expect(hrefs.filter((h) => h?.startsWith('/handbook/')).length).toBeGreaterThanOrEqual(4);
});
