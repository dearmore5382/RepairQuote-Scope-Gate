# Frozen Studionet Live Matrix

Run only after exact deployed-source SHA-256 parity is established.

| Case | Actor flow | Expected authoritative result |
|---|---|---|
| H1 tenant misuse | owner create -> tenant accept -> owner seal -> tenant report -> owner respond -> tenant seal -> assess | `TENANT_RESPONSIBLE` |
| H2 system failure | same lifecycle; concealed supply line failure aligned to owner duty | `OWNER_RESPONSIBLE` |
| H3 normal wear | same lifecycle; ordinary finish degradation | `NORMAL_WEAR` |
| H4 accidental/shared | same lifecycle; accidental event and shared duty | `SHARED_RESPONSIBILITY` |
| F1 conflicting accounts | materially incompatible report and response | `INSUFFICIENT_EVIDENCE` |
| F2 wrong caller | outsider accepts/responds/seals | exact authority rejection, no mutation |
| F3 duplicate pending | open second report before terminal first | `PENDING_REPORT_EXISTS` |
| F4 premature assess | assess before response/seal | `REPORT_NOT_ASSESSABLE` |
| A1 prompt injection | instruction-like text inside report | no invented keys/verdict; fail closed or bounded outcome |
| A2 replay | assess finalized report again | `REPORT_NOT_ASSESSABLE`; prior readback unchanged |
| A3 unavailable/retry | transient model/consensus failure if observed | sealed state unchanged; later same-revision retry allowed |
| L1 closure | owner closes with no pending report | `PROPERTY_CLOSED`; new reports rejected |

For every write record transaction hash, sender, arguments, `FINALIZED`, leader execution result, consensus result, returned value, and latest-final contract readback. Do not reinterpret an unexpected valid result as a pass; stop and compare it against `SPEC.md`.
