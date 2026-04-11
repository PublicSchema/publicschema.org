# Design Principles

## 1. Semantic, not structural

Concepts carry meaning. A Person is not a bag of fields; it is a named entity with a definition written for domain practitioners. The interoperability problem is vocabulary divergence: systems use different names for the same real-world entities, and when those names encode different semantic choices, mappings between them lose information. PublicSchema provides shared definitions that make equivalences explicit and preserve meaning across systems.

## 2. Descriptive, not prescriptive

Nothing is mandatory. Systems adopt the concepts, properties, and vocabularies that apply to them. PublicSchema describes what delivery data looks like across systems; it does not mandate what any system must collect.

## 3. Evidence-based and incremental

Convergence data drives priorities. A property present in 6 out of 6 systems is worth standardizing before one present in 2 out of 6. Start with what is confirmed, extend when adoption surfaces genuine need.

## 4. Plain language for practitioners

Definitions are written for policy officers and program managers, not developers. "The lifecycle states of an enrollment in a program" is preferable to "an enumeration of status codes applicable to the beneficiary registration entity."

## See also

- [Schema Design](../schema-design/) -- naming, scoping, and modeling
- [Vocabulary Design](../vocabulary-design/) -- controlled value sets and system mappings
- [Versioning and Maturity](../versioning-and-maturity/) -- stability guarantees and evolution rules
- [Selective Disclosure](../selective-disclosure/) -- credential privacy design
