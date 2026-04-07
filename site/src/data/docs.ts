export interface DocEntry {
  file: string;
  title: string;
  description: string;
  category: string;
}

export const docs: Record<string, DocEntry> = {
  "integration-guide": {
    file: "integration-guide.md",
    title: "Integration Guide",
    description: "How to reference, validate, and use PublicSchema in your system.",
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
  "related-standards": {
    file: "related-standards.md",
    title: "Related Standards",
    description: "How PublicSchema relates to DCI, GovStack, FHIR, EU Core Vocabularies, and other initiatives.",
    category: "Landscape",
  },
};
