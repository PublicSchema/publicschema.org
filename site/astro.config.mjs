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
      },
    },
  },
});
