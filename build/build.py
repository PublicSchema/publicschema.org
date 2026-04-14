"""Builds PublicSchema outputs from YAML source files.

Reads all YAML files from schema/ and generates:
1. vocabulary.json: full vocabulary as structured JSON
2. context.jsonld: JSON-LD context mapping IDs to URIs
3. schemas/*.schema.json: one JSON Schema per concept (for VC validation)
4. jsonld/*.jsonld: per-concept, per-property, per-vocabulary JSON-LD documents
"""

import json
import re
import sys
from pathlib import Path

import yaml


# Type mappings from YAML types to JSON Schema
TYPE_MAP = {
    "string": {"type": "string"},
    "date": {"type": "string", "format": "date"},
    "datetime": {"type": "string", "format": "date-time"},
    "integer": {"type": "integer"},
    "decimal": {"type": "number"},
    "boolean": {"type": "boolean"},
    "uri": {"type": "string", "format": "uri"},
    "geojson_geometry": {"$ref": "https://geojson.org/schema/Geometry.json"},
}

# Type mappings from YAML types to JSON-LD @type coercion values.
# Only non-string types need coercion; plain strings are left as bare URIs.
JSONLD_TYPE_COERCION = {
    "date": "xsd:date",
    "datetime": "xsd:dateTime",
    "integer": "xsd:integer",
    "decimal": "xsd:decimal",
    "boolean": "xsd:boolean",
    "uri": "@id",
    "geojson_geometry": "@json",
}


# Type mappings from YAML types to JSON-LD rangeIncludes values
RANGE_INCLUDES_MAP = {
    "string": "xsd:string",
    "date": "xsd:date",
    "datetime": "xsd:dateTime",
    "integer": "xsd:integer",
    "decimal": "xsd:decimal",
    "boolean": "xsd:boolean",
    "uri": "xsd:anyURI",
    "geojson_geometry": "https://purl.org/geojson/vocab#Geometry",
}


# Map external_equivalents match values to RDF predicates.
# SKOS match predicates are the standard for asserting equivalences between
# concepts in different schemes. rdfs:seeAlso is the safe fallback when
# the match type is not specified.
MATCH_PREDICATES = {
    "exact": "skos:exactMatch",
    "close": "skos:closeMatch",
    "broad": "skos:broadMatch",
    "narrow": "skos:narrowMatch",
    "related": "skos:relatedMatch",
}
MATCH_FALLBACK = "rdfs:seeAlso"


def _external_equivalents_triples(raw_data: dict) -> dict[str, list[str]]:
    """Extract RDF match triples from an entity's external_equivalents.

    Returns a dict mapping predicate terms (e.g. "skos:exactMatch") to
    lists of URIs. Suitable for merging directly into a JSON-LD node.
    """
    equivalents = raw_data.get("external_equivalents")
    if not equivalents:
        return {}
    entity_id = raw_data.get("id", "<unknown>")
    triples: dict[str, list[str]] = {}
    for system, entry in equivalents.items():
        uri = entry.get("uri")
        if not uri:
            print(
                f"WARNING: external_equivalents[{system}] on {entity_id} "
                f"is missing 'uri' field, skipping",
                file=sys.stderr,
            )
            continue
        match_type = entry.get("match")
        predicate = MATCH_PREDICATES.get(match_type, MATCH_FALLBACK)
        triples.setdefault(predicate, []).append(uri)
    return triples


def _to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case. e.g. PaymentEvent -> payment_event."""
    return re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name).lower()


def _language_tagged(texts: dict) -> list[dict]:
    """Build a list of JSON-LD language-tagged value objects from a {lang: text} dict."""
    return [
        {"@value": text, "@language": lang}
        for lang, text in texts.items()
        if text
    ]


def _resolve_range_includes(
    prop_type: str, out_concepts: dict[str, dict],
) -> str:
    """Map a property type to a JSON-LD rangeIncludes value."""
    if prop_type.startswith("concept:"):
        ref_id = prop_type.split(":", 1)[1]
        if ref_id in out_concepts:
            return out_concepts[ref_id]["uri"]
        return ref_id
    return RANGE_INCLUDES_MAP.get(prop_type, "xsd:string")


def _concept_property_jsonld(
    prop_out: dict, prop_raw: dict, concept_uri: str,
    out_concepts: dict, out_vocabularies: dict,
) -> dict:
    """Build a property node for inclusion in a concept's @graph array."""
    prop_type = prop_raw.get("type", "string")
    entry: dict = {
        "@id": prop_out["uri"],
        "@type": "rdf:Property",
        "rdfs:label": prop_out["id"],
        "rdfs:comment": _language_tagged(prop_raw.get("definition", {})),
        "ps:maturity": prop_out["maturity"],
        "schema:domainIncludes": {"@id": concept_uri},
        "schema:rangeIncludes": _resolve_range_includes(prop_type, out_concepts),
        "ps:cardinality": prop_out.get("cardinality"),
    }
    if prop_out.get("vocabulary"):
        vocab = out_vocabularies.get(prop_out["vocabulary"])
        entry["ps:vocabulary"] = vocab["uri"] if vocab else prop_out["vocabulary"]
    if prop_raw.get("references"):
        ref_concept = out_concepts.get(prop_raw["references"])
        entry["ps:references"] = ref_concept["uri"] if ref_concept else prop_raw["references"]
    for predicate, uris in _external_equivalents_triples(prop_raw).items():
        entry[predicate] = uris if len(uris) > 1 else uris[0]
    return entry


