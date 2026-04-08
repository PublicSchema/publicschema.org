/**
 * JSON-LD representations for concepts and properties.
 * Serves pre-built JSON-LD files from dist/jsonld/.
 *
 * Concepts live under dist/jsonld/concepts/ and properties under
 * dist/jsonld/properties/ to avoid case collisions on case-insensitive
 * filesystems (e.g. Address concept vs address property on macOS).
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { loadVocabulary } from "../data/vocabulary";

export function getStaticPaths() {
  const vocab = loadVocabulary();
  const paths = [];

  for (const [id, concept] of Object.entries(vocab.concepts)) {
    const slug = concept.path.replace(/^\//, "");
    paths.push({ params: { slug }, props: { kind: "concept" as const } });
  }
  for (const [id, prop] of Object.entries(vocab.properties)) {
    const slug = prop.path.replace(/^\//, "");
    paths.push({ params: { slug }, props: { kind: "property" as const } });
  }

  return paths;
}

export function GET({ params, props }: { params: { slug: string }; props: { kind: "concept" | "property" } }) {
  const subdir = props.kind === "concept" ? "concepts" : "properties";
  const filePath = resolve(process.cwd(), `../dist/jsonld/${subdir}/${params.slug}.jsonld`);
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
