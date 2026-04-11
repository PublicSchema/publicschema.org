# GovStack Payment Building Block: Mapping Research

## Source

- **System:** GovStack Payment Building Block (BB)
- **Source location:** `/Users/jeremi/Projects/201-Mauritania/govstack-review/bb-payments/api`
- **Spec version:** OpenAPI 3.0.0, individual files versioned 1.0.0-1.0.3
- **Date reviewed:** 2026-04-11

## Overview

The GovStack Payment BB is a specification (not a running system) that defines APIs for payment processing in government service delivery. It acts as a **payment switch/hub** between government agencies (Source BBs) and financial service providers (DFSPs, banks, mobile money operators).

The BB is split into three independent API families:

| Family | Flow direction | Relevance to PublicSchema |
|--------|---------------|--------------------------|
| **G2P** (Government-to-Person) | Govt agency -> Payments BB -> Financial institution -> Beneficiary | **High** -- bulk disbursement to beneficiaries |
| **Voucher** | Govt agency -> Payments BB -> Voucher Engine -> Agent/Merchant | **High** -- voucher lifecycle and redemption |
| **P2G** (Person-to-Government) | Citizen -> Payer FI -> Payments BB -> Govt Biller | **Low** -- bill payment is the reverse of benefit delivery |

## Key architectural differences from other mapped systems

Unlike the other six systems mapped in PublicSchema (OpenSPP, openIMIS, DHIS2, FHIR R4, OpenCRVS, DCI), the GovStack Payment BB is:

1. **An API specification, not a data model.** It defines operations and message schemas, not persistent entities. There is no "Beneficiary" table or "Payment" entity in the traditional sense; instead, there are request/response schemas for API calls.

2. **A payment infrastructure layer, not a program management system.** It does not model programs, enrollments, eligibility, or entitlements. It receives payment instructions from an upstream "Source BB" (which could be OpenSPP, openIMIS, etc.) and executes them.

3. **Opaque on semantics.** Many enum values are numeric codes (`00`, `01`, `02`) without labels in the spec. The `paymentModality` codes (00-04) are never defined with meanings in the API files themselves.

4. **Callback-driven (async).** Most operations return `202 Accepted` with results delivered to a callback URL. This is an architectural pattern, not a semantic concept.

## Concept-level mapping

### Concepts with meaningful overlap

| PublicSchema concept | GovStack Payment BB equivalent | Mapping quality | Notes |
|---------------------|-------------------------------|----------------|-------|
| PaymentEvent | **Batch Detail record** (BatchDetails response) | Partial | Individual transaction within a batch. Has amount, currency, status, payee/payer IDs, fees, timestamps. Missing: link to entitlement/enrollment, delivery channel as a vocabulary. |
| VoucherRedemption | **Voucher Redemption** (VoucherRedemption.yml) | Partial | Synchronous redemption at agent. Has serial number, agent ID, secret number, amount, timestamp, transaction ID. Missing: link to voucher record, items redeemed. |
| Entitlement | **Credit Instruction** (within BulkPayment batch) | Weak | A credit instruction is "pay this amount to this person," which is closer to a payment instruction than an entitlement. The entitlement concept (right to receive) lives upstream in the Source BB, not in the Payment BB. |
| BenefitSchedule | No equivalent | None | Program-level benefit design is outside the Payment BB scope. |
| Person / Identifier | **Beneficiary record** (ID Mapper) | Weak | The Payment BB stores `payeeIdentity` (functional ID), `financialAddress`, and `bankingInstitutionCode`. This is a payment routing record, not a person record. |

### Concepts with no overlap

These PublicSchema concepts have no representation in the GovStack Payment BB:

- Program, Enrollment, EligibilityDecision, AssessmentFramework, AssessmentEvent
- Household, Family, Farm, Group, GroupMembership
- Grievance, Referral
- Address, Location, GeographicArea
- Relationship, HazardEvent

### GovStack Payment BB concepts with no PublicSchema equivalent

| GovStack concept | Description | Why no mapping |
|-----------------|-------------|----------------|
| **Batch** | A group of payment instructions processed together | PublicSchema models individual payments (PaymentEvent), not batch processing. Batching is an operational/infrastructure concern. |
| **Bill** (P2G) | A government bill for citizen payment | P2G (person-to-government) is outside social protection delivery scope. |
| **RTP (Request to Pay)** (P2G) | Biller-initiated payment request | Same as above -- P2G flow. |
| **ID Mapper** | Links functional IDs to financial addresses | Payment routing infrastructure, not a domain concept. |
| **Funds Authorization** | Pre-authorization of batch funds from payer bank | Financial operations infrastructure. |
| **Account Validation** | Verification that destination accounts exist | Financial operations infrastructure. |

