# RepairScope

RepairScope is a non-payable GenLayer dApp for one narrow question: how does a newly reported rental repair condition relate to a jointly sealed move-in baseline and repair-duty policy?

The owner and tenant jointly establish the baseline. A later report contains one statement from each party. Validators independently produce bounded semantic observations, while deterministic contract code derives `OWNER_RESPONSIBLE`, `TENANT_RESPONSIBLE`, `SHARED_RESPONSIBILITY`, `NORMAL_WEAR`, or `INSUFFICIENT_EVIDENCE`.

RepairScope does not authenticate photographs, inspect a building, calculate costs, transfer funds, or decide legal liability.

## Repository

- `contracts/RepairScope.py` — reviewed intelligent contract
- `SPEC.md` — proof obligation, lifecycle, consensus boundary, and precedence
- `tests/` — semantic, static, direct-mode, and frontend protocol tests
- `verification/AUDIT.md` — honest pre-deployment adversarial audit
- `verification/LIVE_MATRIX.md` — frozen post-deployment test plan
- `app/` — English-only dApp frontend using the supplied RepairScope logo

## Local verification

```text
python -m pytest -q
npm test
npm run lint
npm run build
```

The frontend remains in preview mode until a matching-source Studionet deployment passes the live matrix.
