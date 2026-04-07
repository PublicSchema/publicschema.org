/**
 * JSON-LD representations for vocabularies.
 * /vocab/gender-type.jsonld, /vocab/enrollment-status.jsonld, etc.
 */
import { loadVocabulary } from "../../data/vocabulary";
import type { Vocabulary } from "../../data/vocabulary";

const CONTEXT = "https://publicschema.org/ctx/v0.1";

function vocabularyToJsonLd(vocabulary: Vocabulary) {
  const doc: Record<string, unknown> = {
    "@context": CONTEXT,
    "@id": vocabulary.uri,
    "@type": "skos:ConceptScheme",
    "rdfs:label": vocabulary.id,
    "rdfs:comment": vocabulary.definition.en,
    "schema:maturity": vocabulary.maturity,
  };

  if (vocabulary.definition.fr) {
    doc["rdfs:comment_fr"] = vocabulary.definition.fr;
  }
  if (vocabulary.definition.es) {
    doc["rdfs:comment_es"] = vocabulary.definition.es;
  }

  if (vocabulary.domain) {
    doc["schema:domain"] = vocabulary.domain;
  }

  if (vocabulary.standard) {
    doc["schema:standardReference"] = {
      "schema:name": vocabulary.standard.name,
      ...(vocabulary.standard.uri ? { "@id": vocabulary.standard.uri } : {}),
      ...(vocabulary.standard.notes ? { "schema:notes": vocabulary.standard.notes } : {}),
    };
  }

  if (vocabulary.values.length > 0) {
    doc["skos:hasTopConcept"] = vocabulary.values.map((v) => {
      const entry: Record<string, unknown> = {
        "@id": v.uri,
        "@type": "skos:Concept",
        "skos:notation": v.code,
        "skos:prefLabel": v.label.en,
        "skos:definition": v.definition.en,
      };
      if (v.standard_code) {
        entry["schema:standardCode"] = v.standard_code;
      }
      if (v.label.fr) entry["skos:prefLabel_fr"] = v.label.fr;
      if (v.label.es) entry["skos:prefLabel_es"] = v.label.es;
      return entry;
    });
  }

  return doc;
}

export function getStaticPaths() {
  const vocab = loadVocabulary();
  return Object.keys(vocab.vocabularies).map((id) => ({ params: { vocab: id } }));
}

export function GET({ params }: { params: { vocab: string } }) {
  const allVocab = loadVocabulary();
  const vocabulary = allVocab.vocabularies[params.vocab];
  const doc = vocabularyToJsonLd(vocabulary);

  return new Response(JSON.stringify(doc, null, 2), {
    headers: { "Content-Type": "application/ld+json" },
  });
}
