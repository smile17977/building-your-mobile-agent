# Git Activity Analyzer — Step 4: Resource URI Design

Resources need stable, predictable addresses. Scheme: **`git-activity://`**.

## URI grammar

```
git-activity://<category>/<selector>[/<sub-selector>][?<filters>]
```

- **scheme** — always `git-activity://` (identifies this server's namespace)
- **category** — the noun domain: `summary`, `team`, `ownership`,
  `contributors`, `codeowners`, `branches`, `deployments`
- **selector** — the specific entity within the category (a name, path, or
  `_all` / omitted for the collection)
- **query string** — *optional filters only* (windows, formats). Anything that
  identifies **which resource** goes in the path; anything that **filters or
  shapes** a resource goes in the query.

Design rules:
1. **Path = identity, query = filter.** `.../team/backend` names a resource;
   `?since=90d` just narrows it. Two URIs that differ only by query are the
   same underlying resource at different windows.
2. **Stable & guessable.** Categories are a closed, documented set; selectors
   follow the same nouns the tools use (paths are repo-relative).
3. **Collection vs. item.** `git-activity://team` lists teams;
   `git-activity://team/backend` is one team. Same pattern everywhere.
4. **Read-only & idempotent.** A GET on any URI never mutates state.
5. **Percent-encode** path selectors that contain `/` or spaces (file paths).

---

## The URI catalog

### Summary
| URI | Returns |
|-----|---------|
| `git-activity://summary` | summary of the current/default repo |
| `git-activity://summary/{repo}` | per-repo summary (default branch, HEAD, commit count, contributor count, active branches) |

### Team
| URI | Returns |
|-----|---------|
| `git-activity://team` | list of teams |
| `git-activity://team/{team}` | one team's stats (members, owned paths, commit share) — e.g. `git-activity://team/backend` |

### Ownership
| URI | Returns |
|-----|---------|
| `git-activity://ownership/code` | repo-wide ownership map (path → top owners by blame share) |
| `git-activity://ownership/path/{path}` | ownership for one file/dir — e.g. `git-activity://ownership/path/Sources%2FProfile` |

### Contributors
| URI | Returns |
|-----|---------|
| `git-activity://contributors` | ranked contributor list (name, email, commits, first/last) |
| `git-activity://contributors/{login}` | one contributor's activity profile |

### CODEOWNERS
| URI | Returns |
|-----|---------|
| `git-activity://codeowners` | parsed CODEOWNERS rules (glob → owners), unresolved `@team` handles flagged |

### Branches
| URI | Returns |
|-----|---------|
| `git-activity://branches` | branches with ahead/behind vs default + last-commit date |
| `git-activity://branches/{branch}` | one branch's detail |

### Deployments (future)
| URI | Returns |
|-----|---------|
| `git-activity://deployments` | release/tag timeline (offline from git tags) |
| `git-activity://deployments/{env}` | deployment history for an environment (network) |

---

## Query-string filters (examples)

Filters shape a resource without changing its identity:

```
git-activity://summary?since=90d
git-activity://ownership/code?min_share=0.2&top_n=3
git-activity://contributors?since=2026-01-01&limit=25
git-activity://team/backend?include=owned_paths
git-activity://branches?stale_days=30
```

Reserved filter keys (consistent across resources):
- `since` / `until` — time window (relative `90d` or ISO date)
- `top_n`, `limit` — result caps
- `format` — `summary` | `full` (verbosity)

---

## Path vs. query — worked examples

| Intent | URI | Why |
|--------|-----|-----|
| The backend team | `git-activity://team/backend` | `backend` identifies the resource → path |
| Backend team, last 30 days | `git-activity://team/backend?since=30d` | window filters → query |
| Ownership of one file | `git-activity://ownership/path/Sources%2FProfileView.swift` | the path IS the identity → path (encoded) |
| Only strong owners | `git-activity://ownership/code?min_share=0.25` | threshold filters the set → query |

Anti-pattern (avoid): `git-activity://ownership?path=Sources/ProfileView.swift`
— the path is identity, not a filter, so it belongs in the URI path.

---

## Mapping back to Step 3 primitives

Every URI here is a **Resource** (read-only). Parameterized *analysis* stays in
**Tools** — e.g. `risk_hotspots(...)` is a tool, not a URI, because it computes
a ranking from caller params rather than addressing a stable entity. The line:

- Addressable, stable, browsable entity → **Resource URI** (this doc)
- Computed answer from arbitrary params → **Tool** (MCP_PRIMITIVES.md)

## Wave alignment

- **Wave 1 (offline):** `summary`, `summary/{repo}`, `ownership/*`,
  `contributors/*`, `codeowners`, `branches/*`, `deployments` (tags only).
- **Wave 2 (network):** `team`, `team/{team}` (Teams API),
  `deployments/{env}`.
