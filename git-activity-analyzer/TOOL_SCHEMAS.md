# Git Activity Analyzer — Step 5: Tool Schemas

JSON Schema for each tool. Schema-authoring rules applied throughout:

1. **Minimal `required`.** Only fields the tool cannot work without.
2. **Sensible defaults for everything else.**
3. **Descriptions are for the model** — each says *when to use the tool* and
   what each param means, in plain language; that is how the model decides to
   invoke it.
4. **Typed & constrained** — `enum` for closed sets, `integer` for counts, arrays
   for lists.
5. **Read-only** — no tool mutates the repo.

## Conventions (from the reference example)

- `repo_path` (string) — **required** on every local-git tool. Absolute path to
  the local Git repository. No default: the server must be told which repo.
- `branch` (string) — optional, **default `"main"`**.
- `time_range` (string) — optional **enum `["7d","30d","90d","all"]`**, default
  `"30d"`. (CI history tools use a run-count `window` instead — noted inline.)
- Optional arrays (e.g. `filter_authors`) omit a `default` and simply mean
  "include everything" when absent.
- `top_n` (integer) — optional cap with a per-tool default.

---

## Reference pattern — `analyze_hotspots`

```json
{
  "name": "analyze_hotspots",
  "description": "Identify files with the highest change frequency in a repository. Use when the user asks about code churn, refactoring candidates, or which files are most actively modified.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": {
        "type": "string",
        "description": "Absolute path to the local Git repository"
      },
      "branch": {
        "type": "string",
        "description": "Branch to analyze",
        "default": "main"
      },
      "time_range": {
        "type": "string",
        "enum": ["7d", "30d", "90d", "all"],
        "description": "How far back to look in the commit history",
        "default": "30d"
      },
      "filter_authors": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Optional list of author emails to include"
      },
      "top_n": {
        "type": "integer",
        "description": "Number of files to return, ranked by change frequency",
        "default": 10
      }
    },
    "required": ["repo_path"]
  }
}
```

---

## History tools

### `recent_commits`
```json
{
  "name": "recent_commits",
  "description": "List recent commits, newest first. Use when the user asks what changed lately, or wants recent activity by a specific author.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path":  { "type": "string", "description": "Absolute path to the local Git repository" },
      "branch":     { "type": "string", "description": "Branch to read commits from", "default": "main" },
      "time_range": { "type": "string", "enum": ["7d", "30d", "90d", "all"], "description": "How far back to look in the commit history", "default": "7d" },
      "author":     { "type": "string", "description": "Optional single author name or email to filter by" },
      "top_n":      { "type": "integer", "description": "Maximum number of commits to return", "default": 20 }
    },
    "required": ["repo_path"]
  }
}
```

### `file_history`
```json
{
  "name": "file_history",
  "description": "Show the commit history of a single file, following renames. Use when the user asks how or why a specific file evolved.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "path":      { "type": "string", "description": "Repository-relative path to the file" },
      "branch":    { "type": "string", "description": "Branch to read history from", "default": "main" },
      "top_n":     { "type": "integer", "description": "Maximum number of commits to return", "default": 30 }
    },
    "required": ["repo_path", "path"]
  }
}
```

### `line_history`
```json
{
  "name": "line_history",
  "description": "Show which commits last changed a specific range of lines in a file (blame over a line range). Use to find who or what is responsible for a particular piece of code.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path":  { "type": "string", "description": "Absolute path to the local Git repository" },
      "path":       { "type": "string", "description": "Repository-relative path to the file" },
      "start_line": { "type": "integer", "description": "First line of the range (1-based)" },
      "end_line":   { "type": "integer", "description": "Last line of the range (1-based); defaults to start_line if omitted" }
    },
    "required": ["repo_path", "path", "start_line"]
  }
}
```

