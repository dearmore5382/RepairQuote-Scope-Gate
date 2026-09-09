# Frozen Studionet matrix

The exact transaction plan will be populated with commit-pinned raw fixture URLs after the repository has a public commit. No live claim is made before a matching-source deployment exists.

| Group | Scenario | Expected |
|---|---|---|
| Happy | create, capture happy package, assess, close | `QUOTE_ACCEPTABLE`, then `REVIEW_CLOSED` |
| Failure | invalid create fields | explicit validation result, zero records |
| Failure | outsider captures | `CREATOR_ONLY`, state unchanged |
| Failure | wrong digest | digest mismatch, state remains `DRAFT` |
| Failure | assessment before capture | `ASSESSMENT_NOT_ALLOWED` |
| Failure | assessment replay | `ASSESSMENT_NOT_ALLOWED`, frozen record unchanged |
| Adversarial | authenticated out-of-scope quote | `SCOPE_VIOLATION` |
| Adversarial | authenticated ambiguous quote | `REVIEW_REQUIRED` |
