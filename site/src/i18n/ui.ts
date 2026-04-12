import type { Locale } from './languages';

/**
 * UI string dictionary. English is the source of truth; French and Spanish
 * are filled during Phase 2 translation work. Missing keys fall back to
 * English via the `t()` function.
 *
 * Long prose pages (homepage, about, terms, types) are not stored here:
 * they use locale-specific Astro content components. This dictionary is for
 * chrome, navigation, and reusable UI labels.
 */
const en = {
  // Navigation and chrome
  'nav.concepts': 'Concepts',
  'nav.properties': 'Properties',
  'nav.vocabularies': 'Vocabularies',
  'nav.docs': 'Docs',
  'nav.about': 'About',
  'nav.menu': 'Menu',
  'nav.search': 'Search',

  // Language switcher
  'lang.switch_to': 'Switch language to {language}',
  'lang.current': 'Current language: {language}',

  // Search UI
  'search.placeholder': 'Search concepts, properties...',
  'search.min_chars': 'Type at least 2 characters to search',
  'search.no_results': 'No results for',
  'search.browse_hint': 'Browse: Concepts, Properties, Vocabularies',
  'search.results_status': '{count} result(s) found',
  'search.no_results_status': 'No results found',
  'search.aria_label': 'Search PublicSchema',

  // Footer
  'footer.tagline': 'Common definitions for public service delivery. Built so programs can coordinate, share data, and reach the people they serve.',
  'footer.explore': 'Explore',
  'footer.docs': 'Docs',
  'footer.project': 'Project',
  'footer.use_cases': 'Use Cases',
  'footer.extension_mechanism': 'Extension Mechanism',
  'footer.all_docs': 'All documentation',
  'footer.systems': 'Systems',
  'footer.about': 'About',
  'footer.source_github': 'Source on GitHub',
  'footer.terms': 'Terms and License',
  'footer.reference_model_cc': 'Reference model:',
  'footer.code_apache': 'Code:',
  'footer.built_with': 'Built with',

  // Breadcrumbs and shared labels
  'breadcrumb.home': 'Home',
  'common.concepts': 'Concepts',
  'common.properties': 'Properties',
  'common.vocabularies': 'Vocabularies',
  'common.systems': 'Systems',
  'common.data_types': 'Data Types',

  // Concepts index
  'concepts.page_title': 'Concepts',
  'concepts.page_subtitle': 'The core entities that appear across public service delivery systems.',
  'concepts.section_core': 'Core',
  'concepts.section_social_protection': 'Social Protection',
  'concepts.table.concept': 'Concept',
  'concepts.table.definition': 'Definition',
  'concepts.table.maturity': 'Maturity',

  // Properties index
  'properties.page_title': 'Properties',
  'properties.page_subtitle': 'Reusable attributes shared across concepts.',
  'properties.table.property': 'Property',
  'properties.table.type': 'Type',
  'properties.table.used_by': 'Used by',
  'properties.table.definition': 'Definition',

  // Vocabularies index
  'vocab.page_title': 'Vocabularies',
  'vocab.page_subtitle': 'Controlled value sets, referencing international standards where they exist.',
  'vocab.table.vocabulary': 'Vocabulary',
  'vocab.table.values': 'Values',
  'vocab.table.standard': 'Standard',
  'vocab.table.definition': 'Definition',

  // Vocabulary detail
  'vocab_detail.standard_reference': 'Standard reference',
  'vocab_detail.aligned_standards': 'Aligned standards',
  'vocab_detail.values': 'Values',
  'vocab_detail.external_values_note_prefix': 'This vocabulary is defined by an external standard',
  'vocab_detail.external_values_note_suffix': 'The full list of values is available in the downloads above',
  'vocab_detail.official_standard_page': 'official standard page',
  'vocab_detail.table.code': 'Code',
  'vocab_detail.table.label': 'Label',
  'vocab_detail.table.standard_code': 'Standard code',
  'vocab_detail.table.definition': 'Definition',
  'vocab_detail.same_standard': 'Same standard',
  'vocab_detail.same_standard_desc_prefix': 'The following systems use the same underlying standard',
  'vocab_detail.same_standard_desc_suffix': 'for this vocabulary, so values are directly compatible without mapping:',
  'vocab_detail.system_mappings': 'System mappings',
  'vocab_detail.system_vocabulary': 'System vocabulary:',
  'vocab_detail.no_mapping': 'no equivalent',
  'vocab_detail.not_covered_by': 'Not covered by {system}:',

  // Systems index
  'systems.page_title': 'Systems',
  'systems.page_subtitle': 'External systems and standards with vocabulary mappings to PublicSchema canonical values.',
  'systems.table.system': 'System',
  'systems.table.vocabularies': 'Vocabularies',
  'systems.table.value_mappings': 'Value mappings',
  'systems.table.same_standard': 'Same standard',
  'systems.table.status': 'Status',

  // System detail
  'system_detail.vocabularies': 'Vocabularies',
  'system_detail.properties': 'Properties',
  'system_detail.table.vocabulary': 'Vocabulary',
  'system_detail.table.system_name': 'System name',
  'system_detail.table.relationship': 'Relationship',
  'system_detail.table.coverage': 'Coverage',
  'system_detail.table.gaps': 'Gaps',
  'system_detail.relationship_same_standard': 'Same standard',
  'system_detail.relationship_value_mapping': 'Value mapping',
  'system_detail.coverage_all': 'All values',
  'system_detail.coverage_mapped': '{mapped}/{total} mapped',
  'system_detail.not_covered': '{count} not covered',
  'system_detail.report_button': 'Report an issue with these mappings',

  // Concept detail
  'concept_detail.supertypes': 'Supertypes',
  'concept_detail.subtypes': 'Subtypes',
  'concept_detail.properties': 'Properties',
  'concept_detail.no_properties': 'No properties defined yet.',
  'concept_detail.evidence': 'Evidence',
  'concept_detail.table.property': 'Property',
  'concept_detail.table.type': 'Type',
  'concept_detail.table.definition': 'Definition',
  'concept_detail.inherited_from': 'from',
  'concept_detail.includes': 'includes',
  'concept_detail.aligned_standards': 'Aligned standards',
  'concept_detail.table.standard': 'Standard',
  'concept_detail.table.equivalent': 'Equivalent',
  'concept_detail.table.match': 'Match',
  'concept_detail.evidence.all_systems': 'Present in all {total} mapped delivery systems.',
  'concept_detail.evidence.none': 'Not yet found in mapped delivery systems.',
  'concept_detail.evidence.partial': 'Present in {count} of {total} mapped delivery systems.',

  // Property detail
  'property_detail.details': 'Details',
  'property_detail.type': 'Type',
  'property_detail.cardinality': 'Cardinality',
  'property_detail.vocabulary': 'Vocabulary',
  'property_detail.references': 'References',
  'property_detail.used_by': 'Used by',
  'property_detail.no_uses': 'Not used by any concept yet.',
  'property_detail.system_mappings': 'System mappings',
  'property_detail.table.system_code': 'System code',
  'property_detail.table.system_label': 'System label',
  'property_detail.value_column': '{property} value',

  // Shared download labels
  'download.jsonld': 'JSON-LD',
  'download.csv': 'CSV',
  'download.definition_xlsx': 'Definition (Excel)',
  'download.template_xlsx': 'Template (Excel)',

  // Docs index
  'docs.page_title': 'Documentation',
  'docs.page_subtitle': 'Guides, technical references, and background on PublicSchema.',

  // Homepage schema index (data-driven section)
  'home.browse_schema': 'Browse the schema',
  'home.core_concepts': 'Core concepts',
  'home.vocabularies': 'Vocabularies',
  'home.plus_more': '+{count} more',
  'home.closing': 'PublicSchema is maintained as an open project.',
  'home.source_github': 'Source on GitHub',
  'home.about_project': 'About the project',

  // 404
  '404.page_title': 'Page not found',
  '404.message': 'The page you\u2019re looking for doesn\u2019t exist or has been moved.',
  '404.go_home': 'go back to the homepage',
  '404.or_browse': 'or browse',

  // Translation banner
  'banner.not_translated': 'This page is not yet available in your language. The content below is in English.',
  'banner.dismiss': 'Dismiss',
};

type Dict = typeof en;

export const ui: Record<Locale, Partial<Dict>> = {
  en,
  fr: {},
  es: {},
};
