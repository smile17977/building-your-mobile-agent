# Git Activity Analyzer — Step 3: Map to MCP Primitives

Mapping each capability onto the right MCP primitive.

| Data type | Primitive | Why |
|-----------|-----------|-----|
| Static data (repo summary, team structure) | **Resource** — read-only, stable URI | Ambient context the agent reads without a call; cacheable; changes rarely |
| Parameterized operations (analyze hotspots, commit patterns) | **Tool** — functions with typed inputs/outputs | Agent-driven queries with args (path, ref, window); the bulk of the server |
| Common multi-step workflows | **Prompt** — reusable templates that chain tools | Encodes a recipe (e.g. "PR risk report") the agent can invoke in one shot |

---

## 1. Resources — read-only, stable URIs

Static-ish, browsable context. No parameters beyond what's in the URI. The
client can list and read these without side effects.

| URI | Contents | Backed by |
|-----|----------|-----------|
| `repo://overview` | default branch, remote URL, HEAD sha, total commits, contributor count, active-branch list | local git |
| `repo://contributors` | ranked contributor list (name, email, commit count, first/last commit) | local git shortlog |
| `repo://codeowners` | parsed CODEOWNERS rules: glob → owners; note unresolved `@team` handles | local CODEOWNERS file |
| `repo://team-structure` | teams → members (org chart slice) | provider Teams API ⚠️ network |
| `repo://branches` | branches with ahead/behind vs default, last-commit date | local git |

Notes:
- Resources are **read-only and idempotent** — no computation the caller
  parameterizes. If a "read" needs args (a path, a window), it's a Tool.
- `repo://team-structure` is the only network-gated resource; the rest are
  offline. It can be omitted in wave 1 and added with the CI wave.
- URIs are stable so the agent can rely on them as fixed context anchors.

---

## 2. Tools — parameterized functions (the 17-tool catalog)

Each catalog question becomes a tool with typed params and a compact,
machine-parseable JSON return. Grouped by domain.

### History (local git)
- `recent_commits(since, limit, author?)`
- `file_history(path, limit)`
- `line_history(path, start_line, end_line)`
- `search_commits(query, mode="message|diff", limit)`
- `branch_diff(base, head)`
- `commit_detail(sha)`

### Hotspots (local git, computed)
- `churn_ranking(since, top_n, path_glob?)`
- `risk_hotspots(since, top_n)`            # churn × size
- `co_change(path, since, top_n)`
- `fix_density(since, top_n, fix_pattern?)`

### CI (provider API ⚠️ network)
- `ci_status(ref | pr)`
- `ci_failures(run_id | ref)`              # jobs + failing log tail
- `flaky_jobs(workflow, window)`
- `ci_health(workflow, window)`

### Ownership (blame + CODEOWNERS)
- `code_experts(path)`                     # offline
- `suggest_reviewers(paths[])`             # blame ∪ CODEOWNERS; team expansion ⚠️
- `bus_factor(path)`                        # offline

Tool contract conventions:
- Inputs: explicit, typed, sensible defaults (`since="90 days ago"`,
  `top_n=20`). Paths are repo-relative.
- Outputs: JSON — arrays of flat records or a single object. Compact keys,
  stable shapes, ISO-8601 timestamps. No prose.
- Read-only: tools never mutate the repo or push anything.
- Errors: return a structured `{ "error": "...", "hint": "..." }`, not a throw.

---

## 3. Prompts — reusable multi-step workflows

Prompts are named templates the agent can invoke; each orchestrates several
tools/resources into a common analysis. They contain the *recipe*, not new data.

| Prompt | Chains | Answers |
|--------|--------|---------|
| `pr_risk_report(base, head)` | `branch_diff` → `risk_hotspots` + `fix_density` on changed files → `suggest_reviewers` → `ci_status` | "How risky is this PR, who should review, is CI green?" |
| `onboard_to_area(path)` | `repo://overview` + `file_history` + `code_experts` + `co_change` | "I'm new to this dir — what is it, who owns it, what's coupled to it?" |
| `investigate_regression(symptom, since)` | `search_commits` (diff/message) → `line_history` → `commit_detail` → `ci_failures` | "Which change likely caused this, and did CI catch it?" |
| `hotspot_health_check(since)` | `churn_ranking` + `risk_hotspots` + `bus_factor` on top files | "Where is the codebase decaying and who's the single point of failure?" |

Notes:
- Prompts are **argument templates**, not code paths — they tell the agent which
  tools to call in what order, with placeholders the user fills.
- Keep them few and high-value; each should collapse a recurring multi-call
  dance into one intent.
- A prompt referencing a network-gated tool (e.g. `ci_status`) degrades
  gracefully in wave 1 — the other steps still run.

---

## How the three primitives divide the surface

```
Resource   →  "What is this repo / who's on the team?"      (ambient, no args)
Tool       →  "Analyze X with these parameters."            (the workhorses)
Prompt     →  "Run this standard investigation for me."     (tool choreography)
```

Rule of thumb applied here:
- Needs a caller-supplied parameter or computation → **Tool**.
- Fixed, listable, read-only snapshot → **Resource**.
- A named sequence of the above → **Prompt**.

---

## Wave alignment

- **Wave 1 (offline):** all History + Hotspots + `code_experts`/`bus_factor`
  tools; resources `repo://overview|contributors|codeowners|branches`; prompts
  `onboard_to_area`, `hotspot_health_check`.
- **Wave 2 (token + network):** CI tools; `repo://team-structure`; CODEOWNERS
  team expansion in `suggest_reviewers`; prompts `pr_risk_report`,
  `investigate_regression` reach full fidelity.
