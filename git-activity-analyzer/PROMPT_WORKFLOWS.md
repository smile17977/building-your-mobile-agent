# Git Activity Analyzer — Step 6: Prompt Workflows

Prompts orchestrate multiple tools into a **plan** for a common operation. Each
prompt is a named, argument-driven template that tells the agent *which tools to
call, in what order, and how to combine the results* — it holds the recipe, not
new data.

## What makes a good prompt (rules applied here)

1. **One clear intent per prompt** — a recurring question a human actually asks.
2. **Typed arguments with defaults** — same discipline as tool schemas; most
   prompts run with zero required args beyond `repo_path`.
3. **Explicit tool chain** — the plan names each step and how its output feeds
   the next.
4. **Graceful degradation** — if a step needs the network (CI, wave 2) and it's
   unavailable, the prompt says so and continues with the offline steps.
5. **Ends in a synthesis** — the final step tells the agent how to combine
   everything into a human answer, not just dump tool output.

---

## Flagship — `repo_health_review`

The example: build failures → responsible commits → cross-reference hotspots →
flag areas needing attention.

```json
{
  "name": "repo_health_review",
  "description": "Produce a health review of a repository: what's failing in CI, which commits are responsible, how those areas overlap with risky hotspots, and where to focus attention.",
  "arguments": [
    { "name": "repo_path",  "description": "Absolute path to the local Git repository", "required": true },
    { "name": "branch",     "description": "Branch to review", "required": false },
    { "name": "time_range", "description": "History window: 7d | 30d | 90d | all", "required": false }
  ]
}
```

**Orchestration plan the prompt template instructs:**

```
1. CONTEXT      read  repo://summary/{repo}                → default branch, HEAD, size
2. CI STATE     call  ci_status(repo_path, ref=branch)     → is it red? which checks?
                call  ci_failures(repo_path, ref=branch)   → failing jobs + log excerpts
   ⤷ (wave-1 fallback: if CI unavailable, note it and skip to step 4)
3. BLAME CAUSE  for each failing area/file in the logs:
                call  search_commits(repo_path, query=<symbol/error>, mode="diff")
                call  commit_detail(repo_path, sha=<top hit>)   → likely responsible change
4. HOTSPOTS     call  risk_hotspots(repo_path, branch, time_range)
                call  fix_density(repo_path, branch, time_range)
                → intersect with the files implicated in steps 2–3
5. OWNERSHIP    for each flagged file:
                call  code_experts(repo_path, path)         → who to loop in
6. SYNTHESIZE   Produce a ranked "areas needing attention" list:
                file · why flagged (red CI / high risk / fix-prone) · likely
                cause commit · suggested owner. Lead with the most urgent.
```

**Output shape (guidance to the agent):** a short prose summary + a table of
flagged areas. Never just raw tool JSON.

---

## `pr_risk_report`

```json
{
  "name": "pr_risk_report",
  "description": "Assess the risk of a pull request or branch: what it changes, whether those files are risky or fix-prone, who should review, and whether CI is green.",
  "arguments": [
    { "name": "repo_path", "description": "Absolute path to the local Git repository", "required": true },
    { "name": "head",      "description": "The PR/branch head ref", "required": true },
    { "name": "base",      "description": "Base ref to compare against (default main)", "required": false }
  ]
}
```

**Plan:**
```
1. call branch_diff(repo_path, base, head)        → changed files + ahead/behind
2. for the changed files:
     call risk_hotspots(...) and fix_density(...)  → which touched files are risky
     call co_change(path) on the riskiest          → what else usually changes with them (missing edits?)
3. call suggest_reviewers(repo_path, paths=<changed files>)
4. call ci_status(repo_path, ref=head)            → wave-1 fallback: note "CI check unavailable offline"
5. SYNTHESIZE: risk verdict (low/med/high) + rationale + reviewers + CI state + "consider also touching X" hints
```

---

## `onboard_to_area`

```json
{
  "name": "onboard_to_area",
  "description": "Help someone new understand a directory or subsystem: what it is, how it evolved, who owns it, and what it is coupled to.",
  "arguments": [
    { "name": "repo_path", "description": "Absolute path to the local Git repository", "required": true },
    { "name": "path",      "description": "Directory or file to onboard into", "required": true }
  ]
}
```

