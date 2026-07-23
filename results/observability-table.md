# Observability table

<!--
TODO: run /review-pr 1 through /review-pr 5 with LangSmith tracing on, then
fill in this table from the trace data and answer the PR-03 diagnostic.
-->

| Input | Total tokens | Most expensive span | `security-reviewer` called? |
| --- | --- | --- | --- |
| PR-01 (clean) | ~40.5K | `claude-opus-4-8` consolidation span (0.78s, ~40K tokens) | Yes |
| PR-02 (style violations) | ~46.7K | `claude-opus-4-8` consolidation span (5.17s, ~46K tokens, incl. `Edit`) | Yes |
| PR-03 (hardcoded API key) | ~53.4K | `claude-opus-4-8` consolidation span (87.80s, ~53K tokens, incl. 85.47s `Edit`) | Yes |
| PR-04 (architecture violation) | ~59.9K | `claude-opus-4-8` consolidation span (5.38s, ~60K tokens, incl. `Edit`) | Yes |
| PR-05 (mixed issues) | ~68K | `claude-opus-4-8` consolidation span (3.72s, ~67K tokens, incl. `Edit`) | Yes |

## Diagnostic (PR-03)
The PR-03 trace shows only **two** reviewer sub-agents — `security-reviewer` (7.01s, 7.8K) and
`architecture-reviewer` (12.01s, 17.3K). There is **no `style-reviewer` span**, so the style
pass never ran on PR-03 even though the hardcoded API key also carries a style finding
(`API_KEY` should be a `const val` in a companion object). `security-reviewer` did fire and
would have caught the hardcoded key, but the review is incomplete: one of the three mandated
reviewers was skipped.

The run is also dominated by the final `claude-opus-4-8` consolidation span at **87.80s**,
almost entirely the **85.47s `Edit`** to `review_history.md` — the write, not the review, is
the latency bottleneck.

### Security-reviewer questions (PR-03)

**Was the security-reviewer subagent called? (Y/N)**
Y. The `security-reviewer` Subagent span is present in the PR-03 trace (7.01s, 7.8K tokens),
with an internal `claude-haiku-4-5` completion and a `Read` tool call — it ran.

**What did the security-reviewer return? (span output)**
Not available from the pasted trace: it contains only span metadata (durations, token counts,
tool names), not the span's output text. To capture the verbatim return, open the
`security-reviewer` span in LangSmith and copy its output field. (For reference, in the
in-session review the security-reviewer reported: hardcoded live API key — HIGH; missing input
validation on `charge()` — MEDIUM; error swallowing in `charge()` — MEDIUM.)

**Failure mode**
For PR-03 the security finding was **not** missing — the hardcoded-API-key HIGH finding did
surface and the security-reviewer both ran and returned it. The reviewer absent from the trace
is `style-reviewer`, whose failure mode is **subagent not called** (no span exists for it at
all — not wrong input, not a tool that failed to fire, not an insufficient prompt).
