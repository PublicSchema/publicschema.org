/**
 * JSON-LD representations for concepts and properties.
 * Mirrors the catch-all HTML route: /Person.jsonld, /sp/Enrollment.jsonld, /given_name.jsonld, etc.
 */
import { loadVocabulary } from "../data/vocabulary";
import type { Concept, Property } from "../data/vocabulary";

const CONTEXT = "https://publicschema.org/ctx/v0.1";

/** Append .jsonld so the URI dereferences on static hosts (no content negotiation). */
function jsonldUrl(uri: string): string {
  return uri + ".jsonld";
}

export function getStaticPaths() {
  const vocab = loadVocabulary();
  const paths = [];

  for (const [id, concept] of Object.entries(vocab.concepts)) {
    const slug = concept.path.replace(/^\//, "");
    paths.push({ params: { slug }, props: { kind: "concept" as const, termId: id } });
  }
  for (const [id, prop] of Object.entries(vocab.properties)) {
    const slug = prop.path.replace(/^\//, "");
    paths.push({ params: { slug }, props: { kind: "property" as const, termId: id } });
  }

  return paths;
}

function conceptToJsonLd(concept: Concept, vocab: ReturnType<typeof loadVocabulary>) {
  const doc: Record<string, unknown> = {
    "@context": CONTEXT,
    "@id": jsonldUrl(concept.uri),
    "@type": "rdfs:Class",
    "rdfs:label": concept.id,
    "rdfs:comment": concept.definition.en,
    "schema:maturity": concept.maturity,
  };

  if (concept.definition.fr) {
    doc["rdfs:comment_fr"] = concept.definition.fr;
  }
  if (concept.definition.es) {
    doc["rdfs:comment_es"] = concept.definition.es;
  }

  if (concept.domain) {
    doc["schema:domain"] = concept.domain;
  }

  if (concept.supertypes.length > 0) {
    doc["rdfs:subClassOf"] = concept.supertypes.map((s) => {
      const parent = vocab.concepts[s];
      return parent ? jsonldUrl(parent.uri) : s;
    });
  }

  if (concept.subtypes.length > 0) {
    doc["schema:subtypes"] = concept.subtypes.map((s) => {
      const child = vocab.concepts[s];
      return child ? jsonldUrl(child.uri) : s;
    });
  }

  if (concept.properties.length > 0) {
    doc["schema:properties"] = concept.properties.map((ref) => {
      const prop = vocab.properties[ref.id];
      if (!prop) return { "@id": ref.id };
      return embeddedPropertyJsonLd(prop, vocab);
    });
  }

  return doc;
}

/** Build a property object for embedding inside a concept document (no @context, no domainIncludes). */
function embeddedPropertyJsonLd(prop: Property, vocab: ReturnType<typeof loadVocabulary>) {
  const entry: Record<string, unknown> = {
    "@id": jsonldUrl(prop.uri),
    "@type": "rdf:Property",
    "rdfs:label": prop.id,
    "rdfs:comment": prop.definition.en,
    "schema:maturity": prop.maturity,
    "schema:rangeIncludes": prop.type,
    "schema:cardinality": prop.cardinality,
  };

  if (prop.definition.fr) {
    entry["rdfs:comment_fr"] = prop.definition.fr;
  }
  if (prop.definition.es) {
    entry["rdfs:comment_es"] = prop.definition.es;
  }

  if (prop.vocabulary) {
    const vocabEntry = vocab.vocabularies[prop.vocabulary];
    entry["schema:vocabulary"] = vocabEntry ? jsonldUrl(vocabEntry.uri) : prop.vocabulary;
  }

  if (prop.references) {
    const refConcept = vocab.concepts[prop.references];
    entry["schema:references"] = refConcept ? jsonldUrl(refConcept.uri) : prop.references;
  }

  if (prop.data_classification) {
    entry["schema:dataClassification"] = prop.data_classification;
  }

  return entry;
}

function propertyToJsonLd(prop: Property, vocab: ReturnType<typeof loadVocabulary>) {
  const doc: Record<string, unknown> = {
    "@context": CONTEXT,
    "@id": jsonldUrl(prop.uri),
    "@type": "rdf:Property",
    "rdfs:label": prop.id,
    "rdfs:comment": prop.definition.en,
    "schema:maturity": prop.maturity,
    "schema:rangeIncludes": prop.type,
    "schema:cardinality": prop.cardinality,
  };

  if (prop.definition.fr) {
    doc["rdfs:comment_fr"] = prop.definition.fr;
  }
  if (prop.definition.es) {
    doc["rdfs:comment_es"] = prop.definition.es;
  }

  if (prop.vocabulary) {
    const vocabEntry = vocab.vocabularies[prop.vocabulary];
    doc["schema:vocabulary"] = vocabEntry ? jsonldUrl(vocabEntry.uri) : prop.vocabulary;
  }

  if (prop.references) {
    const refConcept = vocab.concepts[prop.references];
    doc["schema:references"] = refConcept ? jsonldUrl(refConcept.uri) : prop.references;
  }

  if (prop.used_by.length > 0) {
    doc["schema:domainIncludes"] = prop.used_by.map((id) => {
      const concept = vocab.concepts[id];
      return concept ? jsonldUrl(concept.uri) : id;
    });
  }

  return doc;
}

export function GET({ props }: { props: { kind: "concept" | "property"; termId: string } }) {
  const vocab = loadVocabulary();
  const { kind, termId } = props;

  const doc =
    kind === "concept"
      ? conceptToJsonLd(vocab.concepts[termId], vocab)
      : propertyToJsonLd(vocab.properties[termId], vocab);

  return new Response(JSON.stringify(doc, null, 2), {
    headers: { "Content-Type": "application/ld+json" },
  });
}
