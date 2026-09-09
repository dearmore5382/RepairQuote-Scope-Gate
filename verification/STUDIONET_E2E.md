# Studionet end-to-end evidence

Contract: [`0x5D3618484389dDb5788F6AC975A8163aEac21C4f`](https://explorer-studio.genlayer.com/address/0x5D3618484389dDb5788F6AC975A8163aEac21C4f)

Deployed/local source SHA-256: `db38ed4f22ce58b1d2f8cf870487867e6f3d1c3eac7d5d1310f0f43f3a4df03f` — exact byte parity verified on chain ID `61999`.

Fixture source commit: [`b379644f492cd730e9f7655052b3138250dc65b8`](https://github.com/dearmore5382/RepairQuote-Scope-Gate/tree/b379644f492cd730e9f7655052b3138250dc65b8/test-fixtures)

Every row below reached `FINALIZED`, returned the expected contract result, and passed authoritative `get_review_count` / `get_review` readback. The complete readbacks and immutable inputs are preserved in [`live-0x5d3618484389ddb5788f6ac975a8163aeac21c4f.json`](./live-0x5d3618484389ddb5788f6ac975a8163aeac21c4f.json).

| ID | Path | Method | Expected = actual | Transaction |
|---|---|---|---|---|
| F1 | Failure: empty title | `create_review` | `INVALID_TITLE` | [`0x203756…e40ab`](https://explorer-studio.genlayer.com/tx/0x20375606d537ed5639f64a3735aee19d537898375002a658a1083485cf4e40ab) |
| H1 | Happy: register authenticated package | `create_review` | review `0` | [`0xa9d425…c7fee`](https://explorer-studio.genlayer.com/tx/0xa9d425b7c91050d92b2383282e81ba1e6d6233323f4ebfc6f6bcd704d75c7fee) |
| F2 | Failure: outsider capture | `capture_sources` | `CREATOR_ONLY` | [`0x337ae4…c2411`](https://explorer-studio.genlayer.com/tx/0x337ae4a742c507ea9cb9142608328f6763edfea7fabb569036a4081ddf3c2411) |
| F3 | Failure: assess before capture | `assess_quote` | `ASSESSMENT_NOT_ALLOWED` | [`0x46c19e…dcf4f`](https://explorer-studio.genlayer.com/tx/0x46c19e5f0d5333b6109b2b524121f397afcce2a531cd69fee022ff5fbffdcf4f) |
| H2 | Happy: exact fetch, digest and schema capture | `capture_sources` | `SOURCES_CAPTURED` | [`0x01c779…fea37`](https://explorer-studio.genlayer.com/tx/0x01c77921eff58590b9719fa703acffdeda209b6a8d5c073c7c966b07288fea37) |
| H3 | Happy: in-scope quote assessment | `assess_quote` | `QUOTE_ACCEPTABLE` | [`0x598e0f…c510f`](https://explorer-studio.genlayer.com/tx/0x598e0f97dae729004253561980e454666c2514a1220cbd5a5d4b4a32fc9c510f) |
| F4 | Failure: assessment replay | `assess_quote` | `ASSESSMENT_NOT_ALLOWED` | [`0x293bd0…d4bb8`](https://explorer-studio.genlayer.com/tx/0x293bd0e2d2f6d2e3b866c6b9066015ae60b178f9b45bb672ade6c7c9219d4bb8) |
| H4 | Happy: terminal close | `close_review` | `REVIEW_CLOSED` | [`0x9d7840…ad123`](https://explorer-studio.genlayer.com/tx/0x9d78409cdb19139a2c2f888fb71aa0f9b9ae2178f0965eef097d940323fad123) |
| A1 | Adversarial: register violation fixture | `create_review` | review `1` | [`0xd38cf0…fab2a`](https://explorer-studio.genlayer.com/tx/0xd38cf03c9c1a48044f79cec83f7d1ff798056f8bd6f200a313442ddf3b3fab2a) |
| A2 | Adversarial: authenticate violation fixture | `capture_sources` | `SOURCES_CAPTURED` | [`0xa1821d…63bde`](https://explorer-studio.genlayer.com/tx/0xa1821ddf8f7a8555f80588120673373636bd1361927c08236eeeac751f163bde) |
| A3 | Adversarial: detect out-of-scope work | `assess_quote` | `SCOPE_VIOLATION` | [`0xd87b0a…60a32`](https://explorer-studio.genlayer.com/tx/0xd87b0aaef92447c753a8a5d9b0957011c6a700bb8aad9341025f6f436b560a32) |
| A4 | Adversarial: register ambiguous fixture | `create_review` | review `2` | [`0x7bc5d6…9dab0`](https://explorer-studio.genlayer.com/tx/0x7bc5d60a4602f37a17ffdfd4333244f9dbf074a18796def31368661338f9dab0) |
| A5 | Adversarial: authenticate ambiguous fixture | `capture_sources` | `SOURCES_CAPTURED` | [`0x566525…63736`](https://explorer-studio.genlayer.com/tx/0x566525ec7312818de0690b6ec474effa4437009e3cbe55d7e1cf54db6e463736) |
| A6 | Adversarial: refuse unsupported certainty | `assess_quote` | `REVIEW_REQUIRED` | [`0x47dffc…139bd`](https://explorer-studio.genlayer.com/tx/0x47dffc1f7582a938435feedf01a117e0667a805fc7342ab6cfcab7d77fc139bd) |
| F5 | Failure: register false approved-scope digest | `create_review` | review `3` | [`0x8129ef…7e2e9`](https://explorer-studio.genlayer.com/tx/0x8129efe13aff74be0053402dda946ff62972048b4dffbd934ecfb09d6a47e2e9) |
| F6 | Failure: reject false digest without snapshot mutation | `capture_sources` | `APPROVED_SCOPE_HASH_MISMATCH` | [`0x8aecb7…10143`](https://explorer-studio.genlayer.com/tx/0x8aecb77c922a84527ee762f1161ac4a02e6849ece5a21fe38d0aab8c3a510143) |

## Final authoritative state

- Review `0`: `CLOSED`, `QUOTE_ACCEPTABLE`.
- Review `1`: `ASSESSED`, `SCOPE_VIOLATION`.
- Review `2`: `ASSESSED`, `REVIEW_REQUIRED`.
- Review `3`: remains `DRAFT`, `UNASSESSED` after the rejected digest capture.
