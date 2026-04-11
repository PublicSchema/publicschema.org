/**
 * System metadata registry.
 *
 * The authoritative list of systems comes from vocabulary.json
 * (system_mappings keys + same_standard_systems entries).
 * This registry provides display names, URLs, and review status.
 * If a system ID appears in the data but not here, it renders
 * with the raw ID as its name and no URL.
 */

import { loadVocabulary } from "./vocabulary";
import type { Vocabulary } from "./vocabulary";

export interface SystemMeta {
  name: string;
  url: string;
  description: string;
  reviewStatus: "unreviewed" | "reviewed";
  lastReviewed?: string;
  reviewedBy?: string;
}

export const systemRegistry: Record<string, SystemMeta> = {
  openspp: {
    name: "OpenSPP",
    url: "https://openspp.org",
    description: "Open-source social protection platform.",
    reviewStatus: "unreviewed",
  },
  openimis: {
    name: "openIMIS",
    url: "https://openimis.org",
    description: "Open-source insurance management information system.",
    reviewStatus: "unreviewed",
  },
  spdci: {
    name: "SPDCI",
    url: "https://spdci.org",
    description: "Social Protection Digital Convergence Initiative standard.",
    reviewStatus: "unreviewed",
  },
  fhir_r4: {
    name: "FHIR R4",
    url: "https://hl7.org/fhir/R4/",
    description: "HL7 Fast Healthcare Interoperability Resources, Release 4.",
    reviewStatus: "unreviewed",
  },
  dhis2: {
    name: "DHIS2",
    url: "https://dhis2.org",
    description: "Open-source health information management platform.",
    reviewStatus: "unreviewed",
  },
  opencrvs: {
    name: "OpenCRVS",
    url: "https://opencrvs.org",
    description: "Open-source civil registration and vital statistics platform.",
    reviewStatus: "unreviewed",
  },
  ocha_cod_ab: {
    name: "OCHA COD-AB",
    url: "https://cod.unocha.org/",
    description: "OCHA Common Operational Datasets for administrative boundaries.",
    reviewStatus: "unreviewed",
  },
};

export function getSystemName(id: string): string {
  return systemRegistry[id]?.name ?? id;
}

export function getSystemMeta(id: string): SystemMeta {
  return systemRegistry[id] ?? {
    name: id,
    url: "",
    description: "",
    reviewStatus: "unreviewed" as const,
  };
}

export interface EnrichedMappingValue {
  code: string;
  label: string;
  maps_to: string | null;
}

export interface EnrichedMapping {
  vocabulary_name?: string;
  values: EnrichedMappingValue[];
  unmapped_canonical?: string[];
}

export function isEnrichedMapping(mapping: unknown): mapping is EnrichedMapping {
  return (
    typeof mapping === "object" &&
    mapping !== null &&
    "values" in mapping &&
    Array.isArray((mapping as EnrichedMapping).values)
  );
}

export interface SystemVocabEntry {
  kind: "vocabulary" | "property";
  vocabId: string;
  vocabDefinition: string;
  relationship: "value_mapping" | "same_standard";
  vocabularyName?: string;
  mappedCount: number;
  totalSystemValues: number;
  unmappedCanonicalCount: number;
}

/**
 * Collect all system IDs from vocabulary data and build
 * per-system vocabulary entries.
 */
export function buildSystemIndex(): Record<string, SystemVocabEntry[]> {
  const vocab = loadVocabulary();
  const index: Record<string, SystemVocabEntry[]> = {};

  for (const v of Object.values(vocab.vocabularies)) {
    if (v.system_mappings) {
      for (const [systemId, mapping] of Object.entries(v.system_mappings)) {
        if (!index[systemId]) index[systemId] = [];

        if (isEnrichedMapping(mapping)) {
          const mapped = mapping.values.filter((val) => val.maps_to !== null).length;
          index[systemId].push({
            kind: "vocabulary",
            vocabId: v.id,
            vocabDefinition: v.definition.en?.slice(0, 100) || "",
            relationship: "value_mapping",
            vocabularyName: mapping.vocabulary_name,
            mappedCount: mapped,
            totalSystemValues: mapping.values.length,
            unmappedCanonicalCount: mapping.unmapped_canonical?.length ?? 0,
          });
        } else {
          const count = Object.keys(mapping as Record<string, string>).length;
          index[systemId].push({
            kind: "vocabulary",
            vocabId: v.id,
            vocabDefinition: v.definition.en?.slice(0, 100) || "",
            relationship: "value_mapping",
            mappedCount: count,
            totalSystemValues: count,
            unmappedCanonicalCount: 0,
          });
        }
      }
    }

    if (v.same_standard_systems) {
      for (const systemId of v.same_standard_systems) {
        if (!index[systemId]) index[systemId] = [];
        // Skip if this system already has a value mapping for this vocab
        const existing = index[systemId].find((e) => e.vocabId === v.id);
        if (existing) continue;

        index[systemId].push({
          kind: "vocabulary",
          vocabId: v.id,
          vocabDefinition: v.definition.en?.slice(0, 100) || "",
          relationship: "same_standard",
          mappedCount: v.values.length,
          totalSystemValues: v.values.length,
          unmappedCanonicalCount: 0,
        });
      }
    }
  }

  // Property-level system_mappings
  for (const p of Object.values(vocab.properties)) {
    if (p.system_mappings) {
      for (const [systemId, mapping] of Object.entries(p.system_mappings)) {
        if (!index[systemId]) index[systemId] = [];

        if (isEnrichedMapping(mapping)) {
          const mapped = mapping.values.filter((val) => val.maps_to !== null).length;
          index[systemId].push({
            kind: "property",
            vocabId: p.id,
            vocabDefinition: p.definition.en?.slice(0, 100) || "",
            relationship: "value_mapping",
            vocabularyName: mapping.vocabulary_name,
            mappedCount: mapped,
            totalSystemValues: mapping.values.length,
            unmappedCanonicalCount: mapping.unmapped_canonical?.length ?? 0,
          });
        }
      }
    }
  }

  // Warn about unregistered systems in dev
  if (import.meta.env?.DEV) {
    for (const systemId of Object.keys(index)) {
      if (!systemRegistry[systemId]) {
        console.warn(
          `[systems] System "${systemId}" found in vocabulary data but missing from systemRegistry in systems.ts`
        );
      }
    }
  }

  // Sort each system's vocabs alphabetically
  for (const entries of Object.values(index)) {
    entries.sort((a, b) => a.vocabId.localeCompare(b.vocabId));
  }

  return index;
}

const GITHUB_REPO = "https://github.com/PublicSchema/publicschema.org";

export function getIssueUrl(systemName: string): string {
  const title = encodeURIComponent(`Mapping review: ${systemName}`);
  const body = encodeURIComponent(
    `## System: ${systemName}\n\n` +
    `**Reviewed by:** (your name / organization)\n` +
    `**Date:** (today)\n\n` +
    `### Issues found\n\n` +
    `(Describe any incorrect mappings, missing values, or other problems)\n\n` +
    `### Confirmed correct\n\n` +
    `- [ ] I have reviewed all vocabulary mappings for ${systemName} and confirm the above are the only issues.`
  );
  return `${GITHUB_REPO}/issues/new?title=${title}&body=${body}`;
}
