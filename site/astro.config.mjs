// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { resolve } from 'node:path';
import { collectDraftDownloads } from './src/data/draft-downloads';

// https://astro.build/config
export default defineConfig({
  site: 'https://publicschema.org',
  trailingSlash: 'always',
  i18n: {
    locales: ['en', 'fr', 'es'],
    defaultLocale: 'en',
    routing: { prefixDefaultLocale: false },
  },
  integrations: [{
    name: 'draft-downloads',
    hooks: {
      'astro:config:setup': ({ injectRoute }) => {
        // Explicit file routes keep their extensions in Astro's route manifest.
        // A catch-all endpoint instead inherits the page trailing-slash rule.
        for (const { params } of collectDraftDownloads(resolve('..'))) {
          injectRoute({
            pattern: `/registry-draft/${params.path}`,
            entrypoint: './src/endpoints/draft-download.ts',
          });
        }
      },
    },
  }, sitemap({
    filter: (page) => !page.includes('/viz/'),
    i18n: {
      defaultLocale: 'en',
      locales: { en: 'en', fr: 'fr', es: 'es' },
    },
    serialize(item) {
      if (item.links?.length && !item.links.some((l) => l.lang === 'x-default')) {
        const enLink = item.links.find((l) => l.lang === 'en');
        if (enLink) {
          item.links.push({ lang: 'x-default', url: enLink.url });
        }
      }
      return item;
    },
  })],
  vite: {
    resolve: {
      alias: {
        '@vocab-data': resolve('../dist/vocabulary.json'),
        '@system-matchings': resolve('../dist/system_matchings.json'),
        '@metrics-data': resolve('../dist/metrics_catalog.json'),
      },
    },
  },
});
