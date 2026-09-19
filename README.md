# RepairQuote Scope Gate

RepairQuote Scope Gate is a non-payable GenLayer dApp for checking whether a commercial repair quote stays within an approved repair scope. It deliberately avoids image-based damage attribution or competing party narratives.

## Trust model

1. A creator registers two commit-pinned HTTPS JSON URLs and their SHA-256 digests.
2. Any connected wallet may trigger source capture; validators fetch the exact bytes through `strict_eq` consensus.
3. The contract verifies both digests and a narrow shared schema before storing the snapshots.
4. Validators return one bounded semantic verdict: `QUOTE_ACCEPTABLE`, `REVIEW_REQUIRED`, or `SCOPE_VIOLATION`.
5. Contract code stores a deterministic reason and freezes the assessed record.

The contract does not decide price, workmanship, urgency, legal liability, or payment. Public fixtures are synthetic test data, not evidence of real work.

## Contract workflow

`DRAFT -> CAPTURED -> ASSESSED -> CLOSED`

- `create_review`: locks URLs and expected digests.
- `capture_sources`: permissionlessly fetches, hashes, validates, and snapshots both locked JSON documents.
- `assess_quote`: compares the quote with the authenticated scope.
- `close_review`: creator-only terminal transition.
- `get_review`: authoritative flat readback.

## Local verification

```text
pytest -q
npm test
npm run lint
npm run build
```

Deployment is intentionally unset until a matching-source Studionet contract passes the live happy, failure, and adversarial matrix.

## Verified deployment

- [Live dApp](https://repairquote-scope-gate.dearmorescheuer5382.workers.dev)
- [Studionet contract](https://explorer-studio.genlayer.com/address/0x5c2E4331B735FA702F2Ba62d2F10D3d0dCFc70D9)
- [Human-readable 16-step E2E evidence](verification/STUDIONET_E2E.md)
- [Machine-readable E2E checkpoint](verification/live-0x5c2e4331b735fa702f2ba62d2f10d3d0dcfc70d9.json)

The frontend now uses three reviewer-friendly pages: an overview, a guided review creator, and a public Explorer that enumerates finalized StudioNet records. Lifecycle buttons are state-aware; creator-only Close is disabled for unauthorized wallets instead of sending a transaction that the contract will reject.
