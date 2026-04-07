# Related Standards

PublicSchema sits in a landscape of adjacent initiatives that operate at different layers. It is designed to complement, not compete with, each of them.

## Where PublicSchema sits

| Layer | What exists | What's missing |
|---|---|---|
| Trust and transport | EBSI, OpenID4VC, W3C VC Data Model | No domain vocabulary inside credentials |
| Identity attributes | EU Core Person Vocabulary, W3C Citizenship Vocabulary | Covers name/birth/citizenship only, not delivery data |
| Service catalogues | CPSV-AP (EU), HSDS/Open Referral, schema.org/GovernmentService | Describes what services exist, not who receives what |
| API interoperability | DCI/SPDCI, GovStack | Interface contracts between systems, not semantic vocabulary |
| Statistical measurement | ILO/World Bank ASPIRE, ILOSTAT | Counts and indicators, not data models for exchange |
| **Delivery lifecycle vocabulary** | **Nothing** | **This is the gap PublicSchema fills** |

## Specific initiatives

### DCI/SPDCI

The Digital Convergence Initiative builds API interoperability standards between social protection systems (social registry, payment, civil registration interfaces), jointly steered by GIZ, ILO, and the World Bank. PublicSchema is the semantic vocabulary layer that DCI's API standards implicitly need but have not built. DCI defines how data flows between systems; PublicSchema defines what the data means. The two are complementary.

### EU Core Vocabularies (SEMIC / Interoperable Europe)

The closest technical precedent for how to build a shared vocabulary. The Core Person Vocabulary, Core Location Vocabulary, and Core Public Service Vocabulary Application Profile (CPSV-AP) are minimal, reusable RDF vocabularies for EU public administration, published with SHACL validation shapes under CC-BY 4.0. PublicSchema aligns with these where they overlap (person, location, address) rather than reinventing definitions. However, the EU Core Vocabularies cover identity and service cataloguing, not the delivery lifecycle (enrollment, entitlement, payment, grievance).

### GovStack

GovStack defines building block specifications for digital government services (identity, payments, messaging). PublicSchema is the data model counterpart: where GovStack says "you need a payment building block," PublicSchema defines what payment data looks like across systems and how to translate between them. GovStack explicitly lacks a cross-cutting semantic layer, which is the gap PublicSchema addresses.

### FHIR

The health sector's interoperability standard, combining a data model with an API spec. PublicSchema takes inspiration from FHIR's approach (resources, extensions, value sets, maturity levels) but targets the government services space. FHIR's vocabulary governance model is a useful reference.

### Schema.org

The direct model for how PublicSchema is structured and published. Schema.org succeeded because it was simple, optional, and useful from day one. Its government types (GovernmentService, GovernmentOrganization) are extremely thin and SEO-oriented; they do not model delivery data.

### HSDS / Open Referral

The standard for service directories ("what services exist where"). PublicSchema is for delivery data ("who receives what, when, how"). A service described in HSDS could be the same service described by a PublicSchema Program, but the two address opposite ends of the lifecycle.

### W3C Verifiable Credentials

The VC Data Model 2.0 provides the trust layer. PublicSchema's vocabulary, published as a JSON-LD context with resolvable URIs, serves as the schema that makes government service credentials interoperable across borders and systems. Related specs include SD-JWT VC for selective disclosure and OpenID4VCI/VP for credential issuance and presentation.

### EBSI

The European Blockchain Services Infrastructure operates at the trust and transport layer, not the domain vocabulary layer. However, its credential schemas for person identity (eIDAS PID), social security coordination (Portable Document A1), health insurance (EHIC), and education (Europass EDC / ELM 3.2) model many of the same entities PublicSchema covers. PublicSchema used EBSI schemas as a design input to identify missing properties on Person, Address, Identifier, Enrollment, and Entitlement.

### Trust registries

A companion concern. The vocabulary defines what terms mean, but verifiers also need to know which issuers are authoritative for which claims. This is out of scope for the vocabulary itself, but any deployment will need a trust registry alongside it. OpenID Federation and the EBSI trust model are reference points.
