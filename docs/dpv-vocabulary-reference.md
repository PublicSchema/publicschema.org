# DPV Vocabulary Reference for Public Program Delivery

This document is a curated starter list of W3C Data Privacy Vocabulary (DPV) URIs for the three URI-valued properties on `ConsentRecord` and `PrivacyNotice`: `purposes`, `personal_data_categories`, and `processing_operations`.

It is a guide, not a schema artefact. The values listed here are DPV classes; adopters set them as URI strings on their records. PublicSchema does not validate that a given URI is a valid DPV class at runtime.

**Adopters should narrow this list to their actual program scope.** A payment-processing program does not need research or marketing purposes. A single-country registry does not need international-transfer operations. Start from the subset that applies and add only when operationally necessary.

Where your national taxonomy is richer than DPV provides, the DPV extension mechanism allows you to define subclasses. For example, if your country has a statutory category "social assistance identity verification" that DPV does not name directly, you can define `https://your.registry/purpose/SocialAssistanceIdentityVerification` as a subclass of `dpv:IdentityVerification` and use your URI on records.

---

## Purposes (subclasses of `dpv:Purpose`)

Use these as values for `ConsentRecord.purposes` and `PrivacyNotice.purposes`.

| URI | Description |
|---|---|
| `dpv:ServiceProvision` | Processing necessary to deliver a service to the data subject (the broadest service purpose; use a narrower subclass where possible). |
| `dpv:ServicePersonalisation` | Adapting a service based on the individual's characteristics or history. |
| `dpv:ServiceRegistration` | Registering an individual to access or receive a service. |
| `dpv:ServiceUsageAnalytics` | Analysing how services are used to improve delivery. |
| `dpv:IdentityVerification` | Verifying that a person is who they claim to be. |
| `dpv:FraudPreventionAndDetection` | Detecting, preventing, or investigating fraud. |
| `dpv:LegalCompliance` | Complying with a legal obligation. |
| `dpv:MaintainCreditCheckingDatabase` | Maintaining records that inform credit or financial eligibility decisions. |
| `dpv:CommunicationForCustomerCare` | Contacting individuals for case management or support. |
| `dpv:SocialSecurityBenefitAdministration` | Administering social security benefits (enrolment, payment, appeals). |
| `dpv:PublicBenefitAdministration` | Administering any public benefit or assistance program. |
| `dpv:EligibilityDetermination` | Determining whether an individual qualifies for a benefit or service. |
| `dpv:BenefitPaymentProcessing` | Processing the payment of a benefit to an eligible recipient. |
| `dpv:ProgramMonitoring` | Monitoring whether a program is reaching intended beneficiaries and achieving its goals. |
| `dpv:MandatedDataSharing` | Sharing data required by law with another authority. |
| `dpv:ResearchAndDevelopment` | Research, including policy research, impact evaluation, and programme design. |
| `dpv:Statistics` | Producing statistical output; data is used for aggregate analysis, not individual decisions. |
| `dpv:AcademicResearch` | Research conducted within an academic or research institution. |
| `dpv:HumanitarianAssistance` | Processing in the context of humanitarian response or emergency assistance. |
| `dpv:DisasterRecovery` | Processing to support recovery from a natural disaster or emergency. |
| `dpv:AuditAndAccountability` | Processing to support audit, accountability, or oversight functions. |

---

## Personal data categories (subclasses of `dpv-pd:PersonalData`)

Use these as values for `ConsentRecord.personal_data_categories` and `PrivacyNotice.data_categories`.

### Identifiers

| URI | Description |
|---|---|
| `dpv-pd:Name` | A name that identifies a natural person (given name, family name, or combined). |
| `dpv-pd:Identifier` | Any identifier assigned to a person (national ID number, case number, registry ID). |
| `dpv-pd:NationalIdentificationNumber` | A national identity number (e.g., NIN, SSN, CNPJ). |
| `dpv-pd:DateOfBirth` | Date of birth of the person. |
| `dpv-pd:Age` | Age of the person, whether exact or a range. |

### Demographics

| URI | Description |
|---|---|
| `dpv-pd:Gender` | Gender as self-reported by the individual. |
| `dpv-pd:Sex` | Biological sex of the individual. |
| `dpv-pd:HouseholdComposition` | The number and characteristics of people in a household. |
| `dpv-pd:MaritalStatus` | Marital or civil status. |
| `dpv-pd:Nationality` | Nationality or citizenship. |
| `dpv-pd:Ethnicity` | Ethnic or racial origin. This is a special category under GDPR Art 9. |
| `dpv-pd:Religion` | Religious belief. This is a special category under GDPR Art 9. |
| `dpv-pd:PoliticalOpinion` | Political views or affiliations. This is a special category under GDPR Art 9. |
| `dpv-pd:Disability` | Disability status or type. This is a special category under GDPR Art 9 (health data). |

