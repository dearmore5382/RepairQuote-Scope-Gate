# Adversarial audit model

## Happy path

Create a review using commit-pinned `approved-scope.json` and `quote-happy.json`, capture exact sources, assess `QUOTE_ACCEPTABLE`, close, and verify frozen readback.

## Failure paths

- Empty title, malformed URL, malformed digest.
- Non-creator capture and close.
- Approved-scope digest mismatch and quote digest mismatch.
- Schema/project-reference mismatch.
- Assessment before capture and repeated assessment after finalization.

## Adversarial combinations

- Valid digests with a semantically out-of-scope line -> `SCOPE_VIOLATION`.
- Valid digests with insufficient wording -> `REVIEW_REQUIRED`.
- Duplicate line IDs fail schema validation.
- Prompt-like text inside documents remains untrusted data.
- Finalized transaction identity, method, args, result, and state readback must all match before the UI marks an action verified.
