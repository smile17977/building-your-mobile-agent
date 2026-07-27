# Git Activity Analyzer — Data Sources

Mapping of what organizational data the server needs, where it lives, how it's
accessed, and what it gates (which tools depend on it).

## Summary table

| # | Data | Source | Access mechanism | Auth | Serves tools |
|---|------|--------|------------------|------|--------------|
| 1 | Commit logs, file change history, branch info | **Local git directory** | Shell out to `git` in a checkout on disk | None (filesystem) | H1–H6, P1–P4 |
| 2 | Author contributions, CI/CD run history | **GitHub / GitLab API** | REST/GraphQL over HTTPS | Token (`GITHUB_TOKEN` / PAT) | C1–C4, (author stats optional) |
| 3 | Team structure, repo ownership | **CODEOWNERS + Git provider API** | `CODEOWNERS` file (local) + Teams/Members API | Token | O1–O3 |
| 4 | Deployment history, versions, timestamps | **CI/CD or deployment service** | Provider API (Actions deployments, releases, tags) | Token | (future — not in v1 catalog) |

---

## 1. Local git directory  ✅ available now (offline)

**Lives in:** the working checkout on disk (`.git/`), reached via the `git` CLI.

**Exact data pulled:**
- Commit log — `git log` (sha, author, email, date, subject, body)
- File change history — `git log --follow --name-status -- <path>`
- Line-level history — `git log -L`, `git blame --line-porcelain`
- Diff content search — `git log -S<string>` / `-G<regex>`
- Branch info — `git rev-list --left-right --count base...head`, `git branch`
- Churn / co-change — derived by aggregating `git log --numstat`
- File size/complexity proxy — `wc -l` / line counts per file

**Auth:** none. **Blockers:** none — fully offline.
**Serves:** H1–H6 (History), P1–P4 (Hotspots), and the blame half of O1–O3.

**Config needed:** `repo_path` (absolute path to the checkout). Default: cwd.

---

## 2. GitHub / GitLab API  ⚠️ gated on token + network

**Lives in:** the hosting provider (GitHub Actions / GitLab CI), not on disk.

**Exact data pulled:**
- CI runs & status — Actions `GET /repos/{o}/{r}/actions/runs`, checks API
- Job details & logs — `GET .../jobs`, job-log download (for `ci_failures`)
- Historical runs (flaky/health) — paginated runs filtered by workflow/branch
- Author contribution stats (optional) — `GET /repos/{o}/{r}/stats/contributors`

**Auth:** `GITHUB_TOKEN` env var (fine-grained PAT, read-only: `actions:read`,
`contents:read`, `metadata:read`). GitLab equivalent: `GITLAB_TOKEN`.

**Blockers:**
- Requires outbound HTTPS — **currently blocked by the corporate proxy**
  (ProxyError / SSL handshake timeout; same issue that blocks pip & Playwright
  downloads). Browsing via Chrome works, but API calls from Python do not yet.
- Rate limits (5000 req/hr authenticated).

**Serves:** C1–C4 (CI). **Build wave:** deferred (wave 2).

**Config needed:** `owner`, `repo`, `GITHUB_TOKEN`, optional `api_base_url`
(for GitHub Enterprise / GitLab self-hosted).

---

## 3. Team structure & repo ownership  ⚠️ partly offline

**Lives in:** two places —
- **CODEOWNERS file** (local, in `.github/`, `docs/`, or repo root) — offline ✅
- **Teams & membership** (provider API) — GitHub `GET /orgs/{org}/teams`,
  `.../members`; resolves `@org/team` handles in CODEOWNERS to people — gated ⚠️

**Exact data pulled:**
- Path → owner rules (glob patterns → users/teams) from CODEOWNERS
- Team → member expansion (only if CODEOWNERS references `@team` handles)
- Contributor identity for blame (from local git — see source 1)

**Auth:** none for the CODEOWNERS file; token for team expansion.
**Blockers:** team expansion needs the API (proxy-gated). Blame-based ownership
(O1, O3) works fully offline; only CODEOWNERS-team resolution in O2 needs network.

**Serves:** O1–O3 (Ownership). O1/O3 offline; O2 partial-offline.

---

## 4. Deployment history, versions, timestamps  🔮 future

**Lives in:** the CI/CD or deployment service — GitHub Deployments API,
Releases/Tags, or an external deploy tool (Argo, Spinnaker, etc.).

**Exact data pulled (when added):**
- Releases & tags — `GET /repos/{o}/{r}/releases`, `git tag --sort=-creatordate`
  (tags are also readable **offline** from local git)
- Deployment events — GitHub Deployments API (env, ref, timestamp, status)

**Auth:** token (+ external service creds if not GitHub-native).
**Blockers:** network/proxy + possibly a separate deploy-tool integration.

**Serves:** not in the locked v1 catalog. Noted so the interface leaves room
(e.g. a future `deployment_history` / `release_timeline` tool). Tags alone could
be exposed offline if useful.

---

## What this means for the build

| Domain | Data sources | Runnable now? |
|--------|--------------|---------------|
| History (H1–H6) | Local git | ✅ Yes |
| Hotspots (P1–P4) | Local git | ✅ Yes |
| Ownership O1, O3 | Local git blame | ✅ Yes |
| Ownership O2 | Local CODEOWNERS + (team API) | ◑ Partial (offline w/o team expansion) |
| CI (C1–C4) | GitHub/GitLab API | ⛔ Deferred (proxy blocks outbound HTTPS) |
| Deployment (future) | CI/CD / releases / tags | 🔮 Not in v1 (tags readable offline) |

**Wave 1 (build + test now):** everything backed purely by local git —
History, Hotspots, and the blame-based Ownership tools.
**Wave 2 (needs token + network):** CI tools and CODEOWNERS-team expansion.
