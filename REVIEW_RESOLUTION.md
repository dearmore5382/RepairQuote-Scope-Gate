# Steward Review Resolution

This document records how RepairQuote Scope Gate addressed the steward's requested changes. It is a release note for the reviewed deployment, not a general product description.

## Review request addressed

The steward identified two practical problems:

1. A normal lifecycle transition was rejected with `CREATOR_ONLY`.
2. The frontend needed a clearer multi-page flow and a public way to inspect finalized and completed cases.

Both items are resolved in the current contract, public frontend, and live StudioNet evidence.

## 1. The rejected lifecycle transition

### Root cause

The earlier permission model unnecessarily restricted source capture to the review creator. Capture does not alter the creator's URLs or expected digests. It only fetches the already locked public sources, verifies their exact bytes, validates their schemas, and records the authenticated snapshots.

Requiring the creator for that operation made the workflow brittle and produced the steward-observed `CREATOR_ONLY` rejection.

### Current permission boundary

The reviewed contract separates verification work from the terminal owner action:

| Method | Who may call it | Reason |
| --- | --- | --- |
| `create_review` | Any wallet | The caller becomes creator of that review. |
| `capture_sources` | Any wallet | It verifies creator-locked URLs and digests; the caller cannot replace them. |
| `assess_quote` | Any wallet | It evaluates only the authenticated snapshots stored by capture. |
| `close_review` | Review creator | Closing is the creator-controlled terminal transition. |
| `get_review` | Public read | Reviewers can independently inspect authoritative state. |

The resulting lifecycle is:

```text
DRAFT -> CAPTURED -> ASSESSED -> CLOSED
```

Each transition is guarded by its required predecessor state. Replays and out-of-order calls are rejected.

### Live proof of the fix

The 16-step StudioNet run used two wallets. A second wallet successfully called `capture_sources` for a review created by the first wallet. This proves the formerly blocked transition is now intentionally permissionless while the creator-only close boundary remains enforced.

The same run also proved that a non-creator cannot close a review.

## 2. Frontend rebuilt around the reviewer journey

The frontend is no longer a single dashboard surface. It now exposes three direct routes with distinct purposes:

- **Overview (`/`)** explains the trust model, four-step lifecycle, decision boundary, and common questions.
- **New review (`/create`)** opens directly at the source-binding form and lifecycle controls without repeating the landing-page hero.
- **Explorer (`/explorer`)** reads records from the deployed contract and displays completed and in-progress cases without requiring a wallet.

The primary navigation is centered and remains visible. Calls to action use ordinary links so route changes work reliably on the deployed Worker.

## State-aware interaction guidance

Lifecycle controls now explain the next valid action instead of behaving like dead buttons.

Examples:

- A `DRAFT` review directs the user to capture its locked sources.
- A `CAPTURED` review directs the user to assess it.
- An `ASSESSED` review explains that only its creator may close it.
- A `CLOSED` review is clearly marked read-only.
- Trying Capture on review `0`, which is already closed, reports: `This action requires DRAFT; review 0 is CLOSED.`

Wallet connection is requested only when a valid write action actually needs a signer. Public contract reads remain available without connecting a wallet.

## Public Explorer evidence

The public Explorer currently enumerates four authoritative StudioNet records:

| Review | State | Verdict | Purpose |
| --- | --- | --- | --- |
| `000` | `CLOSED` | `QUOTE_ACCEPTABLE` | Complete happy path and frozen readback. |
| `001` | `ASSESSED` | `SCOPE_VIOLATION` | Authenticated out-of-scope quote. |
| `002` | `ASSESSED` | `REVIEW_REQUIRED` | Authenticated but ambiguous quote. |
| `003` | `DRAFT` | `UNASSESSED` | Deliberate digest mismatch; no snapshot or verdict was stored. |

The page also links directly to the deployed address in GenLayer Explorer so a reviewer can leave the application and independently inspect the contract.

## Source authenticity and bounded AI behavior

The reviewer flow does not rely on uploaded images or subjective damage evidence.

1. The creator registers commit-pinned raw GitHub JSON URLs and expected SHA-256 digests.
2. Validators fetch the exact public bytes.
3. Strict consensus recomputes and verifies both digests and the shared schemas.
4. Only authenticated snapshots reach the semantic assessment.
5. The intelligent contract returns one bounded result: `QUOTE_ACCEPTABLE`, `REVIEW_REQUIRED`, or `SCOPE_VIOLATION`.

It does not decide price fairness, workmanship, urgency, liability, or payment.

## Verification summary

- Matching local/deployed contract SHA-256: `9a97bf34b6c01d93662823951d555c44f7000f10c2d12872f796fa20cb02425b`
- StudioNet live matrix: **16/16 finalized steps passed**
- Frontend unit tests: **5/5 passed**
- Contract tests: **9/9 passed**
- Frontend lint: **passed**
- Production build: **passed**
- Happy, failure, conflict, permission, replay, digest-mismatch, and authoritative-readback paths are covered.

## Reviewed release

- [Public application](https://repairquote-scope-gate.dearmorescheuer5382.workers.dev)
- [StudioNet contract](https://explorer-studio.genlayer.com/address/0x5c2E4331B735FA702F2Ba62d2F10D3d0dCFc70D9)
- [Human-readable live transaction evidence](verification/STUDIONET_E2E.md)
- [Live result summary](verification/LIVE_RESULTS.md)
- [Machine-readable checkpoint](verification/live-0x5c2e4331b735fa702f2ba62d2f10d3d0dcfc70d9.json)

The deployed frontend targets this exact reviewed contract.