def _concept_to_jsonld(
    concept_out: dict, concept_raw: dict, context_url: str,
    out_concepts: dict, out_properties: dict, properties_raw: dict,
    out_vocabularies: dict,
) -> dict:
    """Build a JSON-LD document for a concept using a @graph array.

    The concept class node and its property nodes are peers in the graph,
    linked by schema:domainIncludes on each property. This follows the
    schema.org pattern and produces standard RDF triples.
    """
    concept_node: dict = {
        "@id": concept_out["uri"],
        "@type": "rdfs:Class",
        "rdfs:label": concept_out["id"],
        "rdfs:comment": _language_tagged(concept_raw.get("definition", {})),
        "ps:maturity": concept_out["maturity"],
    }
    if concept_out.get("domain"):
        concept_node["ps:domain"] = concept_out["domain"]
    if concept_out.get("abstract"):
        concept_node["ps:abstract"] = True
    supertypes = concept_out.get("supertypes", [])
    if supertypes:
        concept_node["rdfs:subClassOf"] = [
            out_concepts[s]["uri"] if s in out_concepts else s
            for s in supertypes
        ]
    subtypes = concept_out.get("subtypes", [])
    if subtypes:
        concept_node["ps:subtypes"] = [
            out_concepts[s]["uri"] if s in out_concepts else s
            for s in subtypes
        ]
    for predicate, uris in _external_equivalents_triples(concept_raw).items():
        concept_node[predicate] = uris if len(uris) > 1 else uris[0]
    graph = [concept_node]
    props = concept_out.get("properties", [])
    if props:
        for ref in props:
            if ref["id"] in out_properties and ref["id"] in properties_raw:
                graph.append(
                    _concept_property_jsonld(
                        out_properties[ref["id"]], properties_raw[ref["id"]],
                        concept_out["uri"], out_concepts, out_vocabularies,
                    )
                )
    return {"@context": context_url, "@graph": graph}


def _property_to_jsonld(
    prop_out: dict, prop_raw: dict, context_url: str,
    out_concepts: dict, out_vocabularies: dict,
) -> dict:
    """Build a complete JSON-LD document for a standalone property."""
    prop_type = prop_raw.get("type", "string")
    doc: dict = {
        "@context": context_url,
        "@id": prop_out["uri"],
        "@type": "rdf:Property",
        "rdfs:label": prop_out["id"],
        "rdfs:comment": _language_tagged(prop_raw.get("definition", {})),
        "ps:maturity": prop_out["maturity"],
        "schema:rangeIncludes": _resolve_range_includes(prop_type, out_concepts),
        "ps:cardinality": prop_out.get("cardinality"),
    }
    if prop_out.get("vocabulary"):
        vocab = out_vocabularies.get(prop_out["vocabulary"])
        doc["ps:vocabulary"] = vocab["uri"] if vocab else prop_out["vocabulary"]
    if prop_raw.get("references"):
        ref_concept = out_concepts.get(prop_raw["references"])
        doc["ps:references"] = ref_concept["uri"] if ref_concept else prop_raw["references"]
    for predicate, uris in _external_equivalents_triples(prop_raw).items():
        doc[predicate] = uris if len(uris) > 1 else uris[0]
    used_by = prop_out.get("used_by", [])
    if used_by:
        doc["schema:domainIncludes"] = [
            out_concepts[cid]["uri"] if cid in out_concepts else cid
            for cid in used_by
        ]
    return doc


