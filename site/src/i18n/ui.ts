import type { Locale } from './languages';

/**
 * UI string dictionary. English is the source of truth. Missing keys in
 * French or Spanish fall back to English via the `t()` function.
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
  'lang.menu_label': 'Language',

  // Search UI
  'search.placeholder': 'Search concepts, properties...',
  'search.min_chars': 'Type at least 2 characters to search',
  'search.no_results': 'No results for',
  'search.browse_hint': 'Browse: Concepts, Properties, Vocabularies',
  'search.results_status': '{count} result(s) found',
  'search.no_results_status': 'No results found',
  'search.aria_label': 'Search PublicSchema',
  'search.close': 'Close search',

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
  'concept_detail.abstract_badge': 'abstract',
  'concept_detail.abstract_title': 'Abstract supertype: exists to group shared properties; instances are recorded as one of its subtypes',

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
  'docs.category.getting_started': 'Getting Started',
  'docs.category.technical': 'Technical Documentation',
  'docs.category.landscape': 'Landscape',

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
  fr: {
    // Navigation and chrome
    'nav.concepts': 'Concepts',
    'nav.properties': 'Propriétés',
    'nav.vocabularies': 'Vocabulaires',
    'nav.docs': 'Documentation',
    'nav.about': 'À propos',
    'nav.menu': 'Menu',
    'nav.search': 'Rechercher',

    // Language switcher
    'lang.switch_to': 'Changer la langue en {language}',
    'lang.current': 'Langue actuelle : {language}',
    'lang.menu_label': 'Langue',

    // Search UI
    'search.placeholder': 'Rechercher des concepts, des propriétés...',
    'search.min_chars': 'Saisissez au moins 2 caractères pour rechercher',
    'search.no_results': 'Aucun résultat pour',
    'search.browse_hint': 'Parcourir : Concepts, Propriétés, Vocabulaires',
    'search.results_status': '{count} résultat(s) trouvé(s)',
    'search.no_results_status': 'Aucun résultat trouvé',
    'search.aria_label': 'Rechercher sur PublicSchema',
    'search.close': 'Fermer la recherche',

    // Footer
    'footer.tagline': 'Définitions communes pour la prestation de services publics. Conçu pour permettre aux programmes de coordonner, partager des données et atteindre les personnes qu\'ils servent.',
    'footer.explore': 'Explorer',
    'footer.docs': 'Documentation',
    'footer.project': 'Projet',
    'footer.use_cases': 'Cas d\'usage',
    'footer.extension_mechanism': 'Mécanisme d\'extension',
    'footer.all_docs': 'Toute la documentation',
    'footer.systems': 'Systèmes',
    'footer.about': 'À propos',
    'footer.source_github': 'Source sur GitHub',
    'footer.terms': 'Conditions et licence',
    'footer.reference_model_cc': 'Modèle de référence :',
    'footer.code_apache': 'Code :',
    'footer.built_with': 'Réalisé avec',

    // Breadcrumbs and shared labels
    'breadcrumb.home': 'Accueil',
    'common.concepts': 'Concepts',
    'common.properties': 'Propriétés',
    'common.vocabularies': 'Vocabulaires',
    'common.systems': 'Systèmes',
    'common.data_types': 'Types de données',

    // Concepts index
    'concepts.page_title': 'Concepts',
    'concepts.page_subtitle': 'Les entités fondamentales qui apparaissent dans les systèmes de prestation de services publics.',
    'concepts.section_core': 'Fondamentaux',
    'concepts.section_social_protection': 'Protection sociale',
    'concepts.table.concept': 'Concept',
    'concepts.table.definition': 'Définition',
    'concepts.table.maturity': 'Maturité',

    // Properties index
    'properties.page_title': 'Propriétés',
    'properties.page_subtitle': 'Attributs réutilisables partagés entre les concepts.',
    'properties.table.property': 'Propriété',
    'properties.table.type': 'Type',
    'properties.table.used_by': 'Utilisé par',
    'properties.table.definition': 'Définition',

    // Vocabularies index
    'vocab.page_title': 'Vocabulaires',
    'vocab.page_subtitle': 'Ensembles de valeurs contrôlées, faisant référence aux normes internationales lorsqu\'elles existent.',
    'vocab.table.vocabulary': 'Vocabulaire',
    'vocab.table.values': 'Valeurs',
    'vocab.table.standard': 'Norme',
    'vocab.table.definition': 'Définition',

    // Vocabulary detail
    'vocab_detail.standard_reference': 'Référence normative',
    'vocab_detail.aligned_standards': 'Normes alignées',
    'vocab_detail.values': 'Valeurs',
    'vocab_detail.external_values_note_prefix': 'Ce vocabulaire est défini par une norme externe',
    'vocab_detail.external_values_note_suffix': 'La liste complète des valeurs est disponible dans les téléchargements ci-dessus',
    'vocab_detail.official_standard_page': 'page officielle de la norme',
    'vocab_detail.table.code': 'Code',
    'vocab_detail.table.label': 'Libellé',
    'vocab_detail.table.standard_code': 'Code normalisé',
    'vocab_detail.table.definition': 'Définition',
    'vocab_detail.same_standard': 'Même norme',
    'vocab_detail.same_standard_desc_prefix': 'Les systèmes suivants utilisent la même norme sous-jacente',
    'vocab_detail.same_standard_desc_suffix': 'pour ce vocabulaire, les valeurs sont donc directement compatibles sans correspondance :',
    'vocab_detail.system_mappings': 'Correspondances système',
    'vocab_detail.system_vocabulary': 'Vocabulaire système :',
    'vocab_detail.no_mapping': 'aucun équivalent',
    'vocab_detail.not_covered_by': 'Non couvert par {system} :',

    // Systems index
    'systems.page_title': 'Systèmes',
    'systems.page_subtitle': 'Systèmes externes et normes avec des correspondances de vocabulaire vers les valeurs canoniques de PublicSchema.',
    'systems.table.system': 'Système',
    'systems.table.vocabularies': 'Vocabulaires',
    'systems.table.value_mappings': 'Correspondances de valeurs',
    'systems.table.same_standard': 'Même norme',
    'systems.table.status': 'Statut',

    // System detail
    'system_detail.vocabularies': 'Vocabulaires',
    'system_detail.properties': 'Propriétés',
    'system_detail.table.vocabulary': 'Vocabulaire',
    'system_detail.table.system_name': 'Nom dans le système',
    'system_detail.table.relationship': 'Relation',
    'system_detail.table.coverage': 'Couverture',
    'system_detail.table.gaps': 'Lacunes',
    'system_detail.relationship_same_standard': 'Même norme',
    'system_detail.relationship_value_mapping': 'Correspondance de valeurs',
    'system_detail.coverage_all': 'Toutes les valeurs',
    'system_detail.coverage_mapped': '{mapped}/{total} correspondances',
    'system_detail.not_covered': '{count} non couvert(s)',
    'system_detail.report_button': 'Signaler un problème avec ces correspondances',

    // Concept detail
    'concept_detail.supertypes': 'Supertypes',
    'concept_detail.subtypes': 'Sous-types',
    'concept_detail.properties': 'Propriétés',
    'concept_detail.no_properties': 'Aucune propriété définie pour l\'instant.',
    'concept_detail.evidence': 'Données probantes',
    'concept_detail.table.property': 'Propriété',
    'concept_detail.table.type': 'Type',
    'concept_detail.table.definition': 'Définition',
    'concept_detail.inherited_from': 'de',
    'concept_detail.includes': 'comprend',
    'concept_detail.aligned_standards': 'Normes alignées',
    'concept_detail.table.standard': 'Norme',
    'concept_detail.table.equivalent': 'Équivalent',
    'concept_detail.table.match': 'Correspondance',
    'concept_detail.evidence.all_systems': 'Présent dans l\'ensemble des {total} systèmes de prestation cartographiés.',
    'concept_detail.evidence.none': 'Pas encore trouvé dans les systèmes de prestation cartographiés.',
    'concept_detail.evidence.partial': 'Présent dans {count} des {total} systèmes de prestation cartographiés.',
    'concept_detail.abstract_badge': 'abstrait',
    'concept_detail.abstract_title': 'Supertype abstrait : existe pour regrouper des propriétés partagées ; les instances sont enregistrées comme l\'un de ses sous-types',

    // Property detail
    'property_detail.details': 'Détails',
    'property_detail.type': 'Type',
    'property_detail.cardinality': 'Cardinalité',
    'property_detail.vocabulary': 'Vocabulaire',
    'property_detail.references': 'Références',
    'property_detail.used_by': 'Utilisé par',
    'property_detail.no_uses': 'Non utilisé par aucun concept pour l\'instant.',
    'property_detail.system_mappings': 'Correspondances système',
    'property_detail.table.system_code': 'Code système',
    'property_detail.table.system_label': 'Libellé système',
    'property_detail.value_column': 'Valeur {property}',

    // Shared download labels
    'download.jsonld': 'JSON-LD',
    'download.csv': 'CSV',
    'download.definition_xlsx': 'Définition (Excel)',
    'download.template_xlsx': 'Modèle (Excel)',

    // Docs index
    'docs.page_title': 'Documentation',
    'docs.page_subtitle': 'Guides, références techniques et informations générales sur PublicSchema.',
    'docs.category.getting_started': 'Pour commencer',
    'docs.category.technical': 'Documentation technique',
    'docs.category.landscape': 'Panorama',

    // Homepage schema index (data-driven section)
    'home.browse_schema': 'Explorer le schéma',
    'home.core_concepts': 'Concepts fondamentaux',
    'home.vocabularies': 'Vocabulaires',
    'home.plus_more': '+{count} de plus',
    'home.closing': 'PublicSchema est maintenu comme un projet ouvert.',
    'home.source_github': 'Source sur GitHub',
    'home.about_project': 'À propos du projet',

    // 404
    '404.page_title': 'Page introuvable',
    '404.message': 'La page que vous recherchez n\'existe pas ou a été déplacée.',
    '404.go_home': 'retourner à la page d\'accueil',
    '404.or_browse': 'ou parcourir',

    // Translation banner
    'banner.not_translated': 'Cette page n\'est pas encore disponible dans votre langue. Le contenu ci-dessous est en anglais.',
    'banner.dismiss': 'Fermer',
  },
  es: {
    // Navigation and chrome
    'nav.concepts': 'Conceptos',
    'nav.properties': 'Propiedades',
    'nav.vocabularies': 'Vocabularios',
    'nav.docs': 'Documentación',
    'nav.about': 'Acerca de',
    'nav.menu': 'Menú',
    'nav.search': 'Buscar',

    // Language switcher
    'lang.switch_to': 'Cambiar idioma a {language}',
    'lang.current': 'Idioma actual: {language}',
    'lang.menu_label': 'Idioma',

    // Search UI
    'search.placeholder': 'Buscar conceptos, propiedades...',
    'search.min_chars': 'Escriba al menos 2 caracteres para buscar',
    'search.no_results': 'Sin resultados para',
    'search.browse_hint': 'Explorar: Conceptos, Propiedades, Vocabularios',
    'search.results_status': '{count} resultado(s) encontrado(s)',
    'search.no_results_status': 'No se encontraron resultados',
    'search.aria_label': 'Buscar en PublicSchema',
    'search.close': 'Cerrar búsqueda',

    // Footer
    'footer.tagline': 'Definiciones comunes para la prestación de servicios públicos. Diseñado para que los programas puedan coordinarse, compartir datos y llegar a las personas a quienes sirven.',
    'footer.explore': 'Explorar',
    'footer.docs': 'Documentación',
    'footer.project': 'Proyecto',
    'footer.use_cases': 'Casos de uso',
    'footer.extension_mechanism': 'Mecanismo de extensión',
    'footer.all_docs': 'Toda la documentación',
    'footer.systems': 'Sistemas',
    'footer.about': 'Acerca de',
    'footer.source_github': 'Fuente en GitHub',
    'footer.terms': 'Términos y licencia',
    'footer.reference_model_cc': 'Modelo de referencia:',
    'footer.code_apache': 'Código:',
    'footer.built_with': 'Desarrollado con',

    // Breadcrumbs and shared labels
    'breadcrumb.home': 'Inicio',
    'common.concepts': 'Conceptos',
    'common.properties': 'Propiedades',
    'common.vocabularies': 'Vocabularios',
    'common.systems': 'Sistemas',
    'common.data_types': 'Tipos de datos',

    // Concepts index
    'concepts.page_title': 'Conceptos',
    'concepts.page_subtitle': 'Las entidades fundamentales que aparecen en los sistemas de prestación de servicios públicos.',
    'concepts.section_core': 'Fundamentales',
    'concepts.section_social_protection': 'Protección social',
    'concepts.table.concept': 'Concepto',
    'concepts.table.definition': 'Definición',
    'concepts.table.maturity': 'Madurez',

    // Properties index
    'properties.page_title': 'Propiedades',
    'properties.page_subtitle': 'Atributos reutilizables compartidos entre conceptos.',
    'properties.table.property': 'Propiedad',
    'properties.table.type': 'Tipo',
    'properties.table.used_by': 'Usado por',
    'properties.table.definition': 'Definición',

    // Vocabularies index
    'vocab.page_title': 'Vocabularios',
    'vocab.page_subtitle': 'Conjuntos de valores controlados, con referencia a normas internacionales cuando existen.',
    'vocab.table.vocabulary': 'Vocabulario',
    'vocab.table.values': 'Valores',
    'vocab.table.standard': 'Norma',
    'vocab.table.definition': 'Definición',

    // Vocabulary detail
    'vocab_detail.standard_reference': 'Referencia normativa',
    'vocab_detail.aligned_standards': 'Normas alineadas',
    'vocab_detail.values': 'Valores',
    'vocab_detail.external_values_note_prefix': 'Este vocabulario está definido por una norma externa',
    'vocab_detail.external_values_note_suffix': 'La lista completa de valores está disponible en las descargas anteriores',
    'vocab_detail.official_standard_page': 'página oficial de la norma',
    'vocab_detail.table.code': 'Código',
    'vocab_detail.table.label': 'Etiqueta',
    'vocab_detail.table.standard_code': 'Código normalizado',
    'vocab_detail.table.definition': 'Definición',
    'vocab_detail.same_standard': 'Misma norma',
    'vocab_detail.same_standard_desc_prefix': 'Los siguientes sistemas utilizan la misma norma subyacente',
    'vocab_detail.same_standard_desc_suffix': 'para este vocabulario, por lo que los valores son directamente compatibles sin correspondencia:',
    'vocab_detail.system_mappings': 'Correspondencias del sistema',
    'vocab_detail.system_vocabulary': 'Vocabulario del sistema:',
    'vocab_detail.no_mapping': 'sin equivalente',
    'vocab_detail.not_covered_by': 'No cubierto por {system}:',

    // Systems index
    'systems.page_title': 'Sistemas',
    'systems.page_subtitle': 'Sistemas externos y normas con correspondencias de vocabulario hacia los valores canónicos de PublicSchema.',
    'systems.table.system': 'Sistema',
    'systems.table.vocabularies': 'Vocabularios',
    'systems.table.value_mappings': 'Correspondencias de valores',
    'systems.table.same_standard': 'Misma norma',
    'systems.table.status': 'Estado',

    // System detail
    'system_detail.vocabularies': 'Vocabularios',
    'system_detail.properties': 'Propiedades',
    'system_detail.table.vocabulary': 'Vocabulario',
    'system_detail.table.system_name': 'Nombre en el sistema',
    'system_detail.table.relationship': 'Relación',
    'system_detail.table.coverage': 'Cobertura',
    'system_detail.table.gaps': 'Brechas',
    'system_detail.relationship_same_standard': 'Misma norma',
    'system_detail.relationship_value_mapping': 'Correspondencia de valores',
    'system_detail.coverage_all': 'Todos los valores',
    'system_detail.coverage_mapped': '{mapped}/{total} correspondencias',
    'system_detail.not_covered': '{count} sin cobertura',
    'system_detail.report_button': 'Reportar un problema con estas correspondencias',

    // Concept detail
    'concept_detail.supertypes': 'Supertipos',
    'concept_detail.subtypes': 'Subtipos',
    'concept_detail.properties': 'Propiedades',
    'concept_detail.no_properties': 'No hay propiedades definidas aún.',
    'concept_detail.evidence': 'Evidencia',
    'concept_detail.table.property': 'Propiedad',
    'concept_detail.table.type': 'Tipo',
    'concept_detail.table.definition': 'Definición',
    'concept_detail.inherited_from': 'de',
    'concept_detail.includes': 'incluye',
    'concept_detail.aligned_standards': 'Normas alineadas',
    'concept_detail.table.standard': 'Norma',
    'concept_detail.table.equivalent': 'Equivalente',
    'concept_detail.table.match': 'Correspondencia',
    'concept_detail.evidence.all_systems': 'Presente en los {total} sistemas de prestación mapeados.',
    'concept_detail.evidence.none': 'Aún no encontrado en los sistemas de prestación mapeados.',
    'concept_detail.evidence.partial': 'Presente en {count} de {total} sistemas de prestación mapeados.',
    'concept_detail.abstract_badge': 'abstracto',
    'concept_detail.abstract_title': 'Supertipo abstracto: existe para agrupar propiedades compartidas; las instancias se registran como uno de sus subtipos',

    // Property detail
    'property_detail.details': 'Detalles',
    'property_detail.type': 'Tipo',
    'property_detail.cardinality': 'Cardinalidad',
    'property_detail.vocabulary': 'Vocabulario',
    'property_detail.references': 'Referencias',
    'property_detail.used_by': 'Usado por',
    'property_detail.no_uses': 'No usado por ningún concepto aún.',
    'property_detail.system_mappings': 'Correspondencias del sistema',
    'property_detail.table.system_code': 'Código del sistema',
    'property_detail.table.system_label': 'Etiqueta del sistema',
    'property_detail.value_column': 'Valor de {property}',

    // Shared download labels
    'download.jsonld': 'JSON-LD',
    'download.csv': 'CSV',
    'download.definition_xlsx': 'Definición (Excel)',
    'download.template_xlsx': 'Plantilla (Excel)',

    // Docs index
    'docs.page_title': 'Documentación',
    'docs.page_subtitle': 'Guías, referencias técnicas e información general sobre PublicSchema.',
    'docs.category.getting_started': 'Primeros pasos',
    'docs.category.technical': 'Documentación técnica',
    'docs.category.landscape': 'Panorama',

    // Homepage schema index (data-driven section)
    'home.browse_schema': 'Explorar el esquema',
    'home.core_concepts': 'Conceptos fundamentales',
    'home.vocabularies': 'Vocabularios',
    'home.plus_more': '+{count} más',
    'home.closing': 'PublicSchema se mantiene como un proyecto abierto.',
    'home.source_github': 'Fuente en GitHub',
    'home.about_project': 'Acerca del proyecto',

    // 404
    '404.page_title': 'Página no encontrada',
    '404.message': 'La página que busca no existe o ha sido movida.',
    '404.go_home': 'volver a la página de inicio',
    '404.or_browse': 'o explorar',

    // Translation banner
    'banner.not_translated': 'Esta página aún no está disponible en español. El contenido a continuación está en inglés.',
    'banner.dismiss': 'Cerrar',
  },
};
