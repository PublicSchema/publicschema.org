import { defaultLocale, type Locale } from '../i18n/languages';
import { useTranslations } from '../i18n/utils';
import type { VocabularyData } from './vocabulary';

interface DomainEntry {
  domain: string | null;
  id: string;
}

export interface DomainInfo {
  code: string | null;
  value: string;
  label: string;
  filterLabel: string;
  description: string;
  color: string;
}

const domainColors = [
  '#b54a1a', '#166534', '#6b21a8', '#0e7490', '#a21caf',
  '#854d0e', '#1d4ed8', '#9f1239', '#047857', '#4338ca',
];

/**
 * Authored metadata supplies labels and ordering. Lists contain only domains
 * present in the supplied entries, including codes absent from the metadata.
 * Historical exports retain their translated SP/CRVS labels and ordering.
 */
export function createDomainCatalog(
  vocabulary: Pick<VocabularyData, 'meta'>,
  locale: Locale = defaultLocale,
) {
  const t = useTranslations(locale);
  const metadata = vocabulary.meta.domains ?? {};
  const order = vocabulary.meta.domains ? Object.keys(metadata) : ['sp', 'crvs'];
  const rank = new Map(order.map((code, index) => [code, index]));
  const legacyLabels: Record<string, string> = {
    sp: t('concepts.section_social_protection'),
    crvs: t('concepts.section_crvs'),
  };

  function get(domain: string | null): DomainInfo {
    const code = domain && domain !== 'root' ? domain : null;
    const authored = code ? metadata[code] : undefined;
    const label = code
      ? authored?.label[locale] ?? authored?.label.en ?? legacyLabels[code] ?? code
      : t('browse.domain_universal');
    const colorIndex = code
      ? rank.get(code) ?? Array.from(code).reduce((sum, char) => sum + char.charCodeAt(0), 0)
      : 0;
    return {
      code,
      value: code ?? 'root',
      label,
      filterLabel: code && label !== code ? `${code} (${label})` : label,
      description: authored?.description?.[locale] ?? authored?.description?.en ?? '',
      color: code ? domainColors[colorIndex % domainColors.length] : '#1e3a5f',
    };
  }

  function compareDomains(a: string | null, b: string | null): number {
    const aCode = get(a).code;
    const bCode = get(b).code;
    if (aCode === bCode) return 0;
    if (!aCode) return -1;
    if (!bCode) return 1;
    return (rank.get(aCode) ?? order.length) - (rank.get(bCode) ?? order.length)
      || aCode.localeCompare(bCode);
  }

  return {
    get,
    compare(a: DomainEntry, b: DomainEntry): number {
      return compareDomains(a.domain, b.domain) || a.id.localeCompare(b.id);
    },
    present(entries: Iterable<Pick<DomainEntry, 'domain'>>): DomainInfo[] {
      const codes = new Set(Array.from(entries, (entry) => get(entry.domain).code));
      return Array.from(codes).sort(compareDomains).map(get);
    },
  };
}
