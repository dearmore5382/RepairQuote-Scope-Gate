# StudioNet end-to-end verification

Contract: [`0x5c2E4331B735FA702F2Ba62d2F10D3d0dCFc70D9`](https://explorer-studio.genlayer.com/address/0x5c2E4331B735FA702F2Ba62d2F10D3d0dCFc70D9)

Source SHA-256: `9a97bf34b6c01d93662823951d555c44f7000f10c2d12872f796fa20cb02425b`. StudioNet bytecode/source parity was verified before testing.

The updated deployment completed 16/16 checkpointed two-wallet transactions. Every transaction finalized with validator agreement and was followed by authoritative contract readback.

| Scenario | Result | Explorer |
|---|---|---|
| Create happy review | Review `0` | [transaction](https://explorer-studio.genlayer.com/tx/0x6d8de8cfc9d10b32a47d246edcb67178dc7a0deb5d27d797917187d8902d1185) |
| Second wallet captures creator's locked sources | `SOURCES_CAPTURED` | [transaction](https://explorer-studio.genlayer.com/tx/0xa116121be3c57684fb24902b913714c1830d620bb73b631a6d1cfb5f26fe9fb1) |
| Happy assessment | `QUOTE_ACCEPTABLE` | [transaction](https://explorer-studio.genlayer.com/tx/0x234a49f01560bffa04084b2a45164072a442b655ecab489de573c969112a0832) |
| Second wallet attempts creator-only close | `CREATOR_ONLY`, state unchanged | [transaction](https://explorer-studio.genlayer.com/tx/0x78473c45e2cbd6ee9decfc8bf55a8f65d40531dc1ca7f44dac96f2f0437ba4a0) |
| Creator closes review | `REVIEW_CLOSED` | [transaction](https://explorer-studio.genlayer.com/tx/0x26c16b6be9b93919e6d584acb7a27fa6987fc12a6a83a0244d6d010f6647e694) |
| Out-of-scope assessment | `SCOPE_VIOLATION` | [transaction](https://explorer-studio.genlayer.com/tx/0x88b335735d9e11dcd7a1dd855ae54d46f676c38dab09d8534e4f769cdf404729) |
| Ambiguous assessment | `REVIEW_REQUIRED` | [transaction](https://explorer-studio.genlayer.com/tx/0x65d127a25b1ed145f6c69e4556764b780244ac4c46f9471350c00912933fccf2) |
| Wrong approved-scope digest | `APPROVED_SCOPE_HASH_MISMATCH`, review remains `DRAFT` | [transaction](https://explorer-studio.genlayer.com/tx/0x3e3814013c198c6aa15f2fd4169118e2d1ca3ee78fa7738fec73d54360d0e79a) |

Additional verified controls include invalid title rejection, assessment-before-capture rejection, assessment replay rejection, and immutable readback after failed actions. The complete arguments, all 16 hashes, expected/actual returns, and post-state snapshots are in [`live-0x5c2e4331b735fa702f2ba62d2f10d3d0dcfc70d9.json`](live-0x5c2e4331b735fa702f2ba62d2f10d3d0dcfc70d9.json).
