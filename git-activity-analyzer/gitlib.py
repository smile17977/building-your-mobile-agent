"""
gitlib — wave-1 git analysis for the Git Activity Analyzer MCP.

Pure Python + the `git` CLI. NO dependency on the `mcp` SDK, so this module
runs and can be tested today, independent of network/proxy state. server.py
(the MCP wrapper) and cli.py both call into these functions.

Safety invariants (see ACCESS_CONTROL.md):
- Read-only: only ever runs read-only git subcommands.
- No shell: git is invoked with an argument list, never a shell string.
- `--` separates options from user paths/refs.
- repo_path is verified to be a git work-tree before use.
"""
from __future__ import annotations

import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone

# ---- time_range enum -> git --since expression -------------------------------

_TIME_RANGE = {
    "7d": "7 days ago",
    "30d": "30 days ago",
    "90d": "90 days ago",
    "all": None,  # no --since
}


class GitError(Exception):
    pass


def _since_arg(time_range: str) -> list[str]:
    if time_range not in _TIME_RANGE:
        raise GitError(f"invalid time_range {time_range!r}; "
                       f"choose from {sorted(_TIME_RANGE)}")
    expr = _TIME_RANGE[time_range]
    return [f"--since={expr}"] if expr else []


def _run(repo_path: str, args: list[str]) -> str:
    """Run a read-only git command with an argument vector (no shell)."""
    repo = os.path.abspath(os.path.expanduser(repo_path))
    if not os.path.isdir(repo):
        raise GitError(f"repo_path does not exist: {repo}")
    # verify it's a work tree
    check = subprocess.run(
        ["git", "-C", repo, "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True)
    if check.returncode != 0 or check.stdout.strip() != "true":
        raise GitError(f"not a git work tree: {repo}")
    proc = subprocess.run(["git", "-C", repo, *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


# Unit separator record format for safe parsing of `git log`.
_US = "\x1f"   # field sep
_RS = "\x1e"   # record sep
_LOG_FMT = _US.join(["%H", "%h", "%an", "%ae", "%aI", "%s"]) + _RS


def _parse_commits(out: str) -> list[dict]:
    commits = []
    for rec in out.split(_RS):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split(_US)
        if len(parts) < 6:
            continue
        sha, short, an, ae, aiso, subject = parts[:6]
        commits.append({
            "sha": sha, "short_sha": short,
            "author": an, "email": ae,
            "date": aiso, "subject": subject,
        })
    return commits


# ---- History -----------------------------------------------------------------

def recent_commits(repo_path: str, branch: str = "main",
                   time_range: str = "7d", author: str | None = None,
                   top_n: int = 20) -> list[dict]:
    args = ["log", branch, f"--pretty=format:{_LOG_FMT}",
            f"-n{top_n}", *_since_arg(time_range)]
    if author:
        args.append(f"--author={author}")
    return _parse_commits(_run(repo_path, args))


def file_history(repo_path: str, path: str, branch: str = "main",
                 top_n: int = 30) -> list[dict]:
    args = ["log", branch, f"--pretty=format:{_LOG_FMT}",
            f"-n{top_n}", "--follow", "--", path]
    return _parse_commits(_run(repo_path, args))


def line_history(repo_path: str, path: str, start_line: int,
                 end_line: int | None = None) -> list[dict]:
    end = end_line if end_line is not None else start_line
    args = ["log", f"-L{start_line},{end},:{path}",
            "--no-patch", f"--pretty=format:{_LOG_FMT}"]
    return _parse_commits(_run(repo_path, args))


def search_commits(repo_path: str, query: str, mode: str = "message",
                   top_n: int = 20) -> list[dict]:
    if mode not in ("message", "diff"):
        raise GitError("mode must be 'message' or 'diff'")
    args = ["log", f"--pretty=format:{_LOG_FMT}", f"-n{top_n}"]
    if mode == "message":
        args += [f"--grep={query}", "-i"]
    else:
        args += [f"-S{query}"]
    return _parse_commits(_run(repo_path, args))


def branch_diff(repo_path: str, base: str = "main",
                head: str = "HEAD") -> dict:
    counts = _run(repo_path, ["rev-list", "--left-right", "--count",
                              f"{base}...{head}"]).strip().split()
    behind, ahead = (int(counts[0]), int(counts[1])) if len(counts) == 2 else (0, 0)
    files = [f for f in _run(repo_path,
             ["diff", "--name-only", f"{base}...{head}"]).splitlines() if f]
    return {"base": base, "head": head, "ahead": ahead, "behind": behind,
            "changed_files": files, "changed_count": len(files)}


def commit_detail(repo_path: str, sha: str) -> dict:
    meta = _parse_commits(_run(repo_path,
        ["show", "-s", f"--pretty=format:{_LOG_FMT}", sha]))
    body = _run(repo_path, ["show", "-s", "--pretty=format:%B", sha]).strip()
    numstat = _run(repo_path, ["show", "--numstat", "--pretty=format:", sha])
    files = []
    ins = dels = 0
    for line in numstat.splitlines():
        if not line.strip():
            continue
        a, d, name = (line.split("\t") + ["", "", ""])[:3]
        ai = int(a) if a.isdigit() else 0
        di = int(d) if d.isdigit() else 0
        ins += ai; dels += di
        files.append({"path": name, "insertions": ai, "deletions": di})
    out = meta[0] if meta else {"sha": sha}
    out.update({"body": body, "files": files,
                "insertions": ins, "deletions": dels,
                "files_changed": len(files)})
    return out


# ---- Hotspots ----------------------------------------------------------------

def _numstat_by_file(repo_path: str, branch: str, time_range: str,
                     authors: list[str] | None = None):
    args = ["log", branch, "--numstat", "--pretty=format:%H",
            *_since_arg(time_range)]
    for a in (authors or []):
        args.append(f"--author={a}")
    out = _run(repo_path, args)
    commits = Counter()      # path -> #commits touching it
    ins = Counter(); dels = Counter()
    for line in out.splitlines():
        line = line.strip()
        if not line or _US in line:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        a, d, name = parts
        commits[name] += 1
        ins[name] += int(a) if a.isdigit() else 0
        dels[name] += int(d) if d.isdigit() else 0
    return commits, ins, dels


def analyze_hotspots(repo_path: str, branch: str = "main",
                     time_range: str = "30d",
                     filter_authors: list[str] | None = None,
                     top_n: int = 10) -> list[dict]:
    """Churn ranking: files by change frequency."""
    commits, ins, dels = _numstat_by_file(repo_path, branch, time_range,
                                          filter_authors)
    ranked = sorted(commits.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    return [{"path": p, "commits": c,
             "insertions": ins[p], "deletions": dels[p]} for p, c in ranked]


def _file_loc(repo_path: str, path: str) -> int:
    full = os.path.join(os.path.abspath(os.path.expanduser(repo_path)), path)
    try:
        with open(full, "r", errors="ignore") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def risk_hotspots(repo_path: str, branch: str = "main",
                  time_range: str = "90d", top_n: int = 20) -> list[dict]:
    """Risk = churn (commits) x current size (LOC)."""
    commits, ins, dels = _numstat_by_file(repo_path, branch, time_range, None)
    scored = []
    for path, c in commits.items():
        loc = _file_loc(repo_path, path)
        scored.append({"path": path, "commits": c, "loc": loc,
                       "risk": c * loc})
    scored.sort(key=lambda r: r["risk"], reverse=True)
    return scored[:top_n]


def co_change(repo_path: str, path: str, time_range: str = "90d",
              top_n: int = 10) -> list[dict]:
    """Files that most often change in the same commits as `path`."""
    out = _run(repo_path, ["log", f"--pretty=format:{_RS}%H",
                           "--name-only", *_since_arg(time_range)])
    together = Counter()
    for rec in out.split(_RS):
        files = [l for l in rec.splitlines() if l and _US not in l][1:]
        files = [f for f in files if f]
        if path in files:
            for f in files:
                if f != path:
                    together[f] += 1
    return [{"path": p, "co_changes": n}
            for p, n in together.most_common(top_n)]


def fix_density(repo_path: str, branch: str = "main", time_range: str = "90d",
                top_n: int = 20,
                fix_pattern: str = r"(?i)\b(fix|bug|hotfix|patch|regression)\b"
                ) -> list[dict]:
    rx = re.compile(fix_pattern)
    out = _run(repo_path, ["log", branch, f"--pretty=format:{_RS}%s",
                           "--name-only", *_since_arg(time_range)])
    fixes = Counter()
    for rec in out.split(_RS):
        lines = rec.split("\n")
        subject = lines[0].strip() if lines else ""
        if not subject or not rx.search(subject):
            continue
        for f in lines[1:]:
            if f and _US not in f:
                fixes[f] += 1
    return [{"path": p, "fix_commits": n} for p, n in fixes.most_common(top_n)]


# ---- Ownership ---------------------------------------------------------------

def _blame_authors(repo_path: str, path: str) -> Counter:
    """author -> #lines owned (via blame). Works on a single file."""
    out = _run(repo_path, ["blame", "--line-porcelain", "--", path])
    authors = Counter()
    for line in out.splitlines():
        if line.startswith("author "):
            authors[line[len("author "):].strip()] += 1
    return authors


def _paths_under(repo_path: str, path: str) -> list[str]:
    """Tracked files at/under a path."""
    out = _run(repo_path, ["ls-files", "--", path])
    return [l for l in out.splitlines() if l]


def code_experts(repo_path: str, path: str, top_n: int = 5) -> list[dict]:
    files = _paths_under(repo_path, path) or [path]
    total = Counter()
    for f in files:
        try:
            total.update(_blame_authors(repo_path, f))
        except GitError:
            continue
    grand = sum(total.values()) or 1
    return [{"author": a, "lines": n, "share": round(n / grand, 3)}
            for a, n in total.most_common(top_n)]


def bus_factor(repo_path: str, path: str) -> dict:
    experts = code_experts(repo_path, path, top_n=1000)
    total = sum(e["lines"] for e in experts) or 1
    # bus factor: how many authors to reach >50% of the code
    cum = 0; bf = 0
    for e in experts:
        cum += e["lines"]; bf += 1
        if cum / total > 0.5:
            break
    top_share = experts[0]["share"] if experts else 0.0
    return {"path": path, "contributors": len(experts),
            "bus_factor": bf, "top_owner_share": top_share,
            "risk": "high" if bf <= 1 else "medium" if bf == 2 else "low",
            "top_owners": experts[:3]}


def _parse_codeowners(repo_path: str) -> list[tuple[str, list[str]]]:
    repo = os.path.abspath(os.path.expanduser(repo_path))
    for loc in ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"):
        p = os.path.join(repo, loc)
        if os.path.isfile(p):
            rules = []
            with open(p, errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    rules.append((parts[0], parts[1:]))
            return rules
    return []


def suggest_reviewers(repo_path: str, paths: list[str],
                      max_reviewers: int = 3) -> dict:
    # blame-based experts across all touched paths
    votes = Counter()
    for p in paths:
        for e in code_experts(repo_path, p, top_n=5):
            votes[e["author"]] += e["lines"]
    blame_based = [a for a, _ in votes.most_common(max_reviewers)]
    # CODEOWNERS matches (simple suffix/glob-ish match)
    owners = set()
    for pattern, os_owners in _parse_codeowners(repo_path):
        pat = pattern.strip("/")
        for p in paths:
            if pat in p or pattern == "*":
                owners.update(os_owners)
    return {"blame_experts": blame_based,
            "codeowners": sorted(owners),
            "suggested": (blame_based + [o for o in sorted(owners)
                                         if o not in blame_based])[:max_reviewers]}


# ---- Resource: repo overview -------------------------------------------------

def repo_overview(repo_path: str) -> dict:
    default_branch = "HEAD"
    try:
        ref = _run(repo_path, ["symbolic-ref", "--short", "HEAD"]).strip()
        default_branch = ref or "HEAD"
    except GitError:
        pass
    try:
        remote = _run(repo_path, ["remote", "get-url", "origin"]).strip()
    except GitError:
        remote = ""
    head = _run(repo_path, ["rev-parse", "--short", "HEAD"]).strip()
    total = _run(repo_path, ["rev-list", "--count", "HEAD"]).strip()
    shortlog = _run(repo_path, ["shortlog", "-sne", "HEAD"])
    contributors = len([l for l in shortlog.splitlines() if l.strip()])
    branches = [b.strip("* ").strip()
                for b in _run(repo_path, ["branch", "--format=%(refname:short)"]
                              ).splitlines() if b.strip()]
    return {"branch": default_branch, "remote": remote, "head": head,
            "total_commits": int(total) if total.isdigit() else 0,
            "contributors": contributors, "branches": branches,
            "codeowners_rules": len(_parse_codeowners(repo_path))}