### `search_commits`
```json
{
  "name": "search_commits",
  "description": "Find commits by searching commit messages or the actual diff content. Use to locate when a string, behavior, or feature was introduced.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "query":     { "type": "string", "description": "Text to search for" },
      "mode":      { "type": "string", "enum": ["message", "diff"], "description": "Search commit messages, or the added/removed diff content", "default": "message" },
      "top_n":     { "type": "integer", "description": "Maximum number of commits to return", "default": 20 }
    },
    "required": ["repo_path", "query"]
  }
}
```

### `branch_diff`
```json
{
  "name": "branch_diff",
  "description": "Compare two branches or refs: how many commits each is ahead/behind and which files differ. Use to understand what a branch or PR changes relative to a base.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "base":      { "type": "string", "description": "Base ref to compare against", "default": "main" },
      "head":      { "type": "string", "description": "Head ref being compared", "default": "HEAD" }
    },
    "required": ["repo_path"]
  }
}
```

### `commit_detail`
```json
{
  "name": "commit_detail",
  "description": "Return full detail for one commit: author, date, full message, changed files and per-file line stats. Use after finding a commit of interest.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "sha":       { "type": "string", "description": "Full or abbreviated commit SHA" }
    },
    "required": ["repo_path", "sha"]
  }
}
```

---

## Hotspots tools

### `analyze_hotspots` / `churn_ranking`
The reference example above **is** the churn-ranking tool. (`risk_hotspots`
below adds a size dimension.)

### `risk_hotspots`
```json
{
  "name": "risk_hotspots",
  "description": "Rank files by change-risk: how often they change combined with how large they are. Use to find the parts of a codebase most likely to harbor bugs or need refactoring.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path":  { "type": "string", "description": "Absolute path to the local Git repository" },
      "branch":     { "type": "string", "description": "Branch to analyze", "default": "main" },
      "time_range": { "type": "string", "enum": ["7d", "30d", "90d", "all"], "description": "How far back to look in the commit history", "default": "90d" },
      "top_n":      { "type": "integer", "description": "Number of hotspot files to return", "default": 20 }
    },
    "required": ["repo_path"]
  }
}
```

### `co_change`
```json
{
  "name": "co_change",
  "description": "Given a file, find the files that most often change together with it in the same commits (temporal coupling). Use to discover hidden dependencies and what else may need updating.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path":  { "type": "string", "description": "Absolute path to the local Git repository" },
      "path":       { "type": "string", "description": "Repository-relative path to the anchor file" },
      "time_range": { "type": "string", "enum": ["7d", "30d", "90d", "all"], "description": "How far back to look in the commit history", "default": "90d" },
      "top_n":      { "type": "integer", "description": "Number of coupled files to return", "default": 10 }
    },
    "required": ["repo_path", "path"]
  }
}
```

### `fix_density`
```json
{
  "name": "fix_density",
  "description": "Rank files by how many bug-fix commits touch them (commits whose message matches a fix/bug pattern). Use to find fragile, defect-prone areas.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path":   { "type": "string", "description": "Absolute path to the local Git repository" },
      "branch":      { "type": "string", "description": "Branch to analyze", "default": "main" },
      "time_range":  { "type": "string", "enum": ["7d", "30d", "90d", "all"], "description": "How far back to look in the commit history", "default": "90d" },
      "top_n":       { "type": "integer", "description": "Number of files to return", "default": 20 },
      "fix_pattern": { "type": "string", "description": "Regex matched against commit messages to identify fixes", "default": "(?i)\\b(fix|bug|hotfix|patch|regression)\\b" }
    },
    "required": ["repo_path"]
  }
}
```

---

## CI tools (network — wave 2)

CI history uses a run-count `window` rather than `time_range`, since runs are
naturally counted, not dated.

