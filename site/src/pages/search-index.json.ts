import { buildSearchIndex } from '../data/search-index';

export function GET() {
  return new Response(JSON.stringify(buildSearchIndex('en')), {
    headers: { 'Content-Type': 'application/json' },
  });
}
