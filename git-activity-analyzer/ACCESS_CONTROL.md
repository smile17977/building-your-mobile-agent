# Git Activity Analyzer — Step 7: Access Control & Security

This server is designed to run over **stdio** as a local subprocess. This
document explains the security model, why the default needs no authentication,
and what you **must** do if you deploy it differently.

> **TL;DR for users:** Run it over stdio (the default) and you need no API keys
> or tokens — it runs as you, with your permissions, reachable only by the
> process that launched it. If you expose it over HTTP/SSE, **you** are now
> running a network service and must add authentication (see §4).

---

## 1. Transport security models

| Transport | Security model | Auth needed? |
|-----------|----------------|--------------|
| **stdio** (default) | Runs as a subprocess; inherits the permissions of the user who launched it. No socket, no port — reachable only via the parent process's stdin/stdout. | **No.** There is no network surface to authenticate. |
| **SSE / HTTP** (optional, self-hosted) | Listens on a network port; any client that can reach the port can invoke tools. | **Yes.** API key or JWT verified in middleware, plus TLS. |

The real question is not "is this an MCP server?" but **"is it a network
service?"** stdio = no; SSE/HTTP = yes.

## 2. Why the stdio default needs no authentication

- No listening socket exists, so there is nothing on the network to attack.
- The process runs as the invoking user with exactly that user's file
  permissions — no privilege boundary is crossed.
- The only client is the parent (e.g. Claude Code) that spawned it.

Adding API-key/JWT middleware to a stdio server guards a door that does not
exist. We deliberately **do not** ship transport auth for the default mode.

## 3. Trust & capability model (applies to every transport)

Access control here is mostly about **what the server can do**, not who calls
it. Guarantees this project makes:

1. **Read-only by construction.** Every tool shells out to read-only git
   commands (`git log`, `git blame`, `git rev-list`, `git show`) or read-only
   provider API calls. **No tool writes to the repo, commits, pushes, or
   mutates remote state.** This is the primary safety boundary — even running
   with full user permissions, the server cannot alter history.
2. **No arbitrary command execution.** Git is invoked with fixed argument
   vectors and user input passed as **separate arguments, never interpolated
   into a shell string** (no `shell=True`). See §5.
3. **Path confinement.** `repo_path` scopes every operation to one checkout;
   the server does not read outside the repository it is pointed at.
4. **Least privilege for secrets.** The only credential is the optional
   `GITHUB_TOKEN` for the CI/network tools (§6).

> Run only MCP servers you trust. As the operator of *this* server, the
> read-only guarantee above is what makes it safe to point at any repo you can
> already read.

## 4. If you expose it over SSE / HTTP (self-hosting checklist)

Open-source users may want a remote/shared deployment. If you do, **you become
the operator of a network service** and must add these — none are on by default:

- [ ] **Authentication in middleware** — require an API key (`Authorization:
      Bearer <key>`) or a verified JWT on every request; reject unauthenticated
      calls with 401.
- [ ] **TLS** — terminate HTTPS (reverse proxy or app-level); never ship tokens
      over plaintext.
- [ ] **Bind narrowly** — default to `127.0.0.1`; only bind `0.0.0.0` behind an
      authenticating reverse proxy.
- [ ] **Per-client authorization** — if multiple users connect, constrain which
      `repo_path` values each may pass (the read-only guarantee still lets a
      caller read *any* repo the server process can see).
- [ ] **Rate limiting** — cheap git operations can still be abused; cap request
      rates per key.
- [ ] **Secret isolation** — the server's `GITHUB_TOKEN` is shared by all
      remote callers; scope it minimally and consider per-tenant tokens.

We do not ship an HTTP transport with weak/no auth. If added, auth is a
first-class requirement, not an afterthought.

## 5. Input handling (both transports)

Because tool inputs (paths, refs, queries, patterns) come from a model or a
remote caller, they are untrusted:

- Git is spawned with **argument lists**, never a shell string — no command
  injection via `;`, `$()`, backticks, etc.
- `--` separates options from user-supplied paths/refs so a value like
  `--upload-pack=...` cannot be reinterpreted as a flag.
- `repo_path` is resolved and verified to be a git work-tree before use.
- User-supplied regexes (`fix_pattern`) are applied to text the server already
  fetched, never passed to a shell.
- Provider identifiers (owner/repo/PR) are sent as API parameters, not
  concatenated into URLs unescaped.

## 6. Secret handling (CI / network tools — wave 2)

- `GITHUB_TOKEN` (or `GITLAB_TOKEN`) is read from the **environment only** —
  never a CLI flag, never committed, never written to disk.
- Recommended scopes are **read-only**: `actions:read`, `contents:read`,
  `metadata:read`. The server never needs write scopes.
- Tokens are **never logged** and never included in tool output or error
  messages. Redact before surfacing errors.
- If no token is present, the network tools fail gracefully with a clear
  "credential required" message rather than crashing.

## 7. Open-source hygiene

Because this repo is public:

- Ship a `.env.example` (documenting `GITHUB_TOKEN`) but **never** a real
  `.env`; add `.env` to `.gitignore`.
- No secrets, internal hostnames, org names, or private repo paths in code,
  examples, or fixtures.
- Document the security model (this file) in the README so downstream users
  understand what they are and are not getting by default.
- Add a `SECURITY.md` with a vulnerability-reporting contact.
- State the license and the read-only guarantee prominently.

## Summary

| Concern | Default (stdio) | If self-hosted over HTTP |
|---------|-----------------|--------------------------|
| Transport auth | Not needed (no network surface) | **Required** (API key / JWT + TLS) |
| Runs as | Invoking user | The service account you deploy under |
| Write access | None (read-only by design) | Still none |
| Secrets | `GITHUB_TOKEN` from env (wave 2) | Shared by callers — scope tightly |
| Main risk | Running an untrusted server | Exposing an unauthenticated port |
