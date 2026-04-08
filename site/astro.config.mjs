// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { resolve } from 'node:path';

// https://astro.build/config
export default defineConfig({
  site: 'https://publicschema.org',
  integrations: [sitemap()],
  vite: {
    resolve: {
      alias: {
        '@vocab-data': resolve('../dist/vocabulary.json'),
      },
    },
  },
});
