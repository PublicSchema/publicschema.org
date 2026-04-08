import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export function GET() {
  const contextPath = resolve(process.cwd(), "../dist/context.jsonld");
  const context = readFileSync(contextPath, "utf-8");

  return new Response(context, {
    headers: {
      "Content-Type": "application/ld+json",
    },
  });
}
