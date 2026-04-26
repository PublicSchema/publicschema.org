"""
Compare PublicSchema concepts/properties with SEMIC EU Core Vocabularies.

Parses SEMIC Turtle (OWL + SHACL) files and PublicSchema YAML files,
then produces a structured gap analysis report in Markdown.

Usage:
    uv run python build/compare_semic.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parent.parent
SEMIC_DIR = ROOT / "external" / "semic"
SCHEMA_DIR = ROOT / "schema"
REPORT_PATH = ROOT / "reports" / "semic-comparison.md"

# RDF namespaces
M8G = Namespace("http://data.europa.eu/m8g/")
SHACL = Namespace("http://www.w3.org/ns/shacl#")
PERSON = Namespace("http://www.w3.org/ns/person#")
LOCN = Namespace("http://www.w3.org/ns/locn#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
ADMS = Namespace("http://www.w3.org/ns/adms#")
LEGAL = Namespace("http://www.w3.org/ns/legal#")
ORG = Namespace("http://www.w3.org/ns/org#")
DC = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

# Latest SEMIC release files (SHACL gives us the full property-per-class picture)
SEMIC_SOURCES = {
    "Core Person": {
        "shacl": SEMIC_DIR / "Core-Person-Vocabulary/releases/2.1.1/shacl/core-person-ap-SHACL.ttl",
        "voc": SEMIC_DIR / "Core-Person-Vocabulary/releases/2.1.1/voc/core-person-ap.ttl",
        "version": "2.1.1",
    },
    "Core Location": {
        "shacl": SEMIC_DIR / "Core-Location-Vocabulary/releases/2.1.0/shacl/core-location-ap-SHACL.ttl",
        "voc": SEMIC_DIR / "Core-Location-Vocabulary/releases/2.1.0/voc/core-location.ttl",
        "version": "2.1.0",
    },
    "Core Business": {
        "shacl": SEMIC_DIR / "Core-Business-Vocabulary/releases/2.2.0/shacl/core-business-ap-SHACL.ttl",
        "voc": SEMIC_DIR / "Core-Business-Vocabulary/releases/2.2.0/voc/core-business-ap.ttl",
        "version": "2.2.0",
    },
    "CPOV": {
        "shacl": SEMIC_DIR / "CPOV/releases/2.1.1/shacl/core-public-organisation-ap-SHACL.ttl",
        "voc": SEMIC_DIR / "CPOV/releases/2.1.1/voc/core-public-organisation-ap.ttl",
        "version": "2.1.1",
    },
    "CCCEV": {
        "shacl": SEMIC_DIR / "CCCEV/releases/2.1.0/shacl/cccev-ap-SHACL.ttl",
        "voc": SEMIC_DIR / "CCCEV/releases/2.1.0/voc/cccev.ttl",
        "version": "2.1.0",
    },
    "Core Public Event": {
        "shacl": SEMIC_DIR / "Core-Public-Event-Vocabulary/releases/1.1.0/shacl/core-public-event-ap-SHACL.ttl",
        "voc": SEMIC_DIR / "Core-Public-Event-Vocabulary/releases/1.1.0/voc/core-public-event.ttl",
        "version": "1.1.0",
    },
}


@dataclass
class SemicClass:
    uri: str
    label: str
    comment: str
    vocabulary: str  # which SEMIC vocabulary it comes from
    properties: list[SemicProperty] = field(default_factory=list)
    subclass_of: str | None = None


@dataclass
class SemicProperty:
    uri: str
    label: str
    comment: str
    domain_uri: str  # class this property belongs to
    range_uri: str | None = None


@dataclass
class PSConcept:
    id: str
    definition_en: str
    properties: list[str]
    supertypes: list[str]
    subtypes: list[str]


@dataclass
class PSProperty:
    id: str
    definition_en: str
    type: str
    cardinality: str
    vocabulary: str | None
    schema_org_equivalent: str | None


def uri_local_name(uri: str) -> str:
    """Extract the local name from a URI (after last / or #)."""
    for sep in ("#", "/"):
        if sep in uri:
            return uri.rsplit(sep, 1)[-1]
    return uri


def normalize_label(label: str) -> str:
    """Normalize a label for fuzzy matching: lowercase, strip spaces/underscores."""
    return re.sub(r"[\s_\-]+", "", label.lower())


# ---------------------------------------------------------------------------
# Parse SEMIC
# ---------------------------------------------------------------------------

def parse_semic() -> dict[str, SemicClass]:
    """Parse all SEMIC vocabularies and return a dict of URI -> SemicClass."""
    classes: dict[str, SemicClass] = {}

    for vocab_name, sources in SEMIC_SOURCES.items():
        # Parse OWL vocabulary for class/property definitions
        voc_graph = Graph()
        voc_path = sources["voc"]
        if voc_path.exists():
            voc_graph.parse(str(voc_path), format="turtle")

        # Collect classes from OWL
        for s in voc_graph.subjects(RDF.type, OWL.Class):
            uri = str(s)
            label = str(voc_graph.value(s, RDFS.label, default=""))
            comment = str(voc_graph.value(s, RDFS.comment, default=""))
            subclass = voc_graph.value(s, RDFS.subClassOf)
            classes[uri] = SemicClass(
                uri=uri,
                label=label,
                comment=comment,
                vocabulary=vocab_name,
                subclass_of=str(subclass) if subclass else None,
            )

        # Collect properties from OWL and attach to classes
        for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty):
            for s in voc_graph.subjects(RDF.type, prop_type):
                uri = str(s)
                label = str(voc_graph.value(s, RDFS.label, default=""))
                comment = str(voc_graph.value(s, RDFS.comment, default=""))
                domain = voc_graph.value(s, RDFS.domain)
                range_val = voc_graph.value(s, RDFS.range)
                prop = SemicProperty(
                    uri=uri,
                    label=label,
                    comment=comment,
                    domain_uri=str(domain) if domain else "",
                    range_uri=str(range_val) if range_val else None,
                )
                domain_str = str(domain) if domain else ""
                if domain_str in classes:
                    classes[domain_str].properties.append(prop)
                elif domain_str:
                    # Class defined in external ontology (FOAF, locn, etc.)
                    # Create a stub entry
                    classes[domain_str] = SemicClass(
                        uri=domain_str,
                        label=uri_local_name(domain_str),
                        comment="",
                        vocabulary=vocab_name,
                    )
                    classes[domain_str].properties.append(prop)

        # Parse SHACL for additional properties per class shape
        shacl_graph = Graph()
        shacl_path = sources["shacl"]
        if shacl_path.exists():
            shacl_graph.parse(str(shacl_path), format="turtle")

        for shape in shacl_graph.subjects(RDF.type, SHACL.NodeShape):
            target_class = shacl_graph.value(shape, SHACL.targetClass)
            if not target_class:
                continue
            target_uri = str(target_class)

            # Ensure class entry exists
            if target_uri not in classes:
                classes[target_uri] = SemicClass(
                    uri=target_uri,
                    label=uri_local_name(target_uri),
                    comment="",
                    vocabulary=vocab_name,
                )

            # Collect properties from SHACL shape
            existing_uris = {p.uri for p in classes[target_uri].properties}
            for prop_node in shacl_graph.objects(shape, SHACL.property):
                path = shacl_graph.value(prop_node, SHACL.path)
                if not path:
                    continue
                path_uri = str(path)
                if path_uri in existing_uris:
                    continue
                label = str(shacl_graph.value(prop_node, SHACL.name, default=""))
                comment = str(shacl_graph.value(prop_node, SHACL.description, default=""))
                range_class = shacl_graph.value(prop_node, SHACL["class"])
                range_dt = shacl_graph.value(prop_node, SHACL.datatype)
                range_uri = str(range_class or range_dt) if (range_class or range_dt) else None

                prop = SemicProperty(
                    uri=path_uri,
                    label=label,
                    comment=comment,
                    domain_uri=target_uri,
                    range_uri=range_uri,
                )
                classes[target_uri].properties.append(prop)
                existing_uris.add(path_uri)

    return classes


