# Frozen Studionet matrix

The matrix uses raw fixture URLs pinned to Git commit `b379644f492cd730e9f7655052b3138250dc65b8`. It completed 16/16 steps on the matching-source deployment.

| Group | Scenario | Expected |
|---|---|---|
| Happy | create, capture happy package, assess, close | `QUOTE_ACCEPTABLE`, then `REVIEW_CLOSED` |
| Failure | invalid create fields | explicit validation result, zero records |
| Happy | outsider captures locked public sources | `SOURCES_CAPTURED` |
| Failure | outsider closes assessed record | `CREATOR_ONLY`, state unchanged |
| Failure | wrong digest | digest mismatch, state remains `DRAFT` |
| Failure | assessment before capture | `ASSESSMENT_NOT_ALLOWED` |
| Failure | assessment replay | `ASSESSMENT_NOT_ALLOWED`, frozen record unchanged |
| Adversarial | authenticated out-of-scope quote | `SCOPE_VIOLATION` |
| Adversarial | authenticated ambiguous quote | `REVIEW_REQUIRED` |