### Contact

| URI | Description |
|---|---|
| `dpv-pd:PhoneNumber` | Telephone or mobile number. |
| `dpv-pd:EmailAddress` | Email address. |
| `dpv-pd:Address` | Postal or residential address. |
| `dpv-pd:Location` | Location data, including GPS coordinates and geographic area. |

### Financial

| URI | Description |
|---|---|
| `dpv-pd:Income` | Income, wages, or other earnings. |
| `dpv-pd:FinancialAccount` | Bank account number, mobile money account, or similar financial identifier. |
| `dpv-pd:FinancialStatus` | Overall financial situation, including poverty level or socio-economic status. |
| `dpv-pd:BankAccount` | Bank account details specifically. |
| `dpv-pd:AssetData` | Ownership of land, livestock, property, or other assets. |

### Biometric (all are special category under GDPR Art 9)

| URI | Description |
|---|---|
| `dpv-pd:Biometric` | Any biometric data (broadest; use a narrower subclass where possible). |
| `dpv-pd:Fingerprint` | Fingerprint or handprint data. |
| `dpv-pd:FacialImage` | Facial photograph or facial recognition template. |
| `dpv-pd:IrisScan` | Iris scan or iris recognition data. |
| `dpv-pd:VoiceSignature` | Voice recording used for identification. |

### Health (special category under GDPR Art 9)

| URI | Description |
|---|---|
| `dpv-pd:HealthData` | Any data relating to physical or mental health. Use with `special_category_basis`. |
| `dpv-pd:MedicalHistory` | History of diagnoses, treatments, or conditions. |
| `dpv-pd:Disability` | Disability status (see also under Demographics). |
| `dpv-pd:Nutrition` | Nutritional status, including anthropometric measurements. |

### Program-specific

| URI | Description |
|---|---|
| `dpv-pd:SocialBenefitData` | Data relating to social protection benefit receipt or eligibility. |
| `dpv-pd:SocialMediaData` | Data originating from social media profiles (less common in social protection). |

---

## Processing operations (subclasses of `dpv:Processing`)

Use these as values for `ConsentRecord.processing_operations` and `PrivacyNotice.processing_operations`.

| URI | Description |
|---|---|
| `dpv:Collect` | Gathering data from the data subject or a third party. |
| `dpv:Record` | Creating a persistent record of the data. |
| `dpv:Store` | Retaining data in a storage system. |
| `dpv:Use` | Using data in a process (broad; pair with a specific purpose). |
| `dpv:Retrieve` | Fetching data from a storage system or another party. |
| `dpv:Organise` | Structuring or ordering data (filing, sorting, tagging). |
| `dpv:Analyse` | Analysing data to derive insights or conclusions. |
| `dpv:Derive` | Producing new data from existing data (scoring, aggregation, inference). |
| `dpv:Profile` | Building a profile of an individual from multiple data points. |
| `dpv:Share` | Disclosing data to another party that is within the controller's processing scope. |
| `dpv:Disclose` | Making data available to a third party outside the controller's immediate scope. |
| `dpv:Transfer` | Moving data to another jurisdiction or to an external system. |
| `dpv:Transmit` | Sending data over a network (a narrower sub-case of Transfer or Disclose). |
| `dpv:Disseminate` | Publishing or broadly distributing data. |
| `dpv:Erase` | Deleting or destroying data. |
| `dpv:Anonymise` | Removing or transforming identifiers so the data can no longer be linked to an individual. |
| `dpv:Pseudonymise` | Replacing direct identifiers with a pseudonym while preserving a re-identification key. |
| `dpv:Align` | Combining or reconciling data from two or more sources. |
| `dpv:Copy` | Duplicating data from one system or medium to another. |

---

## Cross-reference to OpenSPP

The OpenSPP `spp_consent` module ships seed data for purposes and personal data categories in its database migration files. As of the version checked for this document, the OpenSPP extracted data in `external/openspp/` does not include consent-specific enum values. Check the OpenSPP documentation directly at https://docs.openspp.org/en/latest/ for the current seed values when integrating with OpenSPP deployments.

---

## Use as guidance, not schema

These URIs are starting points. Do not copy the full list into your records. Set only the URIs that accurately describe your program's processing. Overstating the scope of processing in a consent record is a compliance problem, not a safety margin.

The DPV hierarchy is much larger than this list. This list covers the range relevant to social protection, humanitarian assistance, and civil registration programs. For other domains, browse the full DPV at https://w3id.org/dpv.