# ---------------------------------------------------------------------------
# Parse PublicSchema
# ---------------------------------------------------------------------------

def parse_ps_concepts() -> dict[str, PSConcept]:
    """Parse PublicSchema concept YAML files."""
    concepts = {}
    concept_dir = SCHEMA_DIR / "concepts"
    for path in sorted(concept_dir.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data or "id" not in data:
            continue
        defn = data.get("definition", {})
        concepts[data["id"]] = PSConcept(
            id=data["id"],
            definition_en=defn.get("en", "").strip() if defn else "",
            properties=data.get("properties", []) or [],
            supertypes=data.get("supertypes", []) or [],
            subtypes=data.get("subtypes", []) or [],
        )
    return concepts


def parse_ps_properties() -> dict[str, PSProperty]:
    """Parse PublicSchema property YAML files."""
    props = {}
    prop_dir = SCHEMA_DIR / "properties"
    for path in sorted(prop_dir.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        if not data or "id" not in data:
            continue
        defn = data.get("definition", {})
        props[data["id"]] = PSProperty(
            id=data["id"],
            definition_en=defn.get("en", "").strip() if defn else "",
            type=data.get("type", ""),
            cardinality=data.get("cardinality", ""),
            vocabulary=data.get("vocabulary"),
            schema_org_equivalent=data.get("schema_org_equivalent"),
        )
    return props


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

# Known concept-level mappings (PublicSchema ID -> SEMIC class URI)
# These are manually curated where name-based matching would miss or mismatch.
CONCEPT_HINTS: dict[str, tuple[str, str]] = {
    # (SEMIC URI, match quality)
    # Reviewed 2024-04-11 by semantic expert subagents.
    "Person": ("http://www.w3.org/ns/person#Person", "exact"),
    "Address": ("http://www.w3.org/ns/locn#Address", "exact"),
    "Identifier": ("http://www.w3.org/ns/adms#Identifier", "exact"),
    "Location": ("http://purl.org/dc/terms/Location", "close"),  # ours is hierarchical admin node; dc:Location is generic spatial
    "Party": ("http://xmlns.com/foaf/0.1/Agent", "close"),
    "ScoringRule": ("http://data.europa.eu/m8g/ReferenceFramework", "close"),  # policy/rules from which requirements derive
    # REJECTED after review:
    # Event -> m8g:PublicEvent: PublicEvent is conference/ceremony with audience; our Event is a delivery transaction record
    # EligibilityDecision -> m8g:Criterion: a decision (verdict) is not a criterion (rule)
}

# Known property-level mappings (PS property ID -> SEMIC property URI, match quality)
# Only include mappings where the semantics genuinely align, not just the name.
PROPERTY_HINTS: dict[str, tuple[str, str]] = {
    # Person naming
    "given_name": ("http://xmlns.com/foaf/0.1/givenName", "exact"),
    "family_name": ("http://xmlns.com/foaf/0.1/familyName", "exact"),
    "preferred_name": ("http://purl.org/dc/terms/alternative", "close"),
    "patronymic_name": ("http://www.w3.org/ns/person#patronymicName", "exact"),
    "family_name_at_birth": ("http://www.w3.org/ns/person#birthName", "broad"),  # ours is family name only; SEMIC's is full name at birth
    "name": ("http://xmlns.com/foaf/0.1/name", "exact"),  # both mean "full display name as one string"
    # Person demographics
    "date_of_birth": ("http://data.europa.eu/m8g/birthDate", "exact"),
    "gender": ("http://data.europa.eu/m8g/gender", "exact"),
    "sex": ("http://data.europa.eu/m8g/sex", "exact"),
    "nationality": ("http://www.w3.org/ns/person#citizenship", "close"),
    "phone_number": ("http://data.europa.eu/m8g/telephone", "close"),  # SEMIC puts this on ContactPoint, not Person
    # Address
    "street_address": ("http://www.w3.org/ns/locn#thoroughfare", "close"),
    "city": ("http://www.w3.org/ns/locn#postName", "close"),
    "postal_code": ("http://www.w3.org/ns/locn#postCode", "exact"),
    "country": ("http://www.w3.org/ns/locn#adminUnitL1", "close"),
    "administrative_area": ("http://www.w3.org/ns/locn#adminUnitL2", "close"),
    "building_name": ("http://www.w3.org/ns/locn#locatorName", "close"),
    "house_number": ("http://www.w3.org/ns/locn#locatorDesignator", "close"),
    # Location / geometry
    "latitude": ("http://data.europa.eu/m8g/latitude", "exact"),
    "longitude": ("http://data.europa.eu/m8g/longitude", "exact"),
    "location_name": ("http://www.w3.org/ns/locn#geographicName", "close"),
    # Identifier
    "identifier_value": ("http://www.w3.org/2004/02/skos/core#notation", "close"),
    "issue_date": ("http://purl.org/dc/terms/issued", "exact"),  # identical within Identifier context
    "issuing_authority": ("http://purl.org/dc/terms/creator", "close"),
    "identifier_scheme_id": ("http://purl.org/dc/terms/conformsTo", "close"),
    "identifier_scheme_name": ("http://www.w3.org/2000/01/rdf-schema#label", "close"),
}

# Properties that match by name but NOT semantically. Suppress fuzzy matching.
# Each entry explains why the match is wrong.
PROPERTY_EXCLUSIONS: set[str] = {
    # PS `description` is a generic concept description; dc:description is used on SEMIC PublicOrganisation
    "description",
    # PS `role` is group membership role (head, spouse, child); m8g:role is event participation role
    "role",
    # PS `frequency` is benefit payment frequency; m8g:frequency is on TemporalEntity
    "frequency",
    # PS `location` on Address is a ref to a Location concept; locn:location goes the other direction
    "location",
    # PS `start_date`/`end_date` are generic date fields; time:hasTime is a temporal entity association
    "start_date",
    "end_date",
    # PS `address` is a ref to an Address concept; locn:address means "associates any Resource with Address"
    "address",
}


def find_concept_match(
    ps_id: str,
    semic_classes: dict[str, SemicClass],
) -> tuple[SemicClass | None, str]:
    """Find the best SEMIC class match for a PublicSchema concept."""
    # Check manual hints first
    if ps_id in CONCEPT_HINTS:
        uri, quality = CONCEPT_HINTS[ps_id]
        if uri in semic_classes:
            return semic_classes[uri], quality

    # Fuzzy match on normalized label
    ps_norm = normalize_label(ps_id)
    for uri, cls in semic_classes.items():
        if normalize_label(cls.label) == ps_norm:
            return cls, "name_match"
        if normalize_label(uri_local_name(uri)) == ps_norm:
            return cls, "name_match"

    return None, "none"


def find_property_match(
    ps_prop_id: str,
    semic_classes: dict[str, SemicClass],
) -> tuple[SemicProperty | None, str, str]:
    """Find best SEMIC property match. Returns (property, quality, semic_class_label)."""
    # Check manual hints
    if ps_prop_id in PROPERTY_HINTS:
        uri, quality = PROPERTY_HINTS[ps_prop_id]
        for cls in semic_classes.values():
            for prop in cls.properties:
                if prop.uri == uri:
                    return prop, quality, cls.label
        # URI in hint but not found in parsed data: create a synthetic entry
        # (property exists in the SEMIC spec but not in the latest SHACL/OWL)
        synth = SemicProperty(
            uri=uri,
            label=uri_local_name(uri),
            comment="(from locn/external namespace, not in latest SHACL)",
            domain_uri="",
        )
        return synth, quality, "locn/external"

    # Skip fuzzy matching for properties known to be false positives
    if ps_prop_id in PROPERTY_EXCLUSIONS:
        return None, "none", ""

    # Fuzzy match on property label
    ps_norm = normalize_label(ps_prop_id)
    for cls in semic_classes.values():
        for prop in cls.properties:
            prop_norm = normalize_label(prop.label)
            prop_uri_norm = normalize_label(uri_local_name(prop.uri))
            if prop_norm == ps_norm or prop_uri_norm == ps_norm:
                return prop, "name_match", cls.label

    return None, "none", ""


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    semic_classes: dict[str, SemicClass],
    ps_concepts: dict[str, PSConcept],
    ps_properties: dict[str, PSProperty],
) -> str:
    lines = []
    lines.append("# SEMIC Core Vocabularies Comparison Report")
    lines.append("")
    lines.append("Auto-generated by `build/compare_semic.py`.")
    lines.append("")

    # Summary stats
    total_semic_classes = len([c for c in semic_classes.values() if c.comment])
    all_semic_props = set()
    for cls in semic_classes.values():
        for p in cls.properties:
            all_semic_props.add(p.uri)
    total_semic_props = len(all_semic_props)

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **SEMIC classes parsed:** {total_semic_classes}")
    lines.append(f"- **SEMIC properties parsed:** {total_semic_props}")
    lines.append(f"- **PublicSchema concepts:** {len(ps_concepts)}")
    lines.append(f"- **PublicSchema properties:** {len(ps_properties)}")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 1: Concept-level alignment
    # -----------------------------------------------------------------------
    lines.append("## Concept-level alignment")
    lines.append("")
    lines.append("| PublicSchema | SEMIC class | Match | SEMIC vocabulary |")
    lines.append("|---|---|---|---|")

    matched_concepts = []
    unmatched_ps_concepts = []
    for ps_id in sorted(ps_concepts.keys()):
        cls, quality = find_concept_match(ps_id, semic_classes)
        if cls and quality != "none":
            matched_concepts.append((ps_id, cls, quality))
            lines.append(f"| {ps_id} | `{cls.label}` | {quality} | {cls.vocabulary} |")
        else:
            unmatched_ps_concepts.append(ps_id)
            lines.append(f"| {ps_id} | - | - | - |")

    lines.append("")
    lines.append(f"**Matched:** {len(matched_concepts)} / {len(ps_concepts)} PublicSchema concepts")
    lines.append("")

    # Concepts unique to PublicSchema
    if unmatched_ps_concepts:
        lines.append("### PublicSchema concepts with no SEMIC equivalent")
        lines.append("")
        lines.append("These represent PublicSchema's unique contribution (delivery lifecycle):")
        lines.append("")
        for cid in unmatched_ps_concepts:
            c = ps_concepts[cid]
            defn_short = c.definition_en[:120] + "..." if len(c.definition_en) > 120 else c.definition_en
            lines.append(f"- **{cid}**: {defn_short}")
        lines.append("")

    # Classes in SEMIC with no PublicSchema equivalent
    matched_semic_uris = {cls.uri for _, cls, _ in matched_concepts}
    # Only consider "primary" classes (with comments, not stubs)
    unmatched_semic = [
        cls for uri, cls in semic_classes.items()
        if cls.comment and uri not in matched_semic_uris
    ]
    if unmatched_semic:
        lines.append("### SEMIC classes with no PublicSchema equivalent")
        lines.append("")
        lines.append("| Class | Vocabulary | Description |")
        lines.append("|---|---|---|")
        for cls in sorted(unmatched_semic, key=lambda c: c.vocabulary):
            desc = cls.comment[:100] + "..." if len(cls.comment) > 100 else cls.comment
            lines.append(f"| `{cls.label}` | {cls.vocabulary} | {desc} |")
        lines.append("")

    # -----------------------------------------------------------------------
    # Section 2: Property-level alignment (for matched concepts)
    # -----------------------------------------------------------------------
    lines.append("## Property-level alignment")
    lines.append("")

    total_prop_matched = 0
    total_prop_unmatched = 0
    total_semic_only = 0

    for ps_id, semic_cls, _concept_quality in matched_concepts:
        ps_concept = ps_concepts[ps_id]
        lines.append(f"### {ps_id} vs `{semic_cls.label}`")
        lines.append("")

        # Map PS properties
        lines.append("| PublicSchema property | SEMIC property | Match | SEMIC URI |")
        lines.append("|---|---|---|---|")

        ps_matched_uris = set()
        for prop_id in ps_concept.properties:
            sprop, quality, _ = find_property_match(prop_id, semic_classes)
            if sprop and quality != "none" and quality != "hint_not_found":
                total_prop_matched += 1
                ps_matched_uris.add(sprop.uri)
                local = uri_local_name(sprop.uri)
                lines.append(f"| `{prop_id}` | `{local}` | {quality} | `{sprop.uri}` |")
            else:
                total_prop_unmatched += 1
                lines.append(f"| `{prop_id}` | - | - | - |")

        # List SEMIC properties that PS doesn't have
        semic_only = [
            p for p in semic_cls.properties
            if p.uri not in ps_matched_uris
        ]
        if semic_only:
            total_semic_only += len(semic_only)
            lines.append("")
            lines.append(f"**SEMIC properties not in PublicSchema `{ps_id}`:**")
            lines.append("")
            for p in semic_only:
                local = uri_local_name(p.uri)
                desc = p.comment[:80] + "..." if len(p.comment) > 80 else p.comment
                lines.append(f"- `{local}` ({p.uri}): {desc}")

        lines.append("")

    # -----------------------------------------------------------------------
    # Section 3: Property summary
    # -----------------------------------------------------------------------
    lines.append("## Property alignment summary")
    lines.append("")
    lines.append(f"- **PS properties matched to SEMIC:** {total_prop_matched}")
    lines.append(f"- **PS properties with no SEMIC equivalent:** {total_prop_unmatched}")
    lines.append(f"- **SEMIC properties not in PublicSchema (on matched concepts):** {total_semic_only}")
    lines.append("")

    # -----------------------------------------------------------------------
    # Section 4: All PS properties with matches
    # -----------------------------------------------------------------------
    lines.append("## Full property mapping table")
    lines.append("")
    lines.append("All PublicSchema properties checked against all SEMIC properties:")
    lines.append("")
    lines.append("| PublicSchema | SEMIC property | Match | SEMIC class | SEMIC URI |")
    lines.append("|---|---|---|---|---|")

    matched_total = 0
    for prop_id in sorted(ps_properties.keys()):
        sprop, quality, cls_label = find_property_match(prop_id, semic_classes)
        if sprop and quality != "none" and quality != "hint_not_found":
            matched_total += 1
            local = uri_local_name(sprop.uri)
            lines.append(f"| `{prop_id}` | `{local}` | {quality} | {cls_label} | `{sprop.uri}` |")
        else:
            lines.append(f"| `{prop_id}` | - | - | - | - |")

    lines.append("")
    lines.append(f"**Overall:** {matched_total} / {len(ps_properties)} PublicSchema properties have a SEMIC match")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Parsing SEMIC Core Vocabularies...")
    semic_classes = parse_semic()
    print(f"  Found {len(semic_classes)} classes")
    prop_count = sum(len(c.properties) for c in semic_classes.values())
    print(f"  Found {prop_count} property assignments")

    print("Parsing PublicSchema...")
    ps_concepts = parse_ps_concepts()
    ps_properties = parse_ps_properties()
    print(f"  Found {len(ps_concepts)} concepts, {len(ps_properties)} properties")

    print("Generating comparison report...")
    report = generate_report(semic_classes, ps_concepts, ps_properties)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report)
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