## Vocabulary-level mapping

### 1. paymentModality (G2P) -> delivery-channel

The `paymentModality` field appears throughout the G2P APIs with enum values `00`-`04`. The API YAML files do not label the codes, but the spec document (`spec/7-data-structures.md` section 7.1.1) defines them:

| GovStack code | Spec label | PublicSchema `delivery-channel` | Confidence |
|--------------|-----------|-------------------------------|-----------|
| `00` | Bank Account | `bank_transfer` | High |
| `01` | Mobile Money | `mobile_money` | High |
| `02` | Voucher | null | High (see note) |
| `03` | Digital Wallet | null | Medium |
| `04` | Proxy | null | Medium |

**Gaps:**
- v2_only: `cash`, `agent_network`, `prepaid_card`, `service_point`, `other`
- external_only: `02` (Voucher: is a benefit modality, not a delivery channel), `03` (Digital Wallet: no exact match; closest is `mobile_money`), `04` (Proxy: intermediary receiving on behalf; closest is `agent_network`)

**Notes:**
- GovStack's `paymentModality` conflates delivery channel and benefit modality. Code `02` (Voucher) is a benefit form, not a delivery mechanism. It maps to `benefit-modality: voucher` rather than any `delivery-channel` code.
- Code `03` (Digital Wallet) could arguably map to `mobile_money` (both are electronic wallet-based), but Digital Wallet is broader (includes non-mobile wallets).
- Code `04` (Proxy) describes an intermediary arrangement (someone receives on behalf of the beneficiary), which is orthogonal to delivery channel. Could map to `agent_network` if the proxy is a formal agent.

### 2. Voucher status codes -> voucher-status

The `VoucherStatus.yml` response includes a `status` integer field described in prose (not formally enumerated) with values 01-06 and 9.

| GovStack code | Inferred meaning | PublicSchema `voucher-status` | Confidence |
|--------------|-----------------|------------------------------|-----------|
| `01` | Pre-activated (created, not yet activated) | `created` | High |
| `02` | Activated (ready for distribution/use) | `issued` | High |
| `03` | Redeemed | `redeemed` | High |
| `04` | Cancelled | `cancelled` | High |
| `05` | Suspended | `suspended` | High |
| `06` | Expired | `expired` | High |
| `9` | Error | null | High |

**Gaps:**
- v2_only: `partially_redeemed`
- external_only: `9` (error, operational state not modeled as a lifecycle status)

**Notes:**
- GovStack's "pre-activated" (01) maps well to `created`. The two-phase create-then-activate model in GovStack means 01 = generated but not yet usable, which aligns with "created" (generated but not yet distributed).
- GovStack's "activated" (02) maps to `issued` because activation in GovStack means the voucher is now usable/distributable, which is semantically equivalent to "issued" (distributed to beneficiary).
- `suspended` is being added to PublicSchema's voucher-status vocabulary based on this mapping.

### 3. Batch transaction status -> payment-status

The `BatchDetails.yml` response includes `status` and `statusDetail` as free strings (not enumerated). However, the batch-level counters in `BulkPaymentStatusUpdate.yml` use `ongoing`, `failed`, `completed` as field names, implying at least three states.

| GovStack state (inferred) | PublicSchema `payment-status` | Confidence |
|---------------------------|------------------------------|-----------|
| ongoing / in-progress | `processing` | Medium |
| completed | `paid` | Medium |
| failed | `failed` | Medium |

**Notes:** Since the status field is not enumerated, actual implementations may use different string values. The mapping is based on the batch counter field names, which imply these three lifecycle states.

### 4. RTP requestStatus (P2G) -> payment-status (partial, low relevance)

The P2G RTP status vocabulary maps loosely to payment-status, but P2G is the reverse flow (citizen paying government). Including for completeness:

| GovStack code | Meaning | PublicSchema `payment-status` | Notes |
|--------------|---------|------------------------------|-------|
| `COM` | Completed | `paid` | Semantic stretch -- "completed" in P2G means bill was paid |
| `PND` | Pending | `pending` | |
| `EXP` | Expired | null | No "expired" in payment-status |
| `CAN` | Cancelled | `cancelled` | |
| `RJC` | Rejected | `rejected` | |

### 5. Bill payment status (P2G) -> No mapping

`ACK`/`RJC` for bill payment acknowledgment and `Def`/`Dup`/`Und` for rejection reasons are P2G operational codes with no social protection delivery equivalent.

### 6. Beneficiary status -> No mapping

The `0`/`1` (inactive/active) beneficiary status is an infrastructure record state for the ID Mapper, not a program enrollment or payment status.

