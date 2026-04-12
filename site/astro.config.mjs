// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { resolve } from 'node:path';

// https://astro.build/config
export default defineConfig({
  site: 'https://publicschema.org',
  trailingSlash: 'always',
  i18n: {
    locales: ['en', 'fr', 'es'],
    defaultLocale: 'en',
    routing: { prefixDefaultLocale: false },
  },
  integrations: [sitemap({
    i18n: {
      defaultLocale: 'en',
      locales: { en: 'en', fr: 'fr', es: 'es' },
    },
  })],
  vite: {
    resolve: {
      alias: {
        '@vocab-data': resolve('../dist/vocabulary.json'),
      },
    },
  },
});
