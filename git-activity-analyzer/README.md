# Git Activity Analyzer MCP

An MCP server that lets a coding agent query repository information —
**history, hotspots, CI, and ownership** — through structured tools and a
repo-overview resource.

## Design decisions

| Decision | Choice |
|---|---|
| **Scope** | All four domains: History, Hotspots, CI, Ownership |
| **Data source** | Local git (history / hotspots / ownership) + GitHub API (CI, CODEOWNERS/reviewers) |
| **Shape** | Tools for every question, plus one `repo://overview` resource for ambient context |

## What the server can answer (question catalog)

### 📜 History — *local git*
| ID | Question | Tool |
|----|----------|------|
| H1 | What changed recently? | `recent_commits` |
| H2 | What's the full history of this file? | `file_history` |
| H3 | Who/what last touched these specific lines? | `line_history` |
| H4 | Which commit introduced this message/diff string? | `search_commits` |
| H5 | How does this branch differ from base? | `branch_diff` |
| H6 | Show me one commit in detail | `commit_detail` |

### 🔥 Hotspots — *local git, computed*
| ID | Question | Tool |
|----|----------|------|
| P1 | Which files change most often? | `churn_ranking` |
| P2 | Which files are risky (high churn × large)? | `risk_hotspots` |
| P3 | Which files change together? | `co_change` |
| P4 | Which files attract the most fixes? | `fix_density` |

### 🟢 CI — *GitHub API*
| ID | Question | Tool |
|----|----------|------|
| C1 | Latest CI status for a ref/branch/PR? | `ci_status` |
| C2 | Which jobs failed, and the failing log excerpt? | `ci_failures` |
| C3 | Which tests/jobs are flaky recently? | `flaky_jobs` |
| C4 | Pass rate / duration trend? | `ci_health` |

### 👤 Ownership — *git blame + CODEOWNERS*
| ID | Question | Tool |
|----|----------|------|
| O1 | Who's the expert on this file/dir? | `code_experts` |
| O2 | Who should review this change? | `suggest_reviewers` |
| O3 | What's the bus-factor risk here? | `bus_factor` |

### 📄 Resource
- `repo://overview` — default branch, remote, contributor count, CODEOWNERS
  summary. Ambient context the agent reads without a tool call.

## Build plan (two waves)

1. **Local-git wave** — History + Hotspots + Ownership. Zero auth, fully
   offline, runnable and testable immediately.
2. **CI wave** — the four CI tools. Needs a GitHub token and outbound HTTPS to
   the GitHub API (deferred until network access is available).

## Implementation

| File | Role | Runs without `mcp` SDK? |
|------|------|--------------------------|
| `gitlib.py` | All wave-1 analysis (pure Python + `git` CLI) | ✅ yes |
| `cli.py` | Terminal dispatcher over `gitlib` — exercise every tool today | ✅ yes |
| `server.py` | MCP stdio wrapper (tools + resource + prompts) | needs `mcp` |

The analysis is decoupled from the MCP SDK on purpose: `gitlib`/`cli` run on
the stdlib + `git` alone, so wave 1 is usable even where the `mcp` package
cannot be installed. `server.py` lights up once `pip install mcp` succeeds.

### Try it now (no MCP SDK needed)

```bash
cd git-activity-analyzer
python cli.py overview --repo_path /path/to/repo
python cli.py analyze_hotspots --repo_path /path/to/repo --time_range all --top_n 10
python cli.py code_experts --repo_path /path/to/repo --path src/
python cli.py bus_factor --repo_path /path/to/repo --path src/app.py
```

### Run as an MCP server

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # installs the `mcp` SDK
python server.py                        # stdio transport
# register:  claude mcp add git-activity -- /abs/.venv/bin/python /abs/server.py
```

## Status

- [x] Question catalog locked (17 tools + 1 resource)
- [x] Design specs (data sources, primitives, URIs, schemas, prompts, access control)
- [x] **Wave-1 implementation** — 13 local-git tools + overview resource + 3 offline prompts, verified against a real repo via `cli.py`
- [x] MCP wrapper (`server.py`) written; runs once the `mcp` SDK is installable
- [ ] CI wave (4 tools) — stubbed; needs GitHub/GitLab provider layer + `GITHUB_TOKEN`
- [ ] `.mailmap`-style author identity merging (blame currently counts distinct spellings separately)
