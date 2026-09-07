import { readdirSync, readFileSync } from 'node:fs';
import { extname, join, resolve } from 'node:path';
import type { APIRoute } from 'astro';

// A closed set of authored review examples. Files become static build assets;
// no request path is used to read the filesystem at runtime.
const exampleFolders = [
  'registry-pilots', 'farm-operators', 'government-domains',
  'agriculture-biology', 'agriculture-operations',
];
const decisions = ['020-registry-foundations.md', '021-farm-production-unit.md'];

export function getStaticPaths() {
  const root = resolve(process.cwd(), '..');
  const files = decisions.map((name) => `decisions/${name}`);
  for (const folder of exampleFolders) {
    const relative = `examples/${folder}`;
    for (const entry of readdirSync(join(root, relative), { withFileTypes: true })) {
      if (entry.isFile() && ['.json', '.py', '.md'].includes(extname(entry.name))) {
        files.push(`${relative}/${entry.name}`);
      }
    }
  }
  return files.map((path) => ({
    params: { path },
    props: {
      content: readFileSync(join(root, path), 'utf8'),
      contentType: path.endsWith('.json') ? 'application/json' : 'text/plain',
    },
  }));
}

export const GET: APIRoute = ({ props }) => new Response(props.content, {
  headers: { 'Content-Type': `${props.contentType}; charset=utf-8` },
});
