# Live results

Matching-source Studionet deployment: `0x5c2E4331B735FA702F2Ba62d2F10D3d0dCFc70D9`.

Preflight verified chain ID `61999` and exact deployed/local SHA-256 parity at `9a97bf34b6c01d93662823951d555c44f7000f10c2d12872f796fa20cb02425b`.

The frozen live workflow completed **16/16** steps with FINALIZED consensus and authoritative readback:

- authenticated happy quote: `QUOTE_ACCEPTABLE`;
- authenticated out-of-scope quote: `SCOPE_VIOLATION`;
- authenticated ambiguous quote: `REVIEW_REQUIRED`;
- invalid title, assessment before capture, outsider close, and assessment replay were rejected;
- a second wallet successfully captured the creator's locked public sources, proving the fixed permissionless transition;
- creator close produced `REVIEW_CLOSED`;
- an exact GitHub URL paired with a false SHA-256 returned `APPROVED_SCOPE_HASH_MISMATCH`, and the record remained `DRAFT` with no captured snapshot or verdict.

Public machine-readable evidence: `live-0x5c2e4331b735fa702f2ba62d2f10d3d0dcfc70d9.json`.

Human-readable transaction links: `STUDIONET_E2E.md`.
