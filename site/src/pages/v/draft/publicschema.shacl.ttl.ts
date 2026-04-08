import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export function GET() {
  const filePath = resolve(process.cwd(), "../dist/publicschema.shacl.ttl");
  const content = readFileSync(filePath, "utf-8");

  return new Response(content, {
    headers: {
      "Content-Type": "text/turtle",
    },
  });
}
