/**
 * Shared `getStaticPaths` factories. Dynamic pages in `src/pages/` (and the
 * locale wrappers under `src/pages/fr/`, `src/pages/es/`) re-export these so
 * they produce identical path lists in every locale.
 */
import { loadVocabulary } from './vocabulary';
import { buildSystemIndex } from './systems';
import { docs } from './docs';

export function getTermPaths() {
  const vocab = loadVocabulary();
  const paths = [];
  for (const [id, concept] of Object.entries(vocab.concepts)) {
    const slug = concept.path.replace(/^\//, '');
    paths.push({ params: { slug }, props: { kind: 'concept' as const, termId: id } });
  }
  for (const [id, prop] of Object.entries(vocab.properties)) {
    const slug = prop.path.replace(/^\//, '');
    paths.push({ params: { slug }, props: { kind: 'property' as const, termId: id } });
  }
  return paths;
}

export function getVocabPaths() {
  const vocab = loadVocabulary();
  return Object.keys(vocab.vocabularies).map((id) => ({ params: { vocab: id } }));
}

export function getSystemPaths() {
  const index = buildSystemIndex();
  return Object.keys(index).map((id) => ({ params: { system: id } }));
}

export function getDocPaths() {
  return Object.keys(docs).map((slug) => ({ params: { slug } }));
}
