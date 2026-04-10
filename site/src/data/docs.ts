export interface DocEntry {
  file: string;
  title: string;
  description: string;
  category: string;
}

export const docs: Record<string, DocEntry> = {
  "use-cases": {
    file: "use-cases.md",
    title: "Use Cases",
    description: "Concrete scenarios showing how PublicSchema helps programs coordinate, share data, and reach people across sectors.",
    category: "Getting Started",
  },
  "vocabulary-adoption-guide": {
    file: "vocabulary-adoption-guide.md",
    title: "Vocabulary Adoption Guide",
    description: "The lightest integration path: align your system's codes and field values to canonical vocabularies without changing your data model.",
    category: "Getting Started",
  },
  "interoperability-guide": {
    file: "interoperability-guide.md",
    title: "Interoperability & Mapping Guide",
    description: "Using PublicSchema as a Rosetta Stone to map fields and codes between systems, build data exchanges, and consolidate records.",
    category: "Getting Started",
  },
  "data-model-guide": {
    file: "data-model-guide.md",
    title: "Data Model Design Guide",
    description: "Using PublicSchema as a reference when designing a new system's data model for interoperability from the start.",
    category: "Getting Started",
  },
  "jsonld-vc-guide": {
    file: "jsonld-vc-guide.md",
    title: "JSON-LD & Verifiable Credentials Guide",
    description: "How to use PublicSchema with JSON-LD contexts, JSON Schema validation, and SD-JWT Verifiable Credentials.",
    category: "Getting Started",
  },
  "extension-mechanism": {
    file: "extension-mechanism.md",
    title: "Extension Mechanism",
    description: "Adding custom properties, vocabulary values, and concepts using JSON-LD namespaces.",
    category: "Technical Documentation",
  },
  "selective-disclosure": {
    file: "selective-disclosure.md",
    title: "Selective Disclosure",
    description: "Privacy design for Verifiable Credentials using SD-JWT.",
    category: "Technical Documentation",
  },
  "versioning-and-maturity": {
    file: "versioning-and-maturity.md",
    title: "Versioning and Maturity",
    description: "Stability guarantees, maturity levels, and URI persistence.",
    category: "Technical Documentation",
  },
  "design-principles": {
    file: "design-principles.md",
    title: "Design Principles",
    description: "The foundational philosophy behind PublicSchema: semantic not structural, descriptive not prescriptive, evidence-based.",
    category: "Getting Started",
  },
  "schema-design": {
    file: "schema-design.md",
    title: "Schema Design",
    description: "How elements are named, scoped, and modeled. Naming conventions, domain namespacing, and the concept/property/vocabulary decision tree.",
    category: "Technical Documentation",
  },
  "vocabulary-design": {
    file: "vocabulary-design.md",
    title: "Vocabulary Design",
    description: "Rules for designing controlled vocabularies, referencing standards, and validating through system mappings.",
    category: "Technical Documentation",
  },
  "related-standards": {
    file: "related-standards.md",
    title: "Related Standards",
    description: "How PublicSchema relates to DCI, GovStack, FHIR, EU Core Vocabularies, and other initiatives.",
    category: "Landscape",
  },
};
