# RepairQuote Scope Gate specification

## Purpose

Determine whether line items in one contractor repair quote are semantically contained within one authenticated approved scope. The system is deliberately narrow and non-payable.

## Input packages

Approved scope keys: `schema_version`, `project_ref`, `approved_items`. Each approved item has exactly `scope_id`, `area`, and `work`.

Quote keys: `schema_version`, `project_ref`, `quote_items`. Each quote item has exactly `line_id`, `area`, `work`, and `scope_ref`.

Both documents must use schema `1.0`, share the same `project_ref`, contain 1–40 unique items, and match their registered SHA-256 digest byte-for-byte.

## Verdicts

- `QUOTE_ACCEPTABLE`: every line is within its referenced approved item and no work is duplicated.
- `SCOPE_VIOLATION`: at least one line is clearly outside scope, contradicts the approved area/work, or duplicates work.
- `REVIEW_REQUIRED`: wording is genuinely ambiguous or insufficient.

## Safety properties

- No payable methods or value transfer.
- Only the creator can capture or close.
- Failed fetch, wrong digest, or invalid schema causes zero snapshot mutation.
- Assessment is allowed only after authenticated capture.
- Assessed records are append-only and assessment replay is rejected.
- AI returns one enum; it cannot write prose, prices, remedies, or arbitrary state.
- Branch-moving URLs are discouraged operationally; live evidence uses commit-pinned raw URLs.
