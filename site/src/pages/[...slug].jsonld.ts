/**
 * JSON-LD representations for concepts and properties.
 * Serves pre-built JSON-LD files from dist/jsonld/.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { loadVocabulary } from "../data/vocabulary";

export function getStaticPaths() {
  const vocab = loadVocabulary();
  const paths = [];

  for (const [id, concept] of Object.entries(vocab.concepts)) {
    const slug = concept.path.replace(/^\//, "");
    paths.push({ params: { slug } });
  }
  for (const [id, prop] of Object.entries(vocab.properties)) {
    const slug = prop.path.replace(/^\//, "");
    paths.push({ params: { slug } });
  }

  return paths;
}

export function GET({ params }: { params: { slug: string } }) {
  const filePath = resolve(process.cwd(), `../dist/jsonld/${params.slug}.jsonld`);
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
