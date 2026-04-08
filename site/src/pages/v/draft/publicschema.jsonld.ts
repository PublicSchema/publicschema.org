import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export function GET() {
  const filePath = resolve(process.cwd(), "../dist/publicschema.jsonld");
  const content = readFileSync(filePath, "utf-8");

  return new Response(content, {
    headers: {
      "Content-Type": "application/ld+json",
    },
  });
}