### 7. Funds authorization status -> No mapping

`Y`/`N` (authorized/not authorized) is a bank-level funds check, not a domain concept.

### 8. aliasType (P2G) -> identifier-type (weak)

| GovStack code | Inferred meaning | PublicSchema `identifier-type` | Confidence |
|--------------|-----------------|-------------------------------|-----------|
| `00` | Phone number | null (phone is a property, not an ID type) | Low |
| `01` | Email | null (email is not an ID type) | Low |
| `02` | National ID | `national_id` | Medium |

**Notes:** aliasType is used for payment routing in the P2G RTP flow, not for person identification. The overlap is incidental.

### 9. currency -> currency (same standard)

Both use ISO 4217. GovStack specifies `maxLength: 3` for currency fields, matching the ISO 4217 alpha-3 code format. No code-level mapping needed.

## Properties-level mapping

The GovStack Payment BB fields that map to PublicSchema properties:

| GovStack field | Context | PublicSchema property | Notes |
|---------------|---------|----------------------|-------|
| `amount` | Credit instruction, voucher, batch detail | `payment_amount` / `amount` | Direct match |
| `currency` | Credit instruction, voucher, batch detail | `payment_currency` / `currency` | ISO 4217, same standard |
| `paymentMode` | Credit instruction (BulkPayment) | `delivery_channel` | See paymentModality mapping above |
| `payeeFunctionalID` / `payeeIdentity` | Beneficiary, voucher instruction | `identifier_value` (on Identifier) | Functional ID used for payment routing |
| `serialNumber` | Voucher | No direct property | Voucher serial number; PublicSchema VoucherRedemption uses `voucher_ref` |
| `agentID` | Voucher redemption | `redemption_agent` | Agent/merchant performing redemption |
| `transactionId` | Batch detail, voucher redemption | `transaction_reference` | Payment transaction reference |
| `startedAt` / `completedAt` | Batch detail | `payment_date` | completedAt is closest to payment_date |
| `status` | Batch detail | `payment_status` | See batch transaction status mapping |
| `descriptionText` / `narration` | Credit instruction, voucher | No direct property | Free-text payment description |
| `batchId` | Batch operations | No direct property | Batch grouping is not modeled in PublicSchema |
| `financialAddress` | Beneficiary | No direct property | Bank account / mobile wallet address |
| `bankingInstitutionCode` | Beneficiary | No direct property | DFSP / BIC code |

## Spec quality observations

These are worth noting because they affect mapping confidence and implementation guidance:

1. **Unlabeled enum codes.** `paymentModality` (00-04), `aliasType` (00-02), and `requestType` (00-01) have no documented meanings in the API files.
2. **Inconsistent field naming.** `requestId` vs `requestID` vs `RequestId` vs `RequestID` across files. `payeeIdentity` vs `payeeFunctionalID` for the same concept.
3. **Header naming inconsistency.** `X-Callback-URL` vs `X-Callback_URL`, `X-PayerFI-Id` vs `PayerFI-Id` vs `X-Payer FI-ID` (with space).
4. **Invalid OpenAPI patterns.** `maxLength` on integer fields, GET with request body, `type: float` instead of `type: number, format: float`.
5. **Copy-paste errors.** VoucherRedemption.yml uses `command: cancel` (should be `redeem`). `billInquiryBillerResponse.yml` has prose text before the YAML.
6. **No `required` arrays** on most request/response body schemas.
7. **`serialNumber` maxLength varies** from 6 to 20 across different files for the same field.

## Recommendation

Given the nature of the GovStack Payment BB (an API spec for payment infrastructure, not a domain data model), the mapping is narrower than for systems like OpenSPP or openIMIS. The meaningful mappings are:

1. **voucher-status** -- Good alignment with GovStack voucher lifecycle (5 of 6 codes map). Worth adding to system_mappings.
2. **delivery-channel** -- Partial alignment with paymentModality, but code labels need confirmation from the full GovStack spec document (not just the API YAMLs).
3. **payment-status** -- Weak alignment because batch transaction status is not enumerated in the API spec.
4. **currency** -- Same standard (ISO 4217), no mapping needed.

The P2G family and most G2P infrastructure concepts (batches, ID mapper, funds authorization, account validation) are outside PublicSchema's scope.

### Resolved questions

1. **paymentModality code labels** are documented in `spec/7-data-structures.md` section 7.1.1. Codes confirmed: 00=Bank Account, 01=Mobile Money, 02=Voucher, 03=Digital Wallet, 04=Proxy.
2. **`suspended` added to voucher-status** as a new canonical value.
3. **P2G family is mapped** with appropriate caveats about the reverse flow context.
