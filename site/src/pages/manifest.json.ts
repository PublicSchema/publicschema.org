import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export function GET() {
  const manifestPath = resolve(process.cwd(), "../dist/manifest.json");
  const manifest = readFileSync(manifestPath, "utf-8");

  return new Response(manifest, {
    headers: {
      "Content-Type": "application/json",
    },
  });
}
