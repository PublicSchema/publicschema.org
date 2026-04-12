import { loadVocabulary } from './vocabulary';
import { docs } from './docs';
import { defaultLocale, type Locale } from '../i18n/languages';
import { useTranslations } from '../i18n/utils';

export interface SearchDocument {
  id: string;
  type: string;
  title: string;
  body: string;
  path: string;
  meta: string;
  keywords: string;
}

function truncate(text: string, maxLength: number): string {
  const trimmed = text.trim().replace(/\n/g, ' ');
  if (trimmed.length <= maxLength) return trimmed;
  return trimmed.slice(0, maxLength).trimEnd() + '...';
}

/**
 * Pick a multilingual string for the given locale, falling back to English.
 * The fallback keeps entries searchable even when a translation is missing,
 * which matters for vocabulary value labels and newer concept definitions.
 */
function pick(value: { en?: string; fr?: string; es?: string } | undefined, locale: Locale): string {
  if (!value) return '';
  return value[locale] ?? value[defaultLocale] ?? '';
}

/**
 * Build the searchable document list in the requested locale. Concept,
 * property, and vocabulary IDs stay canonical (English identifiers) so a
 * user on the French site can still find "Person" by typing either the
 * canonical name or its localized definition text.
 */
export function buildSearchIndex(locale: Locale = defaultLocale): SearchDocument[] {
  const vocab = loadVocabulary();
  const t = useTranslations(locale);
  const documents: SearchDocument[] = [];

  for (const concept of Object.values(vocab.concepts)) {
    documents.push({
      id: `concept:${concept.id}`,
      type: 'concept',
      title: concept.id,
      body: truncate(pick(concept.definition, locale), 200),
      path: concept.path,
      meta: concept.domain ? `Domain: ${concept.domain}` : '',
      keywords: concept.properties.map((p) => p.id).join(' '),
    });
  }

  for (const prop of Object.values(vocab.properties)) {
    const usedByList = prop.used_by || [];
    documents.push({
      id: `property:${prop.id}`,
      type: 'property',
      title: prop.id,
      body: truncate(pick(prop.definition, locale), 200),
      path: prop.path,
      meta: usedByList.length > 0 ? `Used by: ${usedByList.join(', ')}` : '',
      keywords: usedByList.join(' '),
    });
  }

  for (const v of Object.values(vocab.vocabularies)) {
    const valueLabels: string[] = [];
    if (!v.external_values) {
      for (const val of v.values) {
        const label = pick(val.label, locale);
        if (label) valueLabels.push(label);
      }
    }
    const valueCount = v.values.length;
    documents.push({
      id: `vocab:${v.id}`,
      type: 'vocabulary',
      title: v.id,
      body: truncate(pick(v.definition, locale), 200),
      path: `/vocab/${v.id}`,
      meta: `${valueCount} values`,
      keywords: valueLabels.join('\t'),
    });
  }

  for (const [slug, doc] of Object.entries(docs)) {
    documents.push({
      id: `doc:${slug}`,
      type: 'doc',
      title: doc.title[locale] ?? doc.title.en,
      body: truncate(doc.description[locale] ?? doc.description.en, 200),
      path: `/docs/${slug}/`,
      meta: t(`docs.category.${doc.category}`),
      keywords: '',
    });
  }

  return documents;
}
