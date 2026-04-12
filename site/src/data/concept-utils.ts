import type { VocabularyData, Property } from './vocabulary';

/** Look up a concept's path by ID. Falls back to `/{id}` if unknown. */
export function conceptPath(vocab: VocabularyData, id: string): string {
  return vocab.concepts[id]?.path || `/${id}`;
}

/** Look up a property's path by ID. Falls back to `/{id}` if unknown. */
export function propPath(vocab: VocabularyData, id: string): string {
  return vocab.properties[id]?.path || `/${id}`;
}

export interface InheritedProperty {
  id: string;
  detail: Property | undefined;
  from: string;
}

/**
 * Walk the full supertype chain and collect properties declared on ancestors.
 * Each property is attributed to the nearest ancestor that declares it.
 * Caller passes a set of IDs already seen (typically the concept's own
 * properties) so inherited entries don't duplicate own entries.
 */
export function collectInheritedProperties(
  vocab: VocabularyData,
  conceptId: string,
  seenIds: Set<string>,
  visited: Set<string> = new Set(),
): InheritedProperty[] {
  const result: InheritedProperty[] = [];
  const concept = vocab.concepts[conceptId];
  if (!concept) return result;
  for (const st of concept.supertypes) {
    if (visited.has(st)) continue;
    visited.add(st);
    const parent = vocab.concepts[st];
    if (!parent) continue;
    for (const ref of parent.properties) {
      if (!seenIds.has(ref.id)) {
        seenIds.add(ref.id);
        result.push({ id: ref.id, detail: vocab.properties[ref.id], from: st });
      }
    }
    result.push(...collectInheritedProperties(vocab, st, seenIds, visited));
  }
  return result;
}

/** Flat list of every subtype (direct and indirect) of a concept. */
export function collectAllSubtypes(vocab: VocabularyData, conceptId: string): string[] {
  const result: string[] = [];
  const visited = new Set<string>();
  function walk(id: string) {
    if (visited.has(id)) return;
    visited.add(id);
    const c = vocab.concepts[id];
    if (!c) return;
    for (const st of c.subtypes) {
      result.push(st);
      walk(st);
    }
  }
  walk(conceptId);
  return result;
}
