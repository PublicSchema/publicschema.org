import { existsSync, lstatSync, readFileSync, realpathSync } from 'node:fs';
import { basename, extname, join } from 'node:path';

// Only these authored files are published. Never walk example subdirectories:
// validator caches, temporary output and unlisted files remain local.
const exampleFiles: Record<string, string[]> = {
  'registry-pilots': ['records.json', 'profile.py'],
  'farm-operators': ['records.json', 'work-records.json', 'validate_profile.py'],
  'government-domains': ['records.json'],
  'agriculture-biology': ['records.json', 'movement-records.json', 'validate_movement_profile.py'],
  'agriculture-operations': [
    'README.md',
    'apiary.json', 'applicator.json', 'aquaculture.json', 'certification.json',
    'component.json', 'facility.json', 'feed.json', 'fertilizer.json',
    'irrigation.json', 'laboratory.json', 'livestock.json', 'machinery.json',
    'membership-organization.json', 'membership-person.json', 'nursery.json',
    'pesticide.json', 'producer-organization.json', 'product.json',
    'seed-operator.json', 'service-role.json', 'supplier.json', 'vessel.json',
    'water.json',
  ],
  'facility-roles': ['records.json', 'validate_profile.py'],
  'fhir-registry': ['README.md', 'bundle.fhir.json', 'registry-links.json', 'validate.py', 'official_validate.py'],
  'fhir-registry/artifacts': ['README.md', 'manifest.json', 'base-profiles.zip', 'fhir.schema.json.zip'],
  'government-relationships': ['records.json', 'negative-cases.json', 'validate_profile.py'],
  'public-services': ['records.json', 'profile.json', 'profile.py'],
  'relationship-date-migration': ['legacy-records.json', 'records.json', 'migrate.py'],
  'domain-migration': ['uri-map.json'],
};

const decisionFiles = [
  '020-registry-foundations.md',
  '021-farm-production-unit.md',
  '023-public-services-and-administrative-history.md',
  '024-government-qualified-relationships.md',
  '025-domain-and-external-model-boundaries.md',
];

const files = new Set([
  ...Object.entries(exampleFiles).flatMap(([folder, names]) =>
    names.map((name) => `examples/${folder}/${name}`)),
  ...decisionFiles.map((name) => `decisions/${name}`),
]);
const directories = new Set([
  ...Object.keys(exampleFiles).map((folder) => `examples/${folder}`),
  'decisions',
]);

export const guideExampleFolders: Record<string, string> = {
  'domain-migration': 'domain-migration',
  'fhir-registry-integration': 'fhir-registry',
  'facility-roles': 'facility-roles',
  'relationship-date-migration': 'relationship-date-migration',
  'public-services-draft': 'public-services',
  'government-relationships-draft': 'government-relationships',
};

/** Return a public URL only for a declared file or its directory index. */
export function draftDownloadUrl(repositoryPath: string): string | undefined {
  const path = repositoryPath.replace(/\/$/, '');
  if (files.has(path)) return `/registry-draft/${path}`;
  if (directories.has(path)) return `/registry-draft/${path}/index.html`;
  return undefined;
}

export function draftContentType(path: string): string {
  if (path.endsWith('.fhir.json')) return 'application/fhir+json; charset=utf-8';
  if (extname(path) === '.json') return 'application/json; charset=utf-8';
  if (extname(path) === '.zip') return 'application/zip';
  if (extname(path) === '.gz') return 'application/gzip';
  return 'text/plain; charset=utf-8';
}

export interface DraftDownloadProps {
  content: ArrayBuffer | string;
  contentType: string;
  filename?: string;
}

interface DraftDownloadRoute {
  params: { path: string };
  props: DraftDownloadProps;
}

function directoryIndex(directory: string, publishedFiles: string[]): string {
  const children = new Set(publishedFiles
    .filter((path) => path.startsWith(`${directory}/`))
    .map((path) => path.slice(directory.length + 1).split('/')[0]));
  const links = Array.from(children).sort().map((name) => {
    const path = `${directory}/${name}`;
    return `<li><a href="${draftDownloadUrl(path)}">${name}${directories.has(path) ? '/' : ''}</a></li>`;
  }).join('\n');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>${directory} | PublicSchema draft downloads</title></head>
<body><main><h1>PublicSchema draft downloads</h1><p><code>${directory}</code></p><ul>${links}</ul></main></body></html>`;
}

/** Read the allowlist at build time. Request paths never reach the filesystem. */
export function collectDraftDownloads(root: string): DraftDownloadRoute[] {
  const canonicalRoot = realpathSync(root);
  const publishedFiles = Array.from(files).filter((path) => {
    const absolute = join(canonicalRoot, path);
    return existsSync(absolute) && lstatSync(absolute).isFile()
      && realpathSync(absolute) === absolute;
  });
  const routes: DraftDownloadRoute[] = publishedFiles.map((path) => ({
    params: { path },
    props: {
      content: Uint8Array.from(readFileSync(join(canonicalRoot, path))).buffer,
      contentType: draftContentType(path),
      filename: ['.zip', '.gz'].includes(extname(path)) ? basename(path) : undefined,
    },
  }));
  for (const directory of directories) {
    if (!publishedFiles.some((path) => path.startsWith(`${directory}/`))) continue;
    routes.push({
      params: { path: `${directory}/index.html` },
      props: { content: directoryIndex(directory, publishedFiles), contentType: 'text/html; charset=utf-8' },
    });
  }
  return routes;
}

export function draftDownloadResponse(props: DraftDownloadProps): Response {
  return new Response(props.content, {
    headers: {
      'Content-Type': props.contentType,
      'X-Content-Type-Options': 'nosniff',
      ...(props.filename ? { 'Content-Disposition': `attachment; filename="${props.filename}"` } : {}),
    },
  });
}