**Plan (fully offline — wave 1):**
```
1. read repo://summary/{repo}                     → the big picture
2. call file_history(repo_path, path)             → how this area evolved, recent churn
3. call code_experts(repo_path, path)             → who to ask
4. call co_change(repo_path, path)                → sibling files you'll likely touch too
5. call bus_factor(repo_path, path)               → is knowledge concentrated / risky?
6. SYNTHESIZE: a short orientation brief — purpose, key commits, go-to people, coupled files, risks
```

---

## `investigate_regression`

```json
{
  "name": "investigate_regression",
  "description": "Track down the likely cause of a regression or new bug: find the change that introduced a symptom, inspect it, and check whether CI caught it.",
  "arguments": [
    { "name": "repo_path", "description": "Absolute path to the local Git repository", "required": true },
    { "name": "symptom",   "description": "A string, error message, or symbol associated with the regression", "required": true },
    { "name": "path",      "description": "Optional file to focus the line-level search", "required": false },
    { "name": "time_range","description": "How far back to search: 7d | 30d | 90d | all", "required": false }
  ]
}
```

**Plan:**
```
1. call search_commits(repo_path, query=symptom, mode="diff")   → candidate commits
2. if path given: call line_history(repo_path, path, ...)       → narrow to the responsible lines
3. call commit_detail(repo_path, sha=<top candidate>)           → inspect the suspect change
4. call ci_failures(repo_path, ref=<suspect sha or branch>)     → did CI flag it? (wave-1 fallback: note unavailable)
5. SYNTHESIZE: "most likely introduced by <sha> (<author>, <date>) — here's the diff and whether CI caught it"
```

---

## `hotspot_health_check`

```json
{
  "name": "hotspot_health_check",
  "description": "Scan the codebase for decay signals: files that are high-churn, fix-prone, and have concentrated ownership — the maintenance risks worth addressing.",
  "arguments": [
    { "name": "repo_path",  "description": "Absolute path to the local Git repository", "required": true },
    { "name": "time_range", "description": "History window: 7d | 30d | 90d | all", "required": false },
    { "name": "top_n",      "description": "How many risk files to examine", "required": false }
  ]
}
```

**Plan (fully offline — wave 1):**
```
1. call risk_hotspots(repo_path, time_range, top_n)   → churn × size ranking
2. call fix_density(repo_path, time_range, top_n)     → defect-prone files
3. for the union of the two lists:
     call bus_factor(repo_path, path)                 → single-point-of-failure risk
4. SYNTHESIZE: a prioritized maintenance list — file · risk signals present
   (churn/fixes/bus-factor) · recommended action (refactor / add tests / spread ownership)
```

---

## Prompt → tool/resource matrix

| Prompt | Tools chained | Resources | Network? | Wave |
|--------|---------------|-----------|----------|------|
| `repo_health_review` | ci_status, ci_failures, search_commits, commit_detail, risk_hotspots, fix_density, code_experts | summary | CI steps | 2 (degrades to 1) |
| `pr_risk_report` | branch_diff, risk_hotspots, fix_density, co_change, suggest_reviewers, ci_status | — | ci_status only | 2 (degrades to 1) |
| `onboard_to_area` | file_history, code_experts, co_change, bus_factor | summary | no | 1 |
| `investigate_regression` | search_commits, line_history, commit_detail, ci_failures | — | ci_failures only | 2 (degrades to 1) |
| `hotspot_health_check` | risk_hotspots, fix_density, bus_factor | — | no | 1 |

## Design notes

- **Prompts don't add data or auth** — they only sequence existing tools and
  resources, so they inherit each tool's wave/blocker status.
- **Two prompts are fully offline** (`onboard_to_area`, `hotspot_health_check`)
  — shippable in wave 1 with the local-git tools.
- **The other three reach full fidelity in wave 2** but each has an explicit
  wave-1 fallback: run the git-backed steps, and clearly label the CI step as
  "unavailable offline" rather than failing the whole workflow.
- **Every prompt ends in a synthesis step** — the value is the combined
  judgement, not the raw tool outputs.
