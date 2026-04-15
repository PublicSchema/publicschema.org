/**
 * Loads vocabulary.json from the build pipeline output.
 * Uses Vite alias @vocab-data (configured in astro.config.mjs)
 * so the path resolves correctly in both dev and build.
 */

// @ts-ignore - resolved by Vite alias
import vocabData from "@vocab-data";

interface MultilingualText {
  en: string;
  fr?: string;
  es?: string;
}

interface Convergence {
  system_count: number;
  total_systems: number;
  notes?: string;
}

interface PropertyRef {
  id: string;
}

export interface PropertyGroup {
  category: string;
  properties: string[];
}

export interface CategoryLabel {
  label: MultilingualText;
}

export interface Concept {
  id: string;
  domain: string | null;
  uri: string;
  path: string;
  maturity: string;
  abstract: boolean;
  featured: boolean;
  label: MultilingualText;
  definition: MultilingualText;
  properties: PropertyRef[];
  property_groups: PropertyGroup[] | null;
  subtypes: string[];
  supertypes: string[];
  convergence: Convergence | null;
  external_equivalents: Record<string, ExternalEquivalent> | null;
  bibliography_refs?: string[];
}

export type AgeBand =
  | "infant_0_1"
  | "child_2_4"
  | "child_5_17"
  | "adolescent"
  | "adult";

export interface Property {
  id: string;
  label: MultilingualText;
  uri: string;
  path: string;
  maturity: string;
  definition: MultilingualText;
  type: string;
  cardinality: string;
  vocabulary: string | null;
  references: string | null;
  used_by: string[];
  category: string | null;
  sensitivity: "standard" | "sensitive" | "restricted" | null;
  age_applicability: AgeBand[] | null;
  system_mappings: Record<string, SystemMapping> | null;
  convergence: Convergence | null;
  external_equivalents: Record<string, ExternalEquivalent> | null;
  bibliography_refs?: string[];
}

export interface VocabValue {
  code: string;
  uri: string;
  label: MultilingualText;
  standard_code: string | null;
  definition: MultilingualText;
  group_type_applicability?: string[];
}

export interface SystemMappingValue {
  code: string;
  label: string;
  maps_to: string | number | null;
  unmapped_reason?: string;
}

export interface SystemMapping {
  vocabulary_name?: string;
  values: SystemMappingValue[];
  unmapped_canonical?: string[];
}

export interface ExternalEquivalent {
  label: string;
  uri: string;
  match:
    | "exact"
    | "close"
    | "broad"
    | "narrow"
    | "related"
    | "name_match"
    | "none";
  vocabulary: string;
  note?: string;
}

export interface VocabReference {
  name: string;
  uri: string;
  relationship: string;
  machine_readable: boolean;
  notes?: string;
}

export interface Vocabulary {
  id: string;
  domain: string | null;
  uri: string;
  path: string;
  maturity: string;
  label: MultilingualText;
  definition: MultilingualText;
  standard: { name: string; uri: string; notes?: string } | null;
  values: VocabValue[];
  system_mappings: Record<string, SystemMapping> | null;
  same_standard_systems: string[] | null;
  external_values: boolean;
  external_equivalents: Record<string, ExternalEquivalent> | null;
  references?: VocabReference[];
  bibliography_refs?: string[];
}

export type BibliographyType =
  | "international_standard"
  | "specification"
  | "classification"
  | "eu_vocabulary"
  | "eu_credential_schema"
  | "legal_instrument"
  | "guidance_publication";

export type BibliographyDomain =
  | "general"
  | "social_protection"
  | "health"
  | "crvs"
  | "payments"
  | "identity"
  | "humanitarian"
  | "education";

export interface BibliographyEntry {
  id: string;
  title: string;
  short_title: string | null;
  standard_number: string | null;
  publisher: string;
  authors: string[];
  year: number | null;
  version: string | null;
  type: BibliographyType;
  domain: BibliographyDomain;
  uri: string | null;
  access: "open" | "paywalled" | "registration_required" | null;
  status: "active" | "draft" | "superseded" | "withdrawn";
  informs: {
    concepts: string[];
    vocabularies: string[];
    properties: string[];
  };
}

export interface VocabularyData {
  meta: {
    name: string;
    base_uri: string;
    version: string;
  };
  concepts: Record<string, Concept>;
  properties: Record<string, Property>;
  vocabularies: Record<string, Vocabulary>;
  bibliography: Record<string, BibliographyEntry>;
  categories: Record<string, CategoryLabel>;
}

export function loadVocabulary(): VocabularyData {
  return vocabData as VocabularyData;
}
