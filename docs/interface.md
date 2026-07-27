# Git Activity Analyzer — Agent Interface

The complete interface an agent uses to talk to the Git Activity Analyzer MCP
server: the three primitive types, every tool's signature and return shape, the
resource URI, and the prompt workflows. This is the single reference for "what
can I call and what do I get back."

- **Transport:** stdio (see `git-activity-analyzer/ACCESS_CONTROL.md`)
- **Server name:** `git-activity-analyzer`
- **Waves:** wave 1 = local git (implemented); wave 2 = CI (stubbed)
- **Universal rule:** every tool requires `repo_path` (absolute path to a git
  work-tree). `time_range` ∈ `{7d, 30d, 90d, all}`. `branch` defaults to `main`.
- **Errors:** tools return `{"error": "<message>"}` (JSON), never throw.

---

## 1. Resource

| URI | Purpose |
|-----|---------|
| `git-activity://summary/{repo_path}` | Ambient repo overview the agent reads for context |

**Returns:**
```json
{
  "branch": "main",
  "remote": "https://github.com/owner/repo.git",
  "head": "2e31b4e",
  "total_commits": 27,
  "contributors": 2,
  "branches": ["main", "feature/x"],
  "codeowners_rules": 0
}
```

---

## 2. Tools

### History

#### `recent_commits(repo_path, branch="main", time_range="7d", author=None, top_n=20)`
Recent commits, newest first.
```json
[{ "sha": "...", "short_sha": "2e31b4e", "author": "...", "email": "...",
   "date": "2026-07-23T10:04:30+03:00", "subject": "..." }]
```

#### `file_history(repo_path, path, branch="main", top_n=30)`
Commit history of one file (follows renames). Same commit-record shape as above.
*Requires:* `path`.

#### `line_history(repo_path, path, start_line, end_line=None)`
Commits that changed a line range (blame over lines). Commit-record array.
*Requires:* `path`, `start_line`.

#### `search_commits(repo_path, query, mode="message", top_n=20)`
Find commits by message (`mode="message"`) or diff content (`mode="diff"`).
Commit-record array. *Requires:* `query`.

#### `branch_diff(repo_path, base="main", head="HEAD")`
Compare two refs.
```json
{ "base": "main", "head": "HEAD", "ahead": 0, "behind": 0,
  "changed_files": ["..."], "changed_count": 0 }
```

#### `commit_detail(repo_path, sha)`
Full detail for one commit. *Requires:* `sha`.
```json
{ "sha": "...", "short_sha": "...", "author": "...", "email": "...",
  "date": "...", "subject": "...", "body": "...",
  "files": [{ "path": "...", "insertions": 34, "deletions": 6 }],
  "insertions": 39, "deletions": 6, "files_changed": 2 }
```

### Hotspots

#### `analyze_hotspots(repo_path, branch="main", time_range="30d", filter_authors=None, top_n=10)`
Files by change frequency (churn).
```json
[{ "path": "CLAUDE.md", "commits": 8, "insertions": 54, "deletions": 37 }]
```

#### `risk_hotspots(repo_path, branch="main", time_range="90d", top_n=20)`
Files by risk = churn × current size.
```json
[{ "path": "...", "commits": 8, "loc": 120, "risk": 960 }]
```

#### `co_change(repo_path, path, time_range="90d", top_n=10)`
Files that change together with `path`. *Requires:* `path`.
```json
[{ "path": "...", "co_changes": 2 }]
```

#### `fix_density(repo_path, branch="main", time_range="90d", top_n=20, fix_pattern=<regex>)`
Files by number of bug-fix commits.
```json
[{ "path": "...", "fix_commits": 3 }]
```

### Ownership

#### `code_experts(repo_path, path, top_n=5)`
People who know a file/dir, by blame share. *Requires:* `path`.
```json
[{ "author": "...", "lines": 9, "share": 0.529 }]
```

#### `suggest_reviewers(repo_path, paths, max_reviewers=3)`
Reviewers from blame experts ∪ CODEOWNERS. *Requires:* `paths` (array).
```json
{ "blame_experts": ["..."], "codeowners": ["..."], "suggested": ["..."] }
```

#### `bus_factor(repo_path, path)`
Knowledge-concentration risk. *Requires:* `path`.
```json
{ "path": "...", "contributors": 2, "bus_factor": 1,
  "top_owner_share": 0.529, "risk": "high", "top_owners": [ ... ] }
```

### CI — wave 2 (stubbed)

`ci_status`, `ci_failures`, `flaky_jobs`, `ci_health` currently return:
```json
{ "error": "CI tools require the wave-2 GitHub/GitLab provider layer and a GITHUB_TOKEN. Not yet implemented." }
```
Planned signatures:
- `ci_status(repo_path, ref="main", pr=None)`
- `ci_failures(repo_path, run_id=None, ref="main", log_lines=40)`
- `flaky_jobs(repo_path, workflow=None, window=30)`
- `ci_health(repo_path, workflow=None, window=50)`

---

## 3. Prompts (workflows)

Named plans that chain tools; the agent invokes one and follows the steps,
ending in a synthesis. Full plans in
`git-activity-analyzer/PROMPT_WORKFLOWS.md`.

| Prompt | Args | Chains | Offline? |
|--------|------|--------|----------|
| `onboard_to_area` | `repo_path, path` | summary → file_history → code_experts → co_change → bus_factor | ✅ |
| `hotspot_health_check` | `repo_path, time_range="90d", top_n=20` | risk_hotspots + fix_density → bus_factor | ✅ |
| `pr_risk_report` | `repo_path, head, base="main"` | branch_diff → risk_hotspots/fix_density/co_change → suggest_reviewers → ci_status | CI degrades |

---

## 4. Quick reference — required params

| Tool | Required (beyond `repo_path`) |
|------|-------------------------------|
| recent_commits, branch_diff, analyze_hotspots, risk_hotspots, fix_density | — |
| file_history, line_history, co_change, code_experts, bus_factor | `path` (line_history also `start_line`) |
| search_commits | `query` |
| commit_detail | `sha` |
| suggest_reviewers | `paths` |
| ci_* (wave 2) | — |

## 5. Calling conventions

- **Paths** are repo-relative (e.g. `Sources/App.swift`), a directory, or a
  file. Ownership tools accept a directory and aggregate across its files.
- **Refs** (`branch`, `base`, `head`, `ref`, `sha`) are any valid git revision.
- **Output** is always a JSON string — an array of flat records or a single
  object. Timestamps are ISO-8601. No prose.
- **Read-only:** no tool mutates the repo or remote.
- **Without the MCP SDK:** the same functions are callable via
  `git-activity-analyzer/cli.py`; `gitlib.py` is the shared core.
