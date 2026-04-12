import { buildSearchIndex } from '../../data/search-index';

export function GET() {
  return new Response(JSON.stringify(buildSearchIndex('es')), {
    headers: { 'Content-Type': 'application/json' },
  });
}
