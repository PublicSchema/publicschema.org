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

export interface Concept {
  id: string;
  domain: string | null;
  uri: string;
  path: string;
  maturity: string;
  definition: MultilingualText;
  properties: PropertyRef[];
  subtypes: string[];
  supertypes: string[];
  convergence: Convergence | null;
}

export interface Property {
  id: string;
  uri: string;
  path: string;
  maturity: string;
  definition: MultilingualText;
  type: string;
  cardinality: string;
  vocabulary: string | null;
  references: string | null;
  used_by: string[];
  sensitivity: "standard" | "sensitive" | "restricted" | null;
  convergence: Convergence | null;
}

export interface VocabValue {
  code: string;
  uri: string;
  label: MultilingualText;
  standard_code: string | null;
  definition: MultilingualText;
}

export interface SystemMappingValue {
  code: string;
  label: string;
  maps_to: string | null;
  unmapped_reason?: string;
}

export interface SystemMapping {
  vocabulary_name?: string;
  values: SystemMappingValue[];
  unmapped_canonical?: string[];
}

export interface Vocabulary {
  id: string;
  domain: string | null;
  uri: string;
  path: string;
  maturity: string;
  definition: MultilingualText;
  standard: { name: string; uri: string; notes?: string } | null;
  values: VocabValue[];
  system_mappings: Record<string, SystemMapping> | null;
  same_standard_systems: string[] | null;
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
}

export function loadVocabulary(): VocabularyData {
  return vocabData as VocabularyData;
}
