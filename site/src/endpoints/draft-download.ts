import { resolve } from 'node:path';
import type { APIRoute } from 'astro';
import { collectDraftDownloads, draftDownloadResponse } from '../data/draft-downloads';

// Load only the authored allowlist. A request never selects a filesystem path.
const downloads = new Map(collectDraftDownloads(resolve('..')).map(({ params, props }) =>
  [`/registry-draft/${params.path}`, props],
));

export const GET: APIRoute = ({ url }) => {
  const props = downloads.get(url.pathname);
  return props ? draftDownloadResponse(props) : new Response('Not found', { status: 404 });
};