def _vocabulary_to_jsonld(
    vocab_out: dict, vocab_raw: dict, context_url: str,
) -> dict:
    """Build a complete JSON-LD document for a vocabulary using SKOS."""
    doc: dict = {
        "@context": context_url,
        "@id": vocab_out["uri"],
        "@type": "skos:ConceptScheme",
        "rdfs:label": vocab_out["id"],
        "rdfs:comment": _language_tagged(vocab_raw.get("definition", {})),
        "ps:maturity": vocab_out["maturity"],
    }
    if vocab_out.get("domain"):
        doc["ps:domain"] = vocab_out["domain"]
    for predicate, uris in _external_equivalents_triples(vocab_raw).items():
        doc[predicate] = uris if len(uris) > 1 else uris[0]
    standard = vocab_raw.get("standard")
    if standard:
        std_entry: dict = {"schema:name": standard.get("name", "")}
        if standard.get("uri"):
            std_entry["@id"] = standard["uri"]
        if standard.get("notes"):
            std_entry["ps:notes"] = standard["notes"]
        doc["ps:standardReference"] = std_entry
    values = vocab_out.get("values", [])
    if values:
        doc["skos:hasTopConcept"] = []
        for v in values:
            entry: dict = {
                "@id": v["uri"],
                "@type": "skos:Concept",
                "skos:notation": v["code"],
                "skos:prefLabel": _language_tagged(v.get("label", {})),
                "skos:definition": _language_tagged(v.get("definition", {})),
            }
            if v.get("standard_code"):
                entry["ps:standardCode"] = v["standard_code"]
            doc["skos:hasTopConcept"].append(entry)
    return doc


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _load_all_yaml(directory: Path) -> dict[str, dict]:
    result = {}
    if not directory.exists():
        return result
    for p in sorted(directory.rglob("*.yaml")):
        data = _load_yaml(p)
        if "id" in data:
            result[data["id"]] = data
    return result


def _load_vocabularies_indexed(directory: Path) -> dict[str, dict]:
    """Load vocabulary YAMLs keyed by their canonical reference form.

    Domain-scoped vocabularies are keyed as ``<domain>/<id>`` (matching how
    properties reference them and how the web page URLs are laid out).
    Universal vocabularies are keyed by bare ``<id>``. The domain is read
    from the YAML ``domain`` field.
    """
    result = {}
    if not directory.exists():
        return result
    for p in sorted(directory.rglob("*.yaml")):
        data = _load_yaml(p)
        if "id" not in data:
            continue
        domain = data.get("domain")
        key = f"{domain}/{data['id']}" if domain else data["id"]
        result[key] = data
    return result


def _normalize_property_entry(entry) -> dict:
    """Normalize a property entry to {id}."""
    if isinstance(entry, str):
        return {"id": entry}
    return {"id": entry["id"]}


def _collect_all_properties(concept_id: str, concepts_raw: dict) -> list:
    """Collect property entries from a concept and all its supertypes."""
    visited = set()
    all_props = []
    seen_ids = set()

    def walk(cid):
        if cid in visited or cid not in concepts_raw:
            return
        visited.add(cid)
        concept = concepts_raw[cid]
        for st in concept.get("supertypes", []):
            walk(st)
        for entry in concept.get("properties", []):
            norm = _normalize_property_entry(entry)
            if norm["id"] not in seen_ids:
                seen_ids.add(norm["id"])
                all_props.append(entry)

    walk(concept_id)
    return all_props


def _compute_uri(base_uri: str, domain: str | None, id_str: str) -> str:
    """Compute a URI with optional domain namespace segment."""
    if domain:
        return f"{base_uri}{domain}/{id_str}"
    return f"{base_uri}{id_str}"


def _compute_path(domain: str | None, id_str: str) -> str:
    """Compute a URL path with optional domain namespace segment."""
    if domain:
        return f"/{domain}/{id_str}"
    return f"/{id_str}"


def _compute_property_domain_namespace(
    prop_id: str,
    concepts_raw: dict[str, dict],
    properties_raw: dict[str, dict] | None = None,
) -> str | None:
    """Derive a property's domain namespace from the concepts that use it.

    If the property has an explicit ``domain_override`` field, that value
    is used directly (None for universal, a domain code for domain-specific).
    Otherwise, if all concepts using this property share the same non-null
    domain, the property gets that domain. Otherwise it's universal (None).
    """
    # Check for explicit override in the property's source YAML
    if properties_raw and prop_id in properties_raw:
        prop_data = properties_raw[prop_id]
        if "domain_override" in prop_data:
            return prop_data["domain_override"]

    domains = set()
    for concept_data in concepts_raw.values():
        for entry in concept_data.get("properties", []):
            pid = entry["id"] if isinstance(entry, dict) else entry
            if pid == prop_id:
                domains.add(concept_data.get("domain"))
    # Only assign a domain if all using concepts share exactly one non-null domain
    if len(domains) == 1:
        sole_domain = next(iter(domains))
        if sole_domain is not None:
            return sole_domain
    return None


