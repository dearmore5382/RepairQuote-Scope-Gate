# RepairScope Specification

## Product boundary

RepairScope records a narrow rental repair dispute for one property component. It compares a jointly sealed move-in baseline and duty policy with statements sealed later by the owner and tenant. Validators classify bounded semantic observations; deterministic contract code derives a responsibility category.

It does **not** inspect a physical property, authenticate photographs, determine legal liability, calculate damages, transfer funds, or prove that either party's statement is true. Images may be shown outside the protocol as context, but they never authorize an outcome.

GenLayer is necessary because mapping natural-language condition records, repair duties, and two party accounts into bounded observations requires contextual interpretation. Consensus changes the immutable outcome recorded for the report.

## Actors and lifecycle

- Owner creates a property record and nominates a distinct tenant.
- Owner may cancel an unaccepted draft if the tenant never participates.
- Tenant accepts the baseline and duty policy.
- Owner seals the jointly accepted property record.
- Either party opens one pending report.
- The counterparty adds one response.
- The reporter seals the two-statement record.
- Anyone may request assessment; unavailable analysis changes no state and remains retryable.
- Owner may close a property only with no pending report.

```text
Property: DRAFT -> ACCEPTED -> SEALED -> CLOSED
          DRAFT -> CANCELLED
Report:   OPEN -> RESPONDED -> SEALED -> FINALIZED
          OPEN -> WITHDRAWN
```

## Consequential observations

| Field | Closed values | Binding |
|---|---|---|
| analysis_status | AVAILABLE, UNAVAILABLE | exact |
| baseline_relation | PRE_EXISTING, NEW_DAMAGE, AMBIGUOUS | effect-aligned |
| damage_character | NORMAL_WEAR, NEGLECT, MISUSE, SYSTEM_FAILURE, ACCIDENT, UNCLEAR | effect-aligned |
| duty_alignment | OWNER, TENANT, SHARED, CONFLICT, UNCLEAR | effect-aligned |
| account_consistency | CONSISTENT, CONFLICTING, INCOMPLETE | effect-aligned |

The leader classifies the sealed texts. Each validator independently acts as a falsifier against the same sealed evidence and accepts only when every consequential observation and its deterministic effect are supported without contradiction. Free-form prose is never compared or stored.

## Precedence

1. Unavailable analysis -> `RETRYABLE`, no mutation.
2. Conflicting or incomplete accounts -> `INSUFFICIENT_EVIDENCE`.
3. Ambiguous baseline -> `INSUFFICIENT_EVIDENCE`.
4. Unknown or conflicting duty/damage -> `INSUFFICIENT_EVIDENCE`.
5. Pre-existing condition -> `OWNER_RESPONSIBLE`.
6. Normal wear -> `NORMAL_WEAR`.
7. System failure aligned to owner duty -> `OWNER_RESPONSIBLE`; contradiction -> insufficient.
8. Misuse aligned to tenant duty -> `TENANT_RESPONSIBLE`; contradiction -> insufficient.
9. Accident or shared duty -> `SHARED_RESPONSIBILITY`.
10. Neglect follows the sealed owner/tenant duty.

## Invariants

- No payable method and no custody.
- Interested-party statements are never treated as authenticated physical truth.
- Baseline and policy become usable only after both named parties act.
- At most one pending report per property.
- Only the counterparty can respond; only the reporter can seal or withdraw.
- Finalized reports are append-only and cannot be replayed or overwritten.
- Model output never directly selects a contract verdict.
- Wrong actor/state/revision is rejected before nondeterminism.
- Model failure or validator disagreement cannot create a substantive outcome.
