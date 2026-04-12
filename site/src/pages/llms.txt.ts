import { loadVocabulary } from '../data/vocabulary';
import { docs } from '../data/docs';

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

  lines.push('## Concepts');
  lines.push('');
  for (const c of concepts) {
    lines.push(`- [${c.id}](https://publicschema.org${c.path}): ${c.definition.en}`);
  }
  lines.push('');

  lines.push('## Properties');
  lines.push('');
  for (const p of properties) {
    lines.push(`- [${p.id}](https://publicschema.org${p.path}): ${p.definition.en}`);
  }
  lines.push('');

  lines.push('## Vocabularies');
  lines.push('');
  for (const [key, v] of vocabularies) {
    lines.push(`- [${v.id}](https://publicschema.org/vocab/${key}): ${v.definition.en}`);
  }
  lines.push('');

  lines.push('## Documentation');
  lines.push('');
  for (const [slug, doc] of Object.entries(docs)) {
    lines.push(`- [${doc.title.en}](https://publicschema.org/docs/${slug}/): ${doc.description.en}`);
  }
  lines.push('');

  lines.push('## Full content');
  lines.push('');
  lines.push('- [llms-full.txt](https://publicschema.org/llms-full.txt): Complete definitions for all concepts, properties, and vocabularies');
  lines.push('');

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
