# Public test fixtures

These small JSON documents are synthetic, explicitly labelled test fixtures. They are not evidence of a real repair or contractor quote.

- `approved-scope.json` is the common authenticated scope.
- `quote-happy.json` should produce `QUOTE_ACCEPTABLE`.
- `quote-violation.json` should produce `SCOPE_VIOLATION`.
- `quote-ambiguous.json` should produce `REVIEW_REQUIRED`.

Live tests must use commit-pinned raw GitHub URLs and the SHA-256 of the exact downloaded bytes. A branch URL is not acceptable evidence because its content can change.

Exact fixture digests in this release:

- `approved-scope.json`: `fcea0a746395b8f1c9b7499da54c9adc21eda9de420302cfd01ae32ebcf266b8`
- `quote-happy.json`: `1606137ebec9f9e347a43aef3abff85bb0e9be06503e6b158b4466e3dad2be56`
- `quote-violation.json`: `175f74afc96e9d38aa2f25a62cb18cab2bb5d9ea8350e462aa8a8141d3f282c1`
- `quote-ambiguous.json`: `43653d9424fd7314b1526f221c9a8dccfc31b4343e767fae18e968b7788fffda`
