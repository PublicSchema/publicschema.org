# Privacy and Data Protection

<aside class="illustration-placeholder">
  <strong>Illustration placeholder:</strong> A data minimization flow. Reader task: help a program team decide which fields should be collected, exchanged, disclosed, aggregated, or excluded. Show sensitive attributes being filtered before data leaves the source system, with a visible review checkpoint.
</aside>

PublicSchema helps teams describe data consistently. It does not make data safe by itself. Public service delivery data can expose poverty status, disability, displacement, household composition, location, grievances, payment history, and identity relationships. Treat every adoption package as a protection decision.

This page is practical guidance, not legal advice. Programs still need to follow applicable law, policy, donor requirements, and local safeguards.

## Protection principles

| Principle | Practical meaning |
|---|---|
| Purpose limitation | Exchange only for a named service, report, verification, or coordination need |
| Data minimization | Include the smallest field set that satisfies the purpose |
| Proportionality | Do not use credentials, linkage, or disclosure if a safer aggregate is enough |
| Separation of concerns | Keep operational case notes, risk details, and audit data out of routine exchange packages |
| Transparency | Record what is shared, with whom, under which authority or agreement |
| Retention control | Set deletion or review dates for exports, samples, and staging files |
| Reviewability | Make privacy decisions visible in package documentation |

## Start with a field review

Before publishing an API, file, credential, or mapping package, classify fields:

| Field | Purpose | Sensitivity | Share? | Protection decision |
|---|---|---|---|---|
| `Enrollment.status` | Confirm service eligibility | medium | yes | Share canonical status only |
| `PaymentEvent.amount` | Reconcile delivery | medium | yes | Share amount, currency, period |
| `Person.dateOfBirth` | Match recipient | high | maybe | Prefer age band when exact date is not needed |
| Case notes | Operational follow-up | high | no | Exclude from exchange |
| Bank account number | Payment execution | high | no | Keep in payment system, share payment reference only |

If the purpose cannot justify the field, leave it out.

## Minimize identifiers

Identifiers are often the riskiest part of interoperability work. Decide what kind of identifier the consumer truly needs:

| Need | Safer pattern |
|---|---|
| Count beneficiaries | Aggregate by area, program, period, or status |
| Detect duplicates within one controlled project | Use a project-specific pseudonymous identifier |
| Reconcile a payment batch | Use a batch reference and payment event id |
| Verify a credential at a service point | Use cryptographic proof and disclose only required claims |
| Link records across agencies | Require a written governance decision and documented safeguards |

Avoid creating a universal identifier for convenience. Linkage that is easy for implementers can be dangerous for people.

## Use safe examples and samples

Example files should be synthetic unless there is a documented reason to use real records.

Safe sample rules:

- Do not include real names, phone numbers, document numbers, addresses, bank details, case notes, or exact locations of vulnerable people.
- Use plausible but synthetic dates and amounts.
- Avoid rare combinations that could re-identify a person or household.
- Mark sample files clearly as synthetic.
- Keep sample data small.

## Privacy review checklist

| Question | Decision |
|---|---|
| What purpose does this exchange serve? | |
| Who receives the data? | |
| Which fields are excluded and why? | |
| Which fields are sensitive or potentially identifying? | |
| Can any fields be aggregated, generalized, hashed, or omitted? | |
| How long will exports, logs, and samples be retained? | |
| Who can approve new consumers or new uses? | |
| What happens if data is sent to the wrong recipient? | |

Record the answers in the package. A future maintainer should not have to guess why a field was included.

## Credentials need extra review

Credentials can be powerful because they let a person carry claims across systems. They also create new risks when claims are overshared, retained by verifiers, or used outside their intended context.

For each credential, document:

| Decision | Example |
|---|---|
| Claim purpose | Prove active enrollment for a service |
| Issuer trust | Which authority can issue this credential |
| Holder control | How the holder stores and presents it |
| Selective disclosure | Which claims can be hidden |
| Verifier policy | Which claims a verifier is allowed to request |
| Status and revocation | How suspended, expired, or withdrawn credentials are handled |
| Retention | Whether verifiers may store presentation data |

Do not issue a credential when a one-time API check, paper receipt, or aggregate report is safer.

## Package evidence

Include a privacy note in every adoption package:

```markdown
# Privacy note

Purpose:
Consumers:
Sensitive fields reviewed:
Fields excluded:
Identifier strategy:
Sample data strategy:
Retention rule:
Approval owner:
Last review date:
```

## Next

- Use [Publish Exchanges and APIs](/handbook/publish-exchanges/) to apply these decisions to APIs, files, and events.
- Use [Issue Credentials](/handbook/issue-credentials/) when the exchange involves holder-controlled credentials.
- Use [Package and Validate Your Work](/handbook/validate-and-package/) to include the privacy note in a handover package.