### `ci_status`
```json
{
  "name": "ci_status",
  "description": "Get the latest CI status for a branch, ref, or pull request. Use to check whether a change is passing before relying on it.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository (used to resolve the owner/repo remote)" },
      "ref":       { "type": "string", "description": "Branch name, commit SHA, or tag", "default": "main" },
      "pr":        { "type": "integer", "description": "Pull request number (alternative to ref)" }
    },
    "required": ["repo_path"]
  }
}
```

### `ci_failures`
```json
{
  "name": "ci_failures",
  "description": "List the failing jobs for a CI run and return a short excerpt of each failing log. Use to diagnose why CI is red.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "run_id":    { "type": "string", "description": "Specific CI run id; if omitted, uses the latest run for 'ref'" },
      "ref":       { "type": "string", "description": "Branch/SHA to use when run_id is not given", "default": "main" },
      "log_lines": { "type": "integer", "description": "Trailing log lines to include per failing job", "default": 40 }
    },
    "required": ["repo_path"]
  }
}
```

### `flaky_jobs`
```json
{
  "name": "flaky_jobs",
  "description": "Identify jobs or tests that flip between pass and fail across recent runs of a workflow (likely flaky). Use to decide whether a failure is real or noise.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "workflow":  { "type": "string", "description": "Workflow name or file (e.g. 'ci.yml'); omit to consider all workflows" },
      "window":    { "type": "integer", "description": "How many recent runs to examine", "default": 30 }
    },
    "required": ["repo_path"]
  }
}
```

### `ci_health`
```json
{
  "name": "ci_health",
  "description": "Summarize a workflow's health over recent runs: pass rate and mean duration, with a simple trend. Use to gauge pipeline reliability.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "workflow":  { "type": "string", "description": "Workflow name or file; omit for all workflows" },
      "window":    { "type": "integer", "description": "How many recent runs to summarize", "default": 50 }
    },
    "required": ["repo_path"]
  }
}
```

---

## Ownership tools

### `code_experts`
```json
{
  "name": "code_experts",
  "description": "Identify the people most knowledgeable about a file or directory, ranked by blame share and recency of contribution. Use to find who to ask about an area.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "path":      { "type": "string", "description": "Repository-relative file or directory path" },
      "top_n":     { "type": "integer", "description": "Maximum number of experts to return", "default": 5 }
    },
    "required": ["repo_path", "path"]
  }
}
```

### `suggest_reviewers`
```json
{
  "name": "suggest_reviewers",
  "description": "Suggest reviewers for a change by combining code experts (from blame) with CODEOWNERS rules for the given paths. Use when opening or triaging a PR.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path":     { "type": "string", "description": "Absolute path to the local Git repository" },
      "paths":         { "type": "array", "items": { "type": "string" }, "description": "Repository-relative paths the change touches" },
      "max_reviewers": { "type": "integer", "description": "Maximum number of reviewers to suggest", "default": 3 }
    },
    "required": ["repo_path", "paths"]
  }
}
```

### `bus_factor`
```json
{
  "name": "bus_factor",
  "description": "Estimate the bus-factor risk for a file or directory: how concentrated its knowledge is among a few contributors. Use to spot single points of failure in ownership.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo_path": { "type": "string", "description": "Absolute path to the local Git repository" },
      "path":      { "type": "string", "description": "Repository-relative file or directory path" }
    },
    "required": ["repo_path", "path"]
  }
}
```

---

## `required` at a glance

Every tool requires `repo_path`. Additional required fields are only those that
*identify the thing being asked about* — there is no sensible default for
"which file / which commit / what query".

| Tool | required (beyond repo_path) |
|------|------------------------------|
| recent_commits | — |
| file_history | path |
| line_history | path, start_line |
| search_commits | query |
| branch_diff | — |
| commit_detail | sha |
| analyze_hotspots / churn_ranking | — |
| risk_hotspots | — |
| co_change | path |
| fix_density | — |
| ci_status | — |
| ci_failures | — |
| flaky_jobs | — |
| ci_health | — |
| code_experts | path |
| suggest_reviewers | paths |
| bus_factor | path |
