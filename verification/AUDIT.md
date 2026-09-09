# Pre-deployment Adversarial Audit

Date: 2026-09-09

## Scope and result

The reviewed source is `contracts/RepairScope.py`. Local syntax, semantic derivation, direct contract behavior, frontend protocol, lint, and production build gates pass. This is a pre-deployment audit; it is not live-chain evidence.

## Happy paths

- Two-party baseline: owner creates, tenant accepts, owner seals.
- Report lifecycle: either party opens, only counterparty responds, only reporter seals.
- All five terminal categories are covered: owner, tenant, shared, normal wear, and insufficient evidence.
- Finalized report readback is immutable; a replay cannot reassess it.

## Failure paths

- Empty/bounded text and invalid tenant identity are rejected before state mutation.
- Wrong tenant, owner, reporter, counterparty, state, pending slot, and revision are rejected before nondeterminism.
- A pending report blocks another report and property closure.
- Malformed model output maps to unavailable analysis.
- Unavailable analysis returns `ASSESSMENT_RETRYABLE` with byte-equivalent property and report readback.
- Frontend refuses writes before verified deployment and refuses a second write while a transaction is unresolved.
- `FINALIZED` alone is not success: execution, consensus, receipt identity, method/arguments, and authoritative readback are all required.

## Adversarial combinations

- Conflicting party accounts take precedence over pre-existing or damage labels.
- Ambiguous baseline blocks a substantive responsibility label.
- System failure paired with tenant duty and misuse paired with owner duty fail to insufficient evidence.
- Prompt injection inside a party statement cannot provide extra keys or a final verdict.
- Narrative differences are tolerated only when independently derived `outcome + reason` remain identical.

## Findings fixed during build

- Test identities use the same 20-byte address representation accepted by the contract.
- Frontend receipt reconciliation verifies the exact transaction identity, calldata, returned value, and state readback.
- The supplied image is branding only; no image or mutable web source sits on the adjudication critical path.
- Live evidence from the first matching-source deployment showed that independent full re-derivation of five coupled fields produced majority disagreement despite the same leader outcome. The successor uses a prover/falsifier topology: validators test the leader's complete candidate and deterministic effect against the same sealed evidence, rather than generating another five-field tuple and comparing it indirectly.

## Residual boundary

The protocol cannot prove physical damage, authorship truth, fair market repair cost, or legal liability. Live validator variability and Studio transaction behavior remain to be tested after deployment using the frozen matrix.

The historical address `0x789c96431699b1e280E36A57102A0842Bae17aE5` is excluded from release. Its failed/retryable attempts remain preserved in `verification/LIVE_RESULTS.md` and the public JSON ledger.

The optional browser WebMCP staging tool is implemented but not claimed as runtime-verified because this pre-deployment environment did not expose a supported WebMCP context.
