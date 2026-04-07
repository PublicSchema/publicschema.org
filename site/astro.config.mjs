// @ts-check
import { defineConfig } from 'astro/config';
import { resolve } from 'node:path';

// https://astro.build/config
export default defineConfig({
  site: 'https://publicschema.org',
  vite: {
    resolve: {
      alias: {
        '@vocab-data': resolve('../dist/vocabulary.json'),
      },
    },
  },
});
