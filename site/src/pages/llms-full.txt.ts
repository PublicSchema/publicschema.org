import { loadVocabulary } from '../data/vocabulary';
import { docs } from '../data/docs';
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

export function GET() {
  const vocab = loadVocabulary();
  const concepts = Object.values(vocab.concepts);
  const properties = Object.values(vocab.properties);
  const vocabularies = Object.entries(vocab.vocabularies);

  const lines: string[] = [];

  lines.push('# PublicSchema');
  lines.push('');
  lines.push('> Common definitions for public service delivery. An open, composable vocabulary of concepts and properties for public services. Think schema.org, but for public service delivery.');
  lines.push('');
  lines.push('PublicSchema provides shared definitions so that programs serving the same people can coordinate, share data, and interoperate. It defines concepts (Person, Household, Enrollment, etc.), their properties, and controlled vocabularies with value-level mappings across 6 major systems (OpenSPP, openIMIS, DCI, DHIS2, FHIR R4, OpenCRVS).');
  lines.push('');
  lines.push('Everything is optional and descriptive, not prescriptive. Systems adopt what they need.');
  lines.push('');
  lines.push('Base URI: https://publicschema.org');
  lines.push(`Version: ${vocab.meta.version}`);
  lines.push('');

  // --- Concepts ---
  lines.push('---');
  lines.push('');
  lines.push('## Concepts');
  lines.push('');

  for (const c of concepts) {
    lines.push(`### ${c.id}`);
    lines.push('');
    lines.push(`URI: ${c.uri}`);
    if (c.domain) lines.push(`Domain: ${c.domain}`);
    lines.push(`Maturity: ${c.maturity}`);
    if (c.abstract) lines.push('Abstract: yes');
    lines.push('');
    lines.push(c.definition.en ?? '');
    lines.push('');

    if (c.supertypes.length > 0) {
      lines.push(`Inherits from: ${c.supertypes.join(', ')}`);
    }
    if (c.subtypes.length > 0) {
      lines.push(`Subtypes: ${c.subtypes.join(', ')}`);
    }

    if (c.properties.length > 0) {
      lines.push('');
      lines.push('Properties:');
      for (const ref of c.properties) {
        const prop = vocab.properties[ref.id];
        if (prop) {
          const def = prop.definition.en ?? '';
          const short = def.length > 120 ? def.slice(0, 120) + '...' : def;
          lines.push(`- ${ref.id} (${prop.type}): ${short}`);
        } else {
          lines.push(`- ${ref.id}`);
        }
      }
    }

    if (c.convergence) {
      lines.push('');
      lines.push(`Convergence: present in ${c.convergence.system_count} of ${c.convergence.total_systems} mapped systems.`);
      if (c.convergence.notes) lines.push(c.convergence.notes);
    }

    lines.push('');
  }

  // --- Properties ---
  lines.push('---');
  lines.push('');
  lines.push('## Properties');
  lines.push('');

  for (const p of properties) {
    lines.push(`### ${p.id}`);
    lines.push('');
    lines.push(`URI: ${p.uri}`);
    lines.push(`Type: ${p.type}`);
    lines.push(`Cardinality: ${p.cardinality}`);
    lines.push(`Maturity: ${p.maturity}`);
    if (p.vocabulary) lines.push(`Vocabulary: ${p.vocabulary}`);
    if (p.references) lines.push(`References: ${p.references}`);
    lines.push('');
    lines.push(p.definition.en ?? '');
    lines.push('');

    if (p.used_by.length > 0) {
      lines.push(`Used by: ${p.used_by.join(', ')}`);
    }

    if (p.convergence) {
      lines.push(`Convergence: present in ${p.convergence.system_count} of ${p.convergence.total_systems} mapped systems.`);
      if (p.convergence.notes) lines.push(p.convergence.notes);
    }

    lines.push('');
  }

  // --- Vocabularies ---
  lines.push('---');
  lines.push('');
  lines.push('## Vocabularies');
  lines.push('');

  for (const [key, v] of vocabularies) {
    lines.push(`### ${v.id}`);
    lines.push('');
    lines.push(`URI: ${v.uri}`);
    if (v.domain) lines.push(`Domain: ${v.domain}`);
    lines.push(`Maturity: ${v.maturity}`);
    if (v.standard) {
      lines.push(`Standard: ${v.standard.name}${v.standard.uri ? ' (' + v.standard.uri + ')' : ''}`);
      if (v.standard.notes) lines.push(`Notes: ${v.standard.notes}`);
    }
    lines.push('');
    lines.push(v.definition.en ?? '');
    lines.push('');

    if (v.external_values) {
      lines.push('Values are maintained by the referenced standard (not listed inline).');
    } else if (v.values.length > 0) {
      lines.push('Values:');
      for (const val of v.values) {
        const label = val.label.en ?? val.code;
        const def = val.definition.en ?? '';
        const stdCode = val.standard_code ? ` [${val.standard_code}]` : '';
        lines.push(`- ${val.code}${stdCode}: ${label}. ${def}`);
      }
    }

    lines.push('');
  }

  // --- Documentation ---
  lines.push('---');
  lines.push('');
  lines.push('## Documentation');
  lines.push('');

  const docsDir = resolve(process.cwd(), '../docs');
  for (const [slug, doc] of Object.entries(docs)) {
    lines.push(`### ${doc.title.en}`);
    lines.push('');
    lines.push(`URL: https://publicschema.org/docs/${slug}/`);
    lines.push('');

    const docPath = resolve(docsDir, doc.file);
    if (existsSync(docPath)) {
      let content = readFileSync(docPath, 'utf-8');
      // Strip the leading H1 (redundant with our heading above)
      content = content.replace(/^#\s+.+\n+/, '');
      lines.push(content.trim());
    } else {
      lines.push(doc.description.en);
    }

    lines.push('');
    lines.push('');
  }

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