def _property_to_json_schema(
    prop_data: dict, vocabularies: dict, out_vocabularies: dict | None = None,
) -> dict:
    """Convert a property definition to a JSON Schema property definition."""
    prop_type = prop_data.get("type", "string")
    cardinality = prop_data.get("cardinality", "single")
    vocab_ref = prop_data.get("vocabulary")

    # If property has a vocabulary, generate enum constraint
    if vocab_ref and vocab_ref in vocabularies:
        vocab = vocabularies[vocab_ref]
        codes = [v["code"] for v in vocab.get("values", [])]
        item_schema: dict = {"type": "string", "enum": codes}
        # Link to the vocabulary URI so consumers can discover full semantics
        if out_vocabularies and vocab_ref in out_vocabularies:
            item_schema["$comment"] = out_vocabularies[vocab_ref]["uri"]
    elif prop_type.startswith("concept:"):
        # Reference to another concept: accept object or string
        item_schema = {"type": ["object", "string"]}
    else:
        item_schema = dict(TYPE_MAP.get(prop_type, {"type": "string"}))

    if cardinality == "multiple":
        return {"type": "array", "items": item_schema}
    return item_schema


def build_vocabulary(schema_dir: Path) -> dict:
    """Build the full vocabulary output from YAML source files.

    Returns a dict with keys: meta, concepts, properties, vocabularies,
    context, concept_schemas.
    """
    meta = _load_yaml(schema_dir / "_meta.yaml")
    base_uri = meta.get("base_uri", "https://publicschema.org/")

    concepts_raw = _load_all_yaml(schema_dir / "concepts")
    properties_raw = _load_all_yaml(schema_dir / "properties")
    vocabularies_raw = _load_vocabularies_indexed(schema_dir / "vocabularies")
    bibliography_raw = _load_all_yaml(schema_dir / "bibliography")
    categories_path = schema_dir / "categories.yaml"
    categories_raw = _load_yaml(categories_path) if categories_path.exists() else {}

    # Compute property domains (which concepts use each property)
    property_domains: dict[str, list[str]] = {
        pid: [] for pid in properties_raw
    }
    for concept_id, concept_data in concepts_raw.items():
        for entry in concept_data.get("properties", []):
            prop_id = entry["id"] if isinstance(entry, dict) else entry
            if prop_id in property_domains:
                property_domains[prop_id].append(concept_id)

    # Build output concepts
    out_concepts = {}
    for concept_id, data in concepts_raw.items():
        domain = data.get("domain")
        out_concepts[concept_id] = {
            "id": concept_id,
            "domain": domain,
            "uri": _compute_uri(base_uri, domain, concept_id),
            "path": _compute_path(domain, concept_id),
            "maturity": data.get("maturity"),
            "abstract": data.get("abstract", False),
            "featured": bool(data.get("featured", False)),
            "label": data.get("label", {}),
            "definition": data.get("definition", {}),
            "properties": [
                _normalize_property_entry(e)
                for e in data.get("properties", [])
            ],
            "subtypes": data.get("subtypes", []),
            "supertypes": data.get("supertypes", []),
            "convergence": data.get("convergence"),
            "external_equivalents": data.get("external_equivalents"),
            "property_groups": data.get("property_groups"),
        }

    # Build output properties
    out_properties = {}
    for prop_id, data in properties_raw.items():
        prop_ns = _compute_property_domain_namespace(prop_id, concepts_raw, properties_raw)
        out_properties[prop_id] = {
            "id": prop_id,
            "uri": _compute_uri(base_uri, prop_ns, prop_id),
            "path": _compute_path(prop_ns, prop_id),
            "maturity": data.get("maturity"),
            "definition": data.get("definition", {}),
            "type": data.get("type"),
            "cardinality": data.get("cardinality"),
            "vocabulary": data.get("vocabulary"),
            "references": data.get("references"),
            "used_by": property_domains.get(prop_id, []),
            "schema_org_equivalent": data.get("schema_org_equivalent"),
            "sensitivity": data.get("sensitivity"),
            "system_mappings": data.get("system_mappings"),
            "external_equivalents": data.get("external_equivalents"),
            "convergence": data.get("convergence"),
            "category": data.get("category"),
            "age_applicability": data.get("age_applicability"),
            "valid_instruments": data.get("valid_instruments"),
        }

    # Build output vocabularies. Vocabularies are keyed by their canonical
    # reference form: '<domain>/<id>' for domain-scoped vocabularies,
    # bare '<id>' for universal ones. The key format matches how properties
    # reference the vocabulary (property's `vocabulary:` field) and how
    # the site route at /<domain>/vocab/<id> or /vocab/<id> is laid out.
    out_vocabularies = {}
    for vocab_key, data in vocabularies_raw.items():
        vocab_id = data["id"]
        vocab_ns = data.get("domain")
        # Vocabulary URI/path are /vocab/<domain>/<id> for domain-scoped vocabs
        # and /vocab/<id> for universal. This keeps all vocabularies under a
        # single /vocab/ namespace on the site while preserving the domain
        # segment to prevent cross-domain name collisions.
        vocab_base = f"{base_uri}vocab/{vocab_key}"
        vocab_path = f"/vocab/{vocab_key}"
        values = []
        for v in data.get("values", []):
            value_out = {
                "code": v["code"],
                "uri": f"{vocab_base}/{v['code']}",
                "label": v.get("label", {}),
                "standard_code": v.get("standard_code"),
                "definition": v.get("definition", {}),
            }
            if v.get("level") is not None:
                value_out["level"] = v["level"]
            if v.get("parent_code") is not None:
                value_out["parent_code"] = v["parent_code"]
            values.append(value_out)
        out_vocabularies[vocab_key] = {
            "id": vocab_id,
            "domain": vocab_ns,
            "uri": vocab_base,
            "path": vocab_path,
            "maturity": data.get("maturity"),
            "label": data.get("label", {}),
            "definition": data.get("definition", {}),
            "standard": data.get("standard"),
            "values": values,
            "system_mappings": data.get("system_mappings"),
            "external_equivalents": data.get("external_equivalents"),
            "same_standard_systems": data.get("same_standard_systems"),
            "external_values": data.get("external_values", False),
            "references": data.get("references", []),
        }

    # Build bibliography output and reverse indexes. Each entry's `informs`
    # block points at concepts/vocabularies/properties; we mirror those edges
    # back onto each entity as `bibliography_refs` so the site can render
    # per-entity reference sections without re-scanning the whole catalog.
    out_bibliography = {}
    concept_bib_refs: dict[str, list[str]] = {cid: [] for cid in out_concepts}
    vocab_bib_refs: dict[str, list[str]] = {vid: [] for vid in out_vocabularies}
    property_bib_refs: dict[str, list[str]] = {pid: [] for pid in out_properties}

    for bib_id, data in bibliography_raw.items():
        informs = data.get("informs") or {"concepts": [], "vocabularies": [], "properties": []}
        out_bibliography[bib_id] = {
            "id": bib_id,
            "title": data.get("title"),
            "short_title": data.get("short_title"),
            "standard_number": data.get("standard_number"),
            "publisher": data.get("publisher"),
            "authors": data.get("authors", []),
            "year": data.get("year"),
            "version": data.get("version"),
            "type": data.get("type"),
            "domain": data.get("domain"),
            "uri": data.get("uri"),
            "access": data.get("access"),
            "status": data.get("status"),
            "informs": {
                "concepts": list(informs.get("concepts", [])),
                "vocabularies": list(informs.get("vocabularies", [])),
                "properties": list(informs.get("properties", [])),
            },
        }
        for cid in informs.get("concepts", []):
            if cid in concept_bib_refs:
                concept_bib_refs[cid].append(bib_id)
            else:
                print(
                    f"WARNING: bibliography {bib_id!r} informs concept {cid!r} which is not defined",
                    file=sys.stderr,
                )
        for vid in informs.get("vocabularies", []):
            if vid in vocab_bib_refs:
                vocab_bib_refs[vid].append(bib_id)
            else:
                print(
                    f"WARNING: bibliography {bib_id!r} informs vocabulary {vid!r} which is not defined",
                    file=sys.stderr,
                )
        for pid in informs.get("properties", []):
            if pid in property_bib_refs:
                property_bib_refs[pid].append(bib_id)
            else:
                print(
                    f"WARNING: bibliography {bib_id!r} informs property {pid!r} which is not defined",
                    file=sys.stderr,
                )

    for cid, refs in concept_bib_refs.items():
        out_concepts[cid]["bibliography_refs"] = sorted(refs)
    for vid, refs in vocab_bib_refs.items():
        out_vocabularies[vid]["bibliography_refs"] = sorted(refs)
    for pid, refs in property_bib_refs.items():
        out_properties[pid]["bibliography_refs"] = sorted(refs)

    # Build JSON-LD context. Concept URIs are bare (the HTML page URL IS the
    # concept URI, following the schema.org pattern). The .jsonld representation
    # is discoverable via <link rel="alternate"> on the HTML page.
    context_map: dict[str, object] = {
        "@vocab": base_uri,
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "schema": "https://schema.org/",
        "ps": "https://publicschema.org/meta/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "type": "@type",
    }
    # URI-valued predicates need @type:@id so JSON-LD processors
    # treat values as URI references, not plain strings.
    context_map["schema:domainIncludes"] = {
        "@id": "https://schema.org/domainIncludes",
        "@type": "@id",
    }
    context_map["schema:rangeIncludes"] = {
        "@id": "https://schema.org/rangeIncludes",
        "@type": "@id",
    }
    context_map["rdfs:subClassOf"] = {
        "@id": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
        "@type": "@id",
        "@container": "@set",
    }
    context_map["ps:subtypes"] = {
        "@id": "https://publicschema.org/meta/subtypes",
        "@type": "@id",
        "@container": "@set",
    }
    context_map["ps:references"] = {
        "@id": "https://publicschema.org/meta/references",
        "@type": "@id",
    }
    context_map["ps:vocabulary"] = {
        "@id": "https://publicschema.org/meta/vocabulary",
        "@type": "@id",
    }
    # SKOS match predicates and rdfs:seeAlso need explicit @id expansions
    # and @type:@id coercion so JSON-LD processors treat values as URI
    # references. CURIE keys alone are not valid context terms; the full
    # IRI must be provided via @id.
    skos_base = "http://www.w3.org/2004/02/skos/core#"
    for skos_pred in MATCH_PREDICATES.values():
        local = skos_pred.split(":", 1)[1]
        context_map[skos_pred] = {"@id": f"{skos_base}{local}", "@type": "@id"}
    context_map["rdfs:seeAlso"] = {
        "@id": "http://www.w3.org/2000/01/rdf-schema#seeAlso",
        "@type": "@id",
    }
    for concept_id, concept_out in out_concepts.items():
        context_map[concept_id] = concept_out["uri"]
    for prop_id, prop_out in out_properties.items():
        prop_uri = prop_out["uri"]
        prop_type = properties_raw[prop_id].get("type", "string")
        cardinality = properties_raw[prop_id].get("cardinality", "single")
        # concept:X references get @type: @id
        if prop_type.startswith("concept:"):
            entry: dict[str, str] = {"@id": prop_uri, "@type": "@id"}
        elif prop_type in JSONLD_TYPE_COERCION:
            entry = {"@id": prop_uri, "@type": JSONLD_TYPE_COERCION[prop_type]}
        elif cardinality == "multiple":
            # Multi-valued properties need an object entry for @container
            entry = {"@id": prop_uri}
        else:
            context_map[prop_id] = prop_uri
            entry = None
        if entry is not None:
            if cardinality == "multiple":
                entry["@container"] = "@set"
            context_map[prop_id] = entry
        # Add camelCase alias for schema.org equivalent properties
        schema_eq = properties_raw[prop_id].get("schema_org_equivalent")
        if schema_eq and schema_eq.startswith("schema:"):
            alias = schema_eq.split(":", 1)[1]
            # Alias points to the same context entry as the original property
            context_map[alias] = context_map[prop_id]
    # Add credential types to context with explicit URIs
    credentials_raw = _load_all_yaml(schema_dir / "credentials")
    for cred_id in credentials_raw:
        context_map[cred_id] = f"{base_uri}credentials/{cred_id}"
    version = meta.get("version", "0.1.0")
    maturity = meta.get("maturity", "draft")
    # Use "draft" as version label while unreleased; major.minor once stable
    version_label = "draft" if maturity == "draft" else ".".join(version.split(".")[:2])
    context = {
        "@context": context_map,
    }

    # Build JSON Schema per concept
    concept_schemas = {}
    for concept_id, data in concepts_raw.items():
        schema_props = {}
        for entry in _collect_all_properties(concept_id, concepts_raw):
            norm = _normalize_property_entry(entry)
            prop_id = norm["id"]
            if prop_id in properties_raw:
                schema_props[prop_id] = _property_to_json_schema(
                    properties_raw[prop_id], vocabularies_raw, out_vocabularies,
                )

        concept_domain = data.get("domain")
        schema_base = f"{base_uri}{concept_domain}/" if concept_domain else base_uri
        concept_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"{schema_base}schemas/{concept_id}.schema.json",
            "title": concept_id,
            "type": "object",
            "properties": schema_props,
        }
        concept_schemas[concept_id] = concept_schema

    # Build SD-JWT VC credential schemas
    # credentials_raw was already loaded above for context generation
    credential_schemas = {}
    for cred_id, cred_data in credentials_raw.items():
        subject_concept_id = cred_data.get("subject_concept")
        if not subject_concept_id or subject_concept_id not in concept_schemas:
            continue

        # Start with the subject concept's properties as credentialSubject
        subject_schema = dict(concept_schemas[subject_concept_id])
        subject_props = dict(subject_schema.get("properties", {}))

        # Add nested included concepts as sub-objects
        for included_id in cred_data.get("included_concepts", []):
            if included_id in concept_schemas:
                nested = dict(concept_schemas[included_id])
                nested_obj = {
                    "type": "object",
                    "properties": nested.get("properties", {}),
                }
                if "required" in nested:
                    nested_obj["required"] = nested["required"]
                # Use snake_case concept name as the property key
                subject_props[_to_snake_case(included_id)] = nested_obj

        # Build SD-JWT VC schema
        credential_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"{base_uri}schemas/credentials/{cred_id}.schema.json",
            "title": cred_id,
            "type": "object",
            "required": ["vct", "iss", "iat"],
            "properties": {
                "vct": {
                    "type": "string",
                    "const": f"{base_uri}schemas/credentials/{cred_id}",
                    "description": "Verifiable credential type identifier",
                },
                "iss": {
                    "type": "string",
                    "description": "Issuer identifier (DID or URL)",
                },
                "sub": {
                    "type": "string",
                    "description": "Subject identifier",
                },
                "iat": {
                    "type": "integer",
                    "description": "Issued at (Unix timestamp)",
                },
                "nbf": {
                    "type": "integer",
                    "description": "Not before (Unix timestamp)",
                },
                "exp": {
                    "type": "integer",
                    "description": "Expiration time (Unix timestamp)",
                },
                "cnf": {
                    "type": "object",
                    "description": "Confirmation claim for key binding",
                },
                "_sd_alg": {
                    "type": "string",
                    "description": "Selective disclosure hash algorithm",
                },
                "credentialSubject": {
                    "type": "object",
                    "properties": subject_props,
                },
            },
        }
        credential_schemas[cred_id] = credential_schema

    # Build JSON-LD documents for concepts, properties, and vocabularies.
    # These are written to dist/jsonld/ and served as static files.
    context_url = f"{base_uri}ctx/{version_label}.jsonld"
    jsonld_docs: dict[str, dict] = {}

    for concept_id, concept_out in out_concepts.items():
        domain = concept_out.get("domain")
        key = f"concepts/{domain}/{concept_id}.jsonld" if domain else f"concepts/{concept_id}.jsonld"
        jsonld_docs[key] = _concept_to_jsonld(
            concept_out, concepts_raw[concept_id], context_url,
            out_concepts, out_properties, properties_raw,
            out_vocabularies,
        )

    for prop_id, prop_out in out_properties.items():
        prop_ns = _compute_property_domain_namespace(prop_id, concepts_raw, properties_raw)
        key = f"properties/{prop_ns}/{prop_id}.jsonld" if prop_ns else f"properties/{prop_id}.jsonld"
        jsonld_docs[key] = _property_to_jsonld(
            prop_out, properties_raw[prop_id], context_url,
            out_concepts, out_vocabularies,
        )

    for vocab_key, vocab_out in out_vocabularies.items():
        # vocab_key is '<domain>/<id>' for domain-scoped vocabs, bare '<id>'
        # otherwise. The path mirrors the site's /vocab/... URL structure.
        key = f"vocab/{vocab_key}.jsonld"
        jsonld_docs[key] = _vocabulary_to_jsonld(
            vocab_out, vocabularies_raw[vocab_key], context_url,
        )

    # Build categories output for vocabulary.json
    out_categories = {}
    for cat_id, cat_data in categories_raw.items():
        out_categories[cat_id] = {"label": cat_data.get("label", {})}

    return {
        "meta": meta,
        "concepts": out_concepts,
        "properties": out_properties,
        "vocabularies": out_vocabularies,
        "bibliography": out_bibliography,
        "categories": out_categories,
        "context": context,
        "concept_schemas": concept_schemas,
        "credential_schemas": credential_schemas,
        "jsonld_docs": jsonld_docs,
    }


