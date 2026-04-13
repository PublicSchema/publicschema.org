# Vocabulary Adoption Guide

This is the lightest way to use PublicSchema. You align your system's codes and field values to PublicSchema's canonical vocabulary, without changing your data model, adopting JSON-LD, or issuing credentials. The payoff: your data becomes comparable with any other system that does the same.

## Contents

- [When to use this approach](#when-to-use-this-approach)
- [Step 1: Identify the vocabularies you need](#step-1-identify-the-vocabularies-you-need)
- [Step 2: Download the vocabulary](#step-2-download-the-vocabulary)
- [Step 3: Build a mapping table](#step-3-build-a-mapping-table)
- [Step 4: Apply the mapping](#step-4-apply-the-mapping)
- [What you get](#what-you-get)
- [Tips](#tips)
- [Available downloads](#available-downloads)
- [Next steps](#next-steps)

## When to use this approach

This approach works well when:

- You need comparable reporting across programs, countries, or donors
- You want to standardize API response codes across agencies
- You are harmonizing data exports from multiple systems
- You want a quick win before committing to deeper integration

You do not need to change your database schema, your internal field names, or your application code. You only need a translation layer between your codes and the canonical codes.

## Step 1: Identify the vocabularies you need

Browse the [vocabularies page](/vocab/) to see all available controlled value sets. Common starting points:

| If your system stores... | Look at vocabulary... |
|---|---|
| Enrollment status (active, suspended, etc.) | [enrollment-status](/vocab/enrollment-status/) |
| Payment status (completed, failed, etc.) | [payment-status](/vocab/payment-status/) |
| Gender | [gender-type](/vocab/gender-type/) |
| Delivery channel (bank, mobile, cash) | [delivery-channel](/vocab/delivery-channel/) |
| Identifier number type (national ID number, passport number, P-code, etc.) | [identifier-type](/vocab/identifier-type/) |
| Identity document type (passport, national ID card, beneficiary card, etc.) | [document-type](/vocab/document-type/) |
| Country | [country](/vocab/country/) |
| Currency | [currency](/vocab/currency/) |

Each vocabulary page shows the canonical codes, their definitions in English, French, and Spanish, and which international standard they reference (ISO, FHIR, etc.).

## Step 2: Download the vocabulary

Every vocabulary page has a **CSV** download button. The CSV includes:

| Column | What it contains |
|---|---|
| `code` | The canonical PublicSchema code |
| `label_en` | English label |
| `label_fr` | French label |
| `label_es` | Spanish label |
| `standard_code` | Code from the referenced international standard (if any) |
| `uri` | Stable URI for the value |
| `definition_en` | English definition |

You can also download the vocabulary as **JSON-LD** for machine-readable access.

## Step 3: Build a mapping table

Compare your system's codes to the canonical codes and build a mapping table. For example, if your system uses numeric codes for gender:

| Your system code | Your label | PublicSchema code |
|---|---|---|
| `1` | Male | `male` |
| `2` | Female | `female` |
| `3` | Other | `other` |
| `9` | Unknown | `not_stated` |

Some things to watch for:

- **One-to-many mappings.** Your system might have one code where PublicSchema has several. For example, your system might use "inactive" for both "suspended" and "completed" enrollments. Document these and decide how to handle them.
- **Unmapped values.** Your system might have values that have no canonical equivalent, or vice versa. Document the gaps; they are useful information even if you cannot resolve them immediately.
- **Semantic differences.** Two codes might look the same but mean different things. Read the definitions, not just the labels. For example, "pending" in your system might mean "awaiting approval" while the canonical "pending" means "awaiting payment."

## Step 4: Apply the mapping

How you apply the mapping depends on what you are trying to do:

**For reporting:** Add a column to your export that translates internal codes to canonical codes. Your reporting template references the canonical column.

**For API responses:** Add a translation layer that converts internal codes to canonical codes in the response. Your internal database stays unchanged.

**For data exchange:** When exporting data for another system, run the values through your mapping table. When importing, run the reverse mapping.

**For dashboards:** Map codes at the visualization layer. Your queries return internal codes; the dashboard translates them for display.

In all cases, your internal system continues to use its own codes. The mapping is applied at the boundary.

## What you get

Once your codes are aligned:

- **Comparable numbers across systems.** "How many active enrollments?" means the same thing everywhere.
- **Simpler data exchange.** Two systems that both map to PublicSchema codes can exchange data without bilateral code translation.
- **Explicit gaps.** Where your system's codes do not match the canonical set, the gap is visible and documented rather than hidden in ad-hoc translations.
- **A foundation for deeper integration.** If you later want to align field names, adopt JSON Schemas, or issue credentials, the vocabulary mapping is already done.

## Tips

- Start with one or two vocabularies, not all of them. Enrollment status and payment status are common starting points.
- If your system already uses codes from an international standard (e.g., ISO 3166 for countries), check whether PublicSchema references the same standard. If so, your mapping may already be trivial.
- PublicSchema vocabularies that reference international standards include the `standard_code` in the CSV. You can map through the standard code if that is easier than mapping through labels.
- Some vocabularies include system-specific mappings in their YAML source files. Check the [vocabulary page](/vocab/) to see if your system is already mapped.

## Available downloads

Every vocabulary page offers:

| Format | What it is | Best for |
|---|---|---|
| **CSV** | Flat file with codes, labels, definitions | Spreadsheets, data pipelines, quick reference |
| **JSON-LD** | Machine-readable linked data | Programmatic access, RDF toolchains |

For the complete vocabulary (all concepts, properties, and vocabularies in one file):

| Format | URL |
|---|---|
| Full vocabulary (JSON-LD) | [`/v/draft/publicschema.jsonld`](/v/draft/publicschema.jsonld) |
| Full vocabulary (Turtle) | [`/v/draft/publicschema.ttl`](/v/draft/publicschema.ttl) |

## Next steps

- To align field names (not just codes), see the [Interoperability & Mapping Guide](/docs/interoperability-guide/).
- To design a new system for compatibility, see the [Data Model Design Guide](/docs/data-model-guide/).
- To use JSON-LD contexts and issue verifiable credentials, see the [JSON-LD & VC Guide](/docs/jsonld-vc-guide/).
