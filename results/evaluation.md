# Evaluation

<!--
TODO: write the Rubric first, score the five saved outputs, run the prompt
injection test, cross-reference failures with traces, and write one improvement proposal.
-->

## Rubric

| Input | Expected finding | Expected severity | Expected reference |
| --- |------------------|-------------------|--------------------|
| PR-01 — clean PR | No blocking issue; sound MVVM/DI. At most a minor `try?` silent-error-swallow note | LOW / none | n/a |
| PR-02 — Swift naming violations | `FetchProfile` PascalCase + ViewModel calls URLSession directly (no DI/repository) | HIGH (arch), MEDIUM (style) | Repository/DI convention |
| PR-03 — hardcoded API key | Hardcoded live `sk-live-…` key in PaymentService | HIGH | n/a |
| PR-04 — bypasses repository layer | ViewModel calls `ApiClient` directly instead of a repository | HIGH | ADR-003 (Repository Pattern) |
| PR-05 — mixed issues | Hardcoded client secret + repository bypass + `GlobalScope` + PascalCase naming | HIGH (security & arch), MEDIUM/LOW (style) | ADR-003 (Repository Pattern) |

## Scores

| Input | Correct findings? | Hallucinated rule? | Severity correct? | ADR cited (if applicable)? |
| --- | --- | --- | --- | - |
| PR-01 | ✓ | ✗ | ✓ | ✓ |
| PR-02 | ✓ | ✗ | ✓ | ✓ |
| PR-03 | ✓ | ✗ | ✓ | ✓ |
| PR-04 | ✓ | ✗ | ✓ | ✓ |
| PR-05 | ✓ | ✗ | ✓ | ✗ |

## Improvement proposal

The reviewers reliably catch the real issues at correct severities with no hallucinated rules — the weak spot is **inconsistent ADR/reference citation**. PR-04 correctly grounded the repository-bypass finding in **ADR-003**, but PR-05 flagged the identical repository-bypass pattern (`CheckoutViewModel` depending on `ApiClient`) without citing ADR-003. The architecture reviewer should be required to attach the governing ADR/convention ID to every architecture finding whenever one exists, so the same violation is cited the same way across PRs. Enforce this in the architecture-reviewer skill (and the architecture-guidelines skill it loads) with an explicit output requirement: "cite the ADR number for each finding, or state 'no governing ADR' if none applies."
