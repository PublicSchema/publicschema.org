/**
 * JSON-LD representations for vocabularies.
 * Serves pre-built JSON-LD files from dist/jsonld/vocab/.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { loadVocabulary } from "../../data/vocabulary";

export function getStaticPaths() {
  const vocab = loadVocabulary();
  return Object.keys(vocab.vocabularies).map((id) => ({ params: { vocab: id } }));
}

export function GET({ params }: { params: { vocab: string } }) {
  const filePath = resolve(process.cwd(), `../dist/jsonld/vocab/${params.vocab}.jsonld`);
  try {
    const content = readFileSync(filePath, "utf-8");
    return new Response(content, {
      headers: { "Content-Type": "application/ld+json" },
    });
  } catch {
    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  }
}
