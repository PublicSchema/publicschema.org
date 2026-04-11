import { loadVocabulary } from "../data/vocabulary";
import { docs } from "../data/docs";

interface SearchDocument {
  id: string;
  type: string;
  title: string;
  body: string;
  path: string;
  meta: string;
  keywords: string;
}

function truncate(text: string, maxLength: number): string {
  const trimmed = text.trim().replace(/\n/g, " ");
  if (trimmed.length <= maxLength) return trimmed;
  return trimmed.slice(0, maxLength).trimEnd() + "...";
}

export function GET() {
  const vocab = loadVocabulary();
  const documents: SearchDocument[] = [];

  // Concepts
  for (const concept of Object.values(vocab.concepts)) {
    documents.push({
      id: `concept:${concept.id}`,
      type: "concept",
      title: concept.id,
      body: truncate(concept.definition.en || "", 200),
      path: concept.path,
      meta: concept.domain ? `Domain: ${concept.domain}` : "",
      keywords: concept.properties.map((p) => p.id).join(" "),
    });
  }

  // Properties
  for (const prop of Object.values(vocab.properties)) {
    const usedByList = prop.used_by || [];
    documents.push({
      id: `property:${prop.id}`,
      type: "property",
      title: prop.id,
      body: truncate(prop.definition.en || "", 200),
      path: prop.path,
      meta: usedByList.length > 0 ? `Used by: ${usedByList.join(", ")}` : "",
      keywords: usedByList.join(" "),
    });
  }

  // Vocabularies
  for (const v of Object.values(vocab.vocabularies)) {
    const valueLabels: string[] = [];
    if (!v.external_values) {
      for (const val of v.values) {
        if (val.label?.en) {
          valueLabels.push(val.label.en);
        }
      }
    }
    const valueCount = v.values.length;

    documents.push({
      id: `vocab:${v.id}`,
      type: "vocabulary",
      title: v.id,
      body: truncate(v.definition.en || "", 200),
      path: `/vocab/${v.id}`,
      meta: `${valueCount} values`,
      keywords: valueLabels.join("\t"),
    });
  }

  // Docs
  for (const [slug, doc] of Object.entries(docs)) {
    documents.push({
      id: `doc:${slug}`,
      type: "doc",
      title: doc.title,
      body: truncate(doc.description, 200),
      path: `/docs/${slug}/`,
      meta: doc.category,
      keywords: "",
    });
  }

  return new Response(JSON.stringify(documents), {
    headers: {
      "Content-Type": "application/json",
    },
  });
}
