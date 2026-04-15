import type { Locale } from '../i18n/languages';

export type DocCategoryKey = 'getting_started' | 'technical' | 'landscape';

export interface DocEntry {
  file: string;
  title: Record<Locale, string>;
  description: Record<Locale, string>;
  category: DocCategoryKey;
}

export const docs: Record<string, DocEntry> = {
  "integration-patterns": {
    file: "integration-patterns.md",
    title: {
      en: "Integration Patterns",
      fr: "Schémas d'intégration",
      es: "Patrones de integración",
    },
    description: {
      en: "How PublicSchema works across REST APIs, event-driven systems, verifiable credentials, file exchanges, and analytics pipelines.",
      fr: "Comment PublicSchema s'intègre aux API REST, aux systèmes événementiels, aux attestations vérifiables, aux échanges de fichiers et aux pipelines analytiques.",
      es: "Cómo PublicSchema funciona con API REST, sistemas orientados a eventos, credenciales verificables, intercambios de archivos y canalizaciones analíticas.",
    },
    category: "getting_started",
  },
  "use-cases": {
    file: "use-cases.md",
    title: {
      en: "Use Cases",
      fr: "Cas d'utilisation",
      es: "Casos de uso",
    },
    description: {
      en: "Concrete scenarios showing how PublicSchema helps programs coordinate, share data, and reach people across sectors.",
      fr: "Scénarios concrets montrant comment PublicSchema aide les programmes à se coordonner, à partager des données et à atteindre les personnes dans différents secteurs.",
      es: "Escenarios concretos que muestran cómo PublicSchema ayuda a los programas a coordinarse, compartir datos y llegar a las personas en distintos sectores.",
    },
    category: "getting_started",
  },
  "vocabulary-adoption-guide": {
    file: "vocabulary-adoption-guide.md",
    title: {
      en: "Vocabulary Adoption Guide",
      fr: "Guide d'adoption des vocabulaires",
      es: "Guía de adopción de vocabularios",
    },
    description: {
      en: "The lightest integration path: align your system's codes and field values to canonical vocabularies without changing your data model.",
      fr: "La voie d'intégration la plus légère : aligner les codes et valeurs de champs de votre système sur les vocabulaires canoniques sans modifier votre modèle de données.",
      es: "La ruta de integración más ligera: alinear los códigos y valores de campos de su sistema con los vocabularios canónicos sin cambiar su modelo de datos.",
    },
    category: "getting_started",
  },
  "interoperability-guide": {
    file: "interoperability-guide.md",
    title: {
      en: "Interoperability & Mapping Guide",
      fr: "Guide d'interopérabilité et de correspondance",
      es: "Guía de interoperabilidad y correspondencia",
    },
    description: {
      en: "Using PublicSchema as a Rosetta Stone to map fields and codes between systems, build data exchanges, and consolidate records.",
      fr: "Utiliser PublicSchema comme pierre de Rosette pour faire correspondre champs et codes entre systèmes, construire des échanges de données et consolider des enregistrements.",
      es: "Usar PublicSchema como piedra de Rosetta para correlacionar campos y códigos entre sistemas, construir intercambios de datos y consolidar registros.",
    },
    category: "getting_started",
  },
  "data-model-guide": {
    file: "data-model-guide.md",
    title: {
      en: "Data Model Design Guide",
      fr: "Guide de conception du modèle de données",
      es: "Guía de diseño del modelo de datos",
    },
    description: {
      en: "Using PublicSchema as a reference when designing a new system's data model for interoperability from the start.",
      fr: "Utiliser PublicSchema comme référence lors de la conception du modèle de données d'un nouveau système, pour l'interopérabilité dès le départ.",
      es: "Usar PublicSchema como referencia al diseñar el modelo de datos de un nuevo sistema, para lograr la interoperabilidad desde el inicio.",
    },
    category: "getting_started",
  },
  "jsonld-vc-guide": {
    file: "jsonld-vc-guide.md",
    title: {
      en: "JSON-LD & Verifiable Credentials Guide",
      fr: "Guide JSON-LD et attestations vérifiables",
      es: "Guía de JSON-LD y credenciales verificables",
    },
    description: {
      en: "How to use PublicSchema with JSON-LD contexts, JSON Schema validation, and SD-JWT Verifiable Credentials.",
      fr: "Comment utiliser PublicSchema avec les contextes JSON-LD, la validation JSON Schema et les attestations vérifiables SD-JWT.",
      es: "Cómo usar PublicSchema con contextos JSON-LD, validación con JSON Schema y credenciales verificables SD-JWT.",
    },
    category: "getting_started",
  },
  "extension-mechanism": {
    file: "extension-mechanism.md",
    title: {
      en: "Extension Mechanism",
      fr: "Mécanisme d'extension",
      es: "Mecanismo de extensión",
    },
    description: {
      en: "Adding custom properties, vocabulary values, and concepts using JSON-LD namespaces.",
      fr: "Ajouter des propriétés, des valeurs de vocabulaire et des concepts personnalisés en utilisant les espaces de noms JSON-LD.",
      es: "Añadir propiedades, valores de vocabulario y conceptos personalizados usando espacios de nombres JSON-LD.",
    },
    category: "technical",
  },
  "selective-disclosure": {
    file: "selective-disclosure.md",
    title: {
      en: "Selective Disclosure",
      fr: "Divulgation sélective",
      es: "Divulgación selectiva",
    },
    description: {
      en: "Privacy design for Verifiable Credentials using SD-JWT.",
      fr: "Conception axée sur la vie privée pour les attestations vérifiables à l'aide de SD-JWT.",
      es: "Diseño orientado a la privacidad para credenciales verificables usando SD-JWT.",
    },
    category: "technical",
  },
  "versioning-and-maturity": {
    file: "versioning-and-maturity.md",
    title: {
      en: "Versioning and Maturity",
      fr: "Versionnage et maturité",
      es: "Versionado y madurez",
    },
    description: {
      en: "Stability guarantees, maturity levels, and URI persistence.",
      fr: "Garanties de stabilité, niveaux de maturité et persistance des URI.",
      es: "Garantías de estabilidad, niveles de madurez y persistencia de URI.",
    },
    category: "technical",
  },
  "design-principles": {
    file: "design-principles.md",
    title: {
      en: "Design Principles",
      fr: "Principes de conception",
      es: "Principios de diseño",
    },
    description: {
      en: "The foundational philosophy behind PublicSchema: semantic not structural, descriptive not prescriptive, evidence-based.",
      fr: "La philosophie fondatrice de PublicSchema : sémantique plutôt que structurel, descriptif plutôt que prescriptif, fondé sur des preuves.",
      es: "La filosofía fundacional de PublicSchema: semántico en vez de estructural, descriptivo en vez de prescriptivo, basado en evidencias.",
    },
    category: "getting_started",
  },
  "schema-design": {
    file: "schema-design.md",
    title: {
      en: "Schema Design",
      fr: "Conception du schéma",
      es: "Diseño del esquema",
    },
    description: {
      en: "How elements are named, scoped, and modeled. Naming conventions, domain namespacing, and the concept/property/vocabulary decision tree.",
      fr: "Comment les éléments sont nommés, délimités et modélisés. Conventions de nommage, espaces de noms par domaine et arbre de décision concept/propriété/vocabulaire.",
      es: "Cómo se nombran, delimitan y modelan los elementos. Convenciones de nomenclatura, espacios de nombres por dominio y árbol de decisión concepto/propiedad/vocabulario.",
    },
    category: "technical",
  },
  "vocabulary-design": {
    file: "vocabulary-design.md",
    title: {
      en: "Vocabulary Design",
      fr: "Conception des vocabulaires",
      es: "Diseño de vocabularios",
    },
    description: {
      en: "Rules for designing controlled vocabularies, referencing standards, and validating through system mappings.",
      fr: "Règles pour concevoir des vocabulaires contrôlés, référencer des normes et valider par des correspondances entre systèmes.",
      es: "Reglas para diseñar vocabularios controlados, referenciar normas y validar mediante correspondencias entre sistemas.",
    },
    category: "technical",
  },
  "related-standards": {
    file: "related-standards.md",
    title: {
      en: "Related Standards",
      fr: "Normes connexes",
      es: "Normas relacionadas",
    },
    description: {
      en: "How PublicSchema relates to DCI, GovStack, FHIR, EU Core Vocabularies, and other initiatives.",
      fr: "Comment PublicSchema se positionne par rapport à DCI, GovStack, FHIR, les vocabulaires de base de l'UE et d'autres initiatives.",
      es: "Cómo se relaciona PublicSchema con DCI, GovStack, FHIR, los vocabularios básicos de la UE y otras iniciativas.",
    },
    category: "landscape",
  },
  "methodology": {
    file: "methodology.md",
    title: {
      en: "Methodology",
      fr: "Méthodologie",
      es: "Metodología",
    },
    description: {
      en: "How PublicSchema is built: sources synthesized, where AI tooling accelerates the work, what humans review, and how claims can be verified.",
      fr: "Comment PublicSchema est construit : sources synthétisées, usages de l'IA pour accélérer le travail, ce que les humains examinent, et comment vérifier les affirmations.",
      es: "Cómo se construye PublicSchema: fuentes sintetizadas, dónde la IA acelera el trabajo, qué revisan los humanos y cómo se pueden verificar las afirmaciones.",
    },
    category: "landscape",
  },
  "fhir-mapping-guide": {
    file: "fhir-mapping-guide.md",
    title: {
      en: "FHIR Mapping Guide",
      fr: "Guide de correspondance FHIR",
      es: "Guía de correspondencia FHIR",
    },
    description: {
      en: "Exchanging PublicSchema disability, functioning, and anthropometric data over FHIR R4: Observation vs. QuestionnaireResponse, LOINC coding, and IPS alignment.",
      fr: "Échanger les données PublicSchema sur le handicap, le fonctionnement et l'anthropométrie via FHIR R4 : Observation ou QuestionnaireResponse, codage LOINC et alignement avec IPS.",
      es: "Intercambiar datos de discapacidad, funcionamiento y antropometría de PublicSchema a través de FHIR R4: Observation o QuestionnaireResponse, codificación LOINC y alineación con IPS.",
    },
    category: "technical",
  },
};
