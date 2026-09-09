# RepairQuote Scope Gate

RepairQuote Scope Gate is a non-payable GenLayer dApp for checking whether a commercial repair quote stays within an approved repair scope. It deliberately avoids image-based damage attribution or competing party narratives.

## Trust model

1. A creator registers two commit-pinned HTTPS JSON URLs and their SHA-256 digests.
2. Validators fetch the exact bytes through `strict_eq` consensus.
3. The contract verifies both digests and a narrow shared schema before storing the snapshots.
4. Validators return one bounded semantic verdict: `QUOTE_ACCEPTABLE`, `REVIEW_REQUIRED`, or `SCOPE_VIOLATION`.
5. Contract code stores a deterministic reason and freezes the assessed record.

The contract does not decide price, workmanship, urgency, legal liability, or payment. Public fixtures are synthetic test data, not evidence of real work.

## Contract workflow

`DRAFT -> CAPTURED -> ASSESSED -> CLOSED`

- `create_review`: locks URLs and expected digests.
- `capture_sources`: fetches, hashes, validates, and snapshots both JSON documents.
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
- [Studionet contract](https://explorer-studio.genlayer.com/address/0x5D3618484389dDb5788F6AC975A8163aEac21C4f)
- [Human-readable 16-step E2E evidence](verification/STUDIONET_E2E.md)
- [Machine-readable E2E checkpoint](verification/live-0x5d3618484389ddb5788f6ac975a8163aeac21c4f.json)
