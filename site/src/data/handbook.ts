export interface HandbookEntry {
  file: string;
  title: string;
  description: string;
  section: 'start' | 'adoption' | 'implementation' | 'governance';
}

export const handbookSectionOrder: HandbookEntry['section'][] = [
  'start',
  'adoption',
  'implementation',
  'governance',
];

export const handbookSectionLabels: Record<HandbookEntry['section'], string> = {
  start: 'Start here',
  adoption: 'Adoption paths',
  implementation: 'Implementation',
  governance: 'Governance and reference',
};

export const handbook: Record<string, HandbookEntry> = {
  introduction: {
    file: 'introduction.md',
    title: 'Introduction',
    description:
      'What PublicSchema is, who it is for, and how the handbook is organized around practical adoption work.',
    section: 'start',
  },
  'choose-your-path': {
    file: 'choose-your-path.md',
    title: 'Choose Your Path',
    description:
      'A decision guide for teams adopting vocabularies, mapping existing systems, designing new systems, issuing credentials, or governing extensions.',
    section: 'start',
  },
  'use-cases': {
    file: 'use-cases.md',
    title: 'Use Cases',
    description:
      'Common public service delivery scenarios and the PublicSchema artifacts each one needs.',
    section: 'start',
  },
  'worked-example': {
    file: 'worked-example.md',
    title: 'Worked Example: Mapping a Program Export',
    description:
      'A small end-to-end example that follows cash transfer reporting from source systems to mappings, validation, publication, and governance.',
    section: 'start',
  },
  'adopt-vocabularies': {
    file: 'adopt-vocabularies.md',
    title: 'Adopt Vocabularies',
    description:
      'The lightest adoption path: align local codes to canonical PublicSchema vocabularies without changing the internal data model.',
    section: 'adoption',
  },
  'map-existing-systems': {
    file: 'map-existing-systems.md',
    title: 'Map Existing Systems',
    description:
      'A complete mapping lifecycle for aligning existing platforms, schemas, APIs, and exports to PublicSchema.',
    section: 'adoption',
  },
  'design-new-system': {
    file: 'design-new-system.md',
    title: 'Design a New System',
    description:
      'How to use PublicSchema when designing a new registry, MIS, case management system, API, or procurement specification.',
    section: 'adoption',
  },
  'procurement-vendor-acceptance': {
    file: 'procurement-vendor-acceptance.md',
    title: 'Procurement and Vendor Acceptance',
    description:
      'Tender language, vendor evidence, acceptance levels, and validation checks for buying PublicSchema-compatible systems.',
    section: 'adoption',
  },
  'publish-exchanges': {
    file: 'publish-exchanges.md',
    title: 'Publish Exchanges and APIs',
    description:
      'How to expose PublicSchema-compatible data through APIs, events, files, analytics pipelines, and canonical exports.',
    section: 'implementation',
  },
  'issue-credentials': {
    file: 'issue-credentials.md',
    title: 'Issue Credentials',
    description:
      'How to use PublicSchema with JSON-LD contexts, JSON Schemas, SD-JWT Verifiable Credentials, and selective disclosure.',
    section: 'implementation',
  },
  'validate-and-package': {
    file: 'validate-and-package.md',
    title: 'Package and Validate Your Work',
    description:
      'What a complete adoption package should contain, how to validate it, and how to make it maintainable.',
    section: 'implementation',
  },
  'templates-and-checklists': {
    file: 'templates-and-checklists.md',
    title: 'Templates and Checklists',
    description:
      'Copyable tables and review checklists for mappings, crosswalks, packages, validation reports, privacy notes, and releases.',
    section: 'implementation',
  },
  'privacy-data-protection': {
    file: 'privacy-data-protection.md',
    title: 'Privacy and Data Protection',
    description:
      'Practical data minimization, identifier, sample data, credential, and package review guidance for sensitive service delivery data.',
    section: 'implementation',
  },
  'extend-publicschema': {
    file: 'extend-publicschema.md',
    title: 'Extend PublicSchema',
    description:
      'When to add local concepts, properties, or vocabulary values, and how to keep extensions interoperable.',
    section: 'governance',
  },
  governance: {
    file: 'governance.md',
    title: 'Governance, Versioning, and Methodology',
    description:
      'How PublicSchema evolves, how maturity and evidence work, and how implementation teams should govern local adoption.',
    section: 'governance',
  },
  glossary: {
    file: 'glossary.md',
    title: 'Glossary',
    description:
      'Shared terms used throughout the handbook, from concepts and properties to mappings, profiles, shapes, and credentials.',
    section: 'governance',
  },
};

export function handbookEntries(): Array<[string, HandbookEntry]> {
  return Object.entries(handbook);
}

export function nextHandbookSlug(slug: string): string | undefined {
  const slugs = Object.keys(handbook);
  const index = slugs.indexOf(slug);
  return index >= 0 ? slugs[index + 1] : undefined;
}

export function previousHandbookSlug(slug: string): string | undefined {
  const slugs = Object.keys(handbook);
  const index = slugs.indexOf(slug);
  return index > 0 ? slugs[index - 1] : undefined;
}
