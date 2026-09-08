import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { gzipSync, gunzipSync } from 'node:zlib';
import { expect, test } from '@playwright/test';
import type { APIContext } from 'astro';
import { Marked } from 'marked';
import { docs, implementationGuideSlugs } from '../src/data/docs';
import { collectDraftDownloads, draftContentType, draftDownloadResponse, draftDownloadUrl } from '../src/data/draft-downloads';
import { documentationLink, rewriteDocumentationLinks } from '../src/data/document-links';
import { GET } from '../src/endpoints/draft-download';

const authoredRoutes = () => collectDraftDownloads(resolve(process.cwd(), '..'));

test('draft downloads exclude unlisted files, caches and symlinks', () => {
  const root = mkdtempSync(join(tmpdir(), 'publicschema-draft-downloads-'));
  try {
    const put = (path: string, content = '{}') => {
      mkdirSync(dirname(join(root, path)), { recursive: true });
      writeFileSync(join(root, path), content);
    };
    put('examples/fhir-registry/bundle.fhir.json');
    put('examples/fhir-registry/artifacts/manifest.json');
    put('examples/fhir-registry/private.json');
    put('examples/fhir-registry/__pycache__/validate.py');
    put('examples/fhir-registry/artifacts/cache/package.json');
    put('private/records.json');
    symlinkSync(join(root, 'private/records.json'), join(root, 'examples/fhir-registry/registry-links.json'));
    symlinkSync(join(root, 'private'), join(root, 'examples/facility-roles'));

    const routes = collectDraftDownloads(root);
    expect(routes.map(({ params }) => params.path).sort()).toEqual([
      'examples/fhir-registry/artifacts/index.html',
      'examples/fhir-registry/artifacts/manifest.json',
      'examples/fhir-registry/bundle.fhir.json',
      'examples/fhir-registry/index.html',
    ]);
    const directory = routes.find(({ params }) => params.path === 'examples/fhir-registry/index.html')!;
    expect(directory.props.content).toContain('href="/registry-draft/examples/fhir-registry/artifacts/index.html"');
    expect(directory.props.content).toContain('href="/registry-draft/examples/fhir-registry/bundle.fhir.json"');
    expect(directory.props.content).not.toContain('private');
    expect(directory.props.content).not.toContain('__pycache__');
    expect(draftDownloadUrl('examples/fhir-registry/private.json')).toBeUndefined();
    expect(draftDownloadUrl('../private/records.json')).toBeUndefined();
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('draft endpoint preserves official archive bytes, media types and provenance downloads', async () => {
  const root = resolve(process.cwd(), '..');
  const routes = authoredRoutes();
  const responseFor = async (path: string) => {
    const route = routes.find(({ params }) => params.path === path);
    expect(route, path).toBeDefined();
    return GET({ url: new URL(`/registry-draft/${path}`, 'http://localhost') } as APIContext);
  };
  for (const filename of ['base-profiles.zip', 'fhir.schema.json.zip']) {
    const path = `examples/fhir-registry/artifacts/${filename}`;
    const response = await responseFor(path);
    expect(response.headers.get('Content-Type')).toBe('application/zip');
    expect(response.headers.get('Content-Disposition')).toBe(`attachment; filename="${filename}"`);
    const source = readFileSync(join(root, path));
    const result = Buffer.from(await response.arrayBuffer());
    expect(createHash('sha256').update(result).digest('hex'))
      .toBe(createHash('sha256').update(source).digest('hex'));
  }
  expect((await responseFor('examples/fhir-registry/bundle.fhir.json')).headers.get('Content-Type'))
    .toBe('application/fhir+json; charset=utf-8');
  expect((await responseFor('examples/fhir-registry/artifacts/README.md')).headers.get('Content-Type'))
    .toBe('text/plain; charset=utf-8');
  expect((await responseFor('examples/fhir-registry/artifacts/manifest.json')).headers.get('Content-Type'))
    .toBe('application/json; charset=utf-8');

  const gzip = gzipSync('binary-safe gzip content');
  const response = draftDownloadResponse({
    content: Uint8Array.from(gzip).buffer,
    contentType: draftContentType('artifact.json.gz'),
    filename: 'artifact.json.gz',
  });
  expect(response.headers.get('Content-Type')).toBe('application/gzip');
  expect(gunzipSync(Buffer.from(await response.arrayBuffer())).toString()).toBe('binary-safe gzip content');
  expect((await GET({ url: new URL('/registry-draft/private.json', 'http://localhost') } as APIContext)).status)
    .toBe(404);
});

test('served draft downloads resolve at their file URLs without a trailing slash', async ({ request }) => {
  for (const { params } of authoredRoutes()) {
    const response = await request.get(`/registry-draft/${params.path}`);
    expect(response.status(), params.path).toBe(200);
    if (params.path.endsWith('.zip') || params.path.endsWith('.fhir.json')) {
      const source = readFileSync(resolve(process.cwd(), '..', params.path));
      expect(createHash('sha256').update(await response.body()).digest('hex'), params.path)
        .toBe(createHash('sha256').update(source).digest('hex'));
    }
  }
  expect((await request.get('/registry-draft/examples/fhir-registry/private.json')).status()).toBe(404);
});

test('guide links resolve declared downloads before locale prefixes', () => {
  for (const locale of ['en', 'fr', 'es'] as const) {
    const source = 'docs/fhir-registry-integration.md';
    expect(documentationLink('../examples/fhir-registry/', source, locale))
      .toBe('/registry-draft/examples/fhir-registry/index.html');
    expect(documentationLink('../examples/fhir-registry/artifacts/', source, locale))
      .toBe('/registry-draft/examples/fhir-registry/artifacts/index.html');
    expect(documentationLink('../examples/fhir-registry/artifacts/fhir.schema.json.zip', source, locale))
      .toBe('/registry-draft/examples/fhir-registry/artifacts/fhir.schema.json.zip');
    expect(documentationLink('../examples/domain-migration/uri-map.json', source, locale))
      .toBe('/registry-draft/examples/domain-migration/uri-map.json');
    expect(documentationLink('../decisions/025-domain-and-external-model-boundaries.md#decision', source, locale))
      .toBe('/registry-draft/decisions/025-domain-and-external-model-boundaries.md#decision');
    expect(documentationLink('../CONTRIBUTING.md', source, locale))
      .toBe('https://github.com/PublicSchema/publicschema.org/blob/main/CONTRIBUTING.md');
    expect(documentationLink('../../examples/facility-roles/records.json', 'docs/fr/facility-roles.md', locale))
      .toBe('/registry-draft/examples/facility-roles/records.json');
    expect(documentationLink('/registry-draft/examples/public-services/records.json', source, locale))
      .toBe('/registry-draft/examples/public-services/records.json');
    expect(documentationLink('../examples/fhir-registry/private.json', source, locale))
      .toBe('../examples/fhir-registry/private.json');
    expect(documentationLink('https://hl7.org/fhir/R5/', source, locale)).toBe('https://hl7.org/fhir/R5/');
    expect(documentationLink('//hl7.org/fhir/R5/', source, locale)).toBe('//hl7.org/fhir/R5/');
    const prefix = locale === 'en' ? '' : `/${locale}`;
    expect(documentationLink('facility-roles.md#roles', 'docs/domain-migration.md', locale))
      .toBe(`${prefix}/docs/facility-roles/#roles`);
    expect(documentationLink('facility-roles.md', 'docs/fr/domain-migration.md', locale))
      .toBe(`${prefix}/docs/facility-roles/`);
    expect(documentationLink('../handbook/introduction.md', 'docs/handbook/worked-example.md', locale))
      .toBe(`${prefix}/handbook/introduction/`);
  }
  expect(rewriteDocumentationLinks('<a href="/docs/schema-design/?q=dates#period">Dates</a>', 'docs/facility-roles.md', 'fr'))
    .toBe('<a href="/fr/docs/schema-design/?q=dates#period">Dates</a>');
});

test('all new authored guide downloads resolve to published routes', async () => {
  const publishedPaths = new Set(authoredRoutes().map(({ params }) => `/registry-draft/${params.path}`));
  const renderer = new Marked();
  for (const slug of implementationGuideSlugs) {
    const sourcePath = `docs/${docs[slug].file}`;
    const raw = readFileSync(resolve(process.cwd(), '..', sourcePath), 'utf8');
    for (const locale of ['en', 'fr', 'es'] as const) {
      const html = rewriteDocumentationLinks(await renderer.parse(raw), sourcePath, locale);
      const links = Array.from(html.matchAll(/href="([^"]*)"/g), (match) => match[1]);
      for (const link of links) {
        expect(link, `${slug}: ${link}`).not.toMatch(/^\.\.?\//);
        expect(link, `${slug}: ${link}`).not.toMatch(/^[^/#:]+\.md(?:#|$)/);
        if (link.startsWith('/registry-draft/')) {
          expect(publishedPaths.has(link.split(/[?#]/)[0]), `${slug}: ${link}`).toBe(true);
        }
      }
    }
  }
});