def write_outputs(result: dict, dist_dir: Path):
    """Write build outputs to the dist directory."""
    from build.export import generate_all_downloads
    from build.rdf_export import write_full_jsonld, write_shacl, write_turtle

    dist_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir = dist_dir / "schemas"
    schemas_dir.mkdir(exist_ok=True)

    # vocabulary.json (everything except context and concept_schemas)
    vocabulary = {
        "meta": result["meta"],
        "concepts": result["concepts"],
        "properties": result["properties"],
        "vocabularies": result["vocabularies"],
        "bibliography": result.get("bibliography", {}),
        "categories": result.get("categories", {}),
    }
    (dist_dir / "vocabulary.json").write_text(
        json.dumps(vocabulary, indent=2, ensure_ascii=False) + "\n"
    )

    # context.jsonld
    (dist_dir / "context.jsonld").write_text(
        json.dumps(result["context"], indent=2, ensure_ascii=False) + "\n"
    )

    # Per-concept JSON Schemas
    for concept_id, schema in result["concept_schemas"].items():
        filename = f"{concept_id}.schema.json"
        (schemas_dir / filename).write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
        )

    # Credential schemas (SD-JWT VC)
    cred_schemas = result.get("credential_schemas", {})
    if cred_schemas:
        creds_dir = schemas_dir / "credentials"
        creds_dir.mkdir(exist_ok=True)
        for cred_id, schema in cred_schemas.items():
            filename = f"{cred_id}.schema.json"
            (creds_dir / filename).write_text(
                json.dumps(schema, indent=2, ensure_ascii=False) + "\n"
            )

    # Per-concept/property/vocabulary JSON-LD documents
    jsonld_docs = result.get("jsonld_docs", {})
    if jsonld_docs:
        jsonld_dir = dist_dir / "jsonld"
        jsonld_dir.mkdir(exist_ok=True)
        for rel_path, doc in jsonld_docs.items():
            out_path = jsonld_dir / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
            )

    # RDF exports (Turtle, JSON-LD, SHACL)
    write_turtle(result, dist_dir)
    write_full_jsonld(result, dist_dir)
    write_shacl(result, dist_dir)

    # CSV and Excel downloads per concept
    downloads_dir = dist_dir / "downloads"
    generate_all_downloads(result, downloads_dir)

    # Machine-readable artifact index
    meta = result["meta"]
    base_uri = meta.get("base_uri", "https://publicschema.org/")
    version = meta.get("version", "0.1.0")
    maturity = meta.get("maturity", "draft")
    version_label = "draft" if maturity == "draft" else ".".join(version.split(".")[:2])

    manifest = {
        "name": meta.get("name", "PublicSchema"),
        "version": version,
        "maturity": maturity,
        "base_uri": base_uri,
        "artifacts": {
            "context": f"/ctx/{version_label}.jsonld",
            "vocabulary": "/vocabulary.json",
            "turtle": f"/v/{version_label}/publicschema.ttl",
            "jsonld": f"/v/{version_label}/publicschema.jsonld",
            "shacl": f"/v/{version_label}/publicschema.shacl.ttl",
        },
        "concepts": {},
        "vocabularies": {},
        "credentials": {},
    }

    for concept_id, concept in result["concepts"].items():
        path = concept["path"]
        domain = concept.get("domain")
        dl_prefix = f"/downloads/{domain}" if domain else "/downloads"
        manifest["concepts"][concept_id] = {
            "schema": f"/schemas/{concept_id}.schema.json",
            "jsonld": f"{path}.jsonld",
            "csv": f"{dl_prefix}/{concept_id}.csv",
            "xlsx_definition": f"{dl_prefix}/{concept_id}-definition.xlsx",
            "xlsx_template": f"{dl_prefix}/{concept_id}-template.xlsx",
        }

    for vocab_id, vocab in result["vocabularies"].items():
        manifest["vocabularies"][vocab_id] = {
            "jsonld": f"/vocab/{vocab_id}.jsonld",
        }

    for cred_id in result.get("credential_schemas", {}):
        manifest["credentials"][cred_id] = {
            "schema": f"/schemas/credentials/{cred_id}.schema.json",
        }

    (dist_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )


def main():
    """CLI entry point for build."""
    schema_dir = Path("schema")
    dist_dir = Path("dist")

    if len(sys.argv) > 1:
        schema_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        dist_dir = Path(sys.argv[2])

    result = build_vocabulary(schema_dir)
    write_outputs(result, dist_dir)
    print(f"Built {len(result['concepts'])} concepts, "
          f"{len(result['properties'])} properties, "
          f"{len(result['vocabularies'])} vocabularies, "
          f"{len(result.get('bibliography', {}))} bibliography entries.")


if __name__ == "__main__":
    main()
