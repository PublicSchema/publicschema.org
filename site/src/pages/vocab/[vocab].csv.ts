/**
 * CSV download for vocabulary value sets.
 * /vocab/gender-type.csv, /vocab/enrollment-status.csv, etc.
 */
import { loadVocabulary } from "../../data/vocabulary";

function escapeCsv(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return '"' + value.replace(/"/g, '""') + '"';
  }
  return value;
}

export function getStaticPaths() {
  const vocab = loadVocabulary();
  return Object.keys(vocab.vocabularies).map((id) => ({ params: { vocab: id } }));
}

export function GET({ params }: { params: { vocab: string } }) {
  const allVocab = loadVocabulary();
  const vocabulary = allVocab.vocabularies[params.vocab];

  const headers = ["code", "label_en", "label_fr", "label_es", "standard_code", "uri", "definition_en"];
  const rows = vocabulary.values.map((v) =>
    [
      v.code,
      v.label.en || "",
      v.label.fr || "",
      v.label.es || "",
      v.standard_code || "",
      v.uri,
      v.definition.en || "",
    ]
      .map(escapeCsv)
      .join(",")
  );

  const csv = [headers.join(","), ...rows].join("\n");

  return new Response(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": `attachment; filename="${params.vocab}.csv"`,
    },
  });
}
