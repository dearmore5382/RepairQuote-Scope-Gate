# Studionet Live Results

## Historical deployment excluded from release

- Address: `0x789c96431699b1e280E36A57102A0842Bae17aE5`
- Source parity: exact for source SHA-256 `e55e7e8f75881d62abfad04315f2414fe64921f98ae313d9191bccc83d3db334`
- Deterministic lifecycle and authority checks: passed through a sealed report.
- First assessment: `FINALIZED`, `MAJORITY_AGREE`, returned `ASSESSMENT_RETRYABLE`, and authoritative report state remained `SEALED` with no mutation.
- One explicit retry: `FINALIZED`, leader returned `TENANT_RESPONSIBLE`, but consensus was `MAJORITY_DISAGREE` (2 agree, 3 disagree).
- Retry transaction: `0x3e0dd97d0be6ee4c4f9973d7d436dae28ca51eba84e77aaff69d52050ad24867`

The matrix stopped immediately. No third retry was submitted, no positive outcome was recorded, and this deployment is not wired into the frontend or claimed as a release. The evidence shows that independent full re-derivation of five coupled observations was too variable even for a deliberately clear case. The successor source changes validator topology to independent candidate falsification while preserving deterministic derivation and fail-closed behavior.
