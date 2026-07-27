"""
Git Activity Analyzer — MCP server (stdio transport).

Thin wrapper over gitlib (wave-1, local git). Exposes tools, a repo overview
resource, and prompt workflows. All analysis lives in gitlib.py, which has no
MCP dependency and is independently testable via cli.py.

CI tools (wave 2) are declared but return a "not yet implemented / needs
GITHUB_TOKEN" stub until the network/provider layer is added.

Run:  python server.py         (requires the `mcp` SDK: pip install mcp)
"""
from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

import gitlib

mcp = FastMCP("git-activity-analyzer")


def _j(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def _safe(fn, **kw) -> str:
    try:
        return _j(fn(**kw))
    except gitlib.GitError as e:
        return _j({"error": str(e)})


# ============================ Resources =====================================

@mcp.resource("git-activity://summary/{repo_path}")
def summary(repo_path: str) -> str:
    """Per-repo summary: default branch, remote, HEAD, commit/contributor counts."""
    return _safe(gitlib.repo_overview, repo_path=repo_path)


# ============================ History tools =================================

@mcp.tool()
def recent_commits(repo_path: str, branch: str = "main", time_range: str = "7d",
                   author: Optional[str] = None, top_n: int = 20) -> str:
    """List recent commits, newest first. Use when the user asks what changed
    lately, or wants recent activity by a specific author."""
    return _safe(gitlib.recent_commits, repo_path=repo_path, branch=branch,
                 time_range=time_range, author=author, top_n=top_n)


@mcp.tool()
def file_history(repo_path: str, path: str, branch: str = "main",
                 top_n: int = 30) -> str:
    """Show the commit history of a single file, following renames."""
    return _safe(gitlib.file_history, repo_path=repo_path, path=path,
                 branch=branch, top_n=top_n)


@mcp.tool()
def line_history(repo_path: str, path: str, start_line: int,
                 end_line: Optional[int] = None) -> str:
    """Show which commits last changed a specific range of lines in a file."""
    return _safe(gitlib.line_history, repo_path=repo_path, path=path,
                 start_line=start_line, end_line=end_line)


@mcp.tool()
def search_commits(repo_path: str, query: str, mode: str = "message",
                   top_n: int = 20) -> str:
    """Find commits by searching commit messages or diff content."""
    return _safe(gitlib.search_commits, repo_path=repo_path, query=query,
                 mode=mode, top_n=top_n)


@mcp.tool()
def branch_diff(repo_path: str, base: str = "main", head: str = "HEAD") -> str:
    """Compare two refs: commits ahead/behind and which files differ."""
    return _safe(gitlib.branch_diff, repo_path=repo_path, base=base, head=head)


@mcp.tool()
def commit_detail(repo_path: str, sha: str) -> str:
    """Full detail for one commit: author, message, files, line stats."""
    return _safe(gitlib.commit_detail, repo_path=repo_path, sha=sha)


# ============================ Hotspot tools =================================

@mcp.tool()
def analyze_hotspots(repo_path: str, branch: str = "main",
                     time_range: str = "30d",
                     filter_authors: Optional[list[str]] = None,
                     top_n: int = 10) -> str:
    """Identify files with the highest change frequency. Use for churn,
    refactoring candidates, or which files are most actively modified."""
    return _safe(gitlib.analyze_hotspots, repo_path=repo_path, branch=branch,
                 time_range=time_range, filter_authors=filter_authors,
                 top_n=top_n)


@mcp.tool()
def risk_hotspots(repo_path: str, branch: str = "main", time_range: str = "90d",
                  top_n: int = 20) -> str:
    """Rank files by change-risk (churn x size). Finds bug-prone / refactor areas."""
    return _safe(gitlib.risk_hotspots, repo_path=repo_path, branch=branch,
                 time_range=time_range, top_n=top_n)


@mcp.tool()
def co_change(repo_path: str, path: str, time_range: str = "90d",
              top_n: int = 10) -> str:
    """Files that most often change together with a given file (coupling)."""
    return _safe(gitlib.co_change, repo_path=repo_path, path=path,
                 time_range=time_range, top_n=top_n)


@mcp.tool()
def fix_density(repo_path: str, branch: str = "main", time_range: str = "90d",
                top_n: int = 20, fix_pattern: Optional[str] = None) -> str:
    """Rank files by number of bug-fix commits touching them (defect-prone)."""
    kw = dict(repo_path=repo_path, branch=branch, time_range=time_range,
              top_n=top_n)
    if fix_pattern:
        kw["fix_pattern"] = fix_pattern
    return _safe(gitlib.fix_density, **kw)


# ============================ Ownership tools ===============================

@mcp.tool()
def code_experts(repo_path: str, path: str, top_n: int = 5) -> str:
    """People most knowledgeable about a file/dir, ranked by blame share."""
    return _safe(gitlib.code_experts, repo_path=repo_path, path=path,
                 top_n=top_n)


@mcp.tool()
def suggest_reviewers(repo_path: str, paths: list[str],
                      max_reviewers: int = 3) -> str:
    """Suggest reviewers by combining blame experts with CODEOWNERS rules."""
    return _safe(gitlib.suggest_reviewers, repo_path=repo_path, paths=paths,
                 max_reviewers=max_reviewers)


@mcp.tool()
def bus_factor(repo_path: str, path: str) -> str:
    """Estimate bus-factor risk: how concentrated a path's knowledge is."""
    return _safe(gitlib.bus_factor, repo_path=repo_path, path=path)


# ============================ CI tools (wave 2 stubs) =======================

_CI_STUB = {"error": "CI tools require the wave-2 GitHub/GitLab provider layer "
                     "and a GITHUB_TOKEN. Not yet implemented."}


@mcp.tool()
def ci_status(repo_path: str, ref: str = "main",
              pr: Optional[int] = None) -> str:
    """Latest CI status for a ref/PR. (Wave 2 — needs provider API + token.)"""
    return _j(_CI_STUB)


@mcp.tool()
def ci_failures(repo_path: str, run_id: Optional[str] = None, ref: str = "main",
                log_lines: int = 40) -> str:
    """Failing jobs + log excerpts for a CI run. (Wave 2.)"""
    return _j(_CI_STUB)


@mcp.tool()
def flaky_jobs(repo_path: str, workflow: Optional[str] = None,
               window: int = 30) -> str:
    """Jobs that flip pass/fail across recent runs. (Wave 2.)"""
    return _j(_CI_STUB)


@mcp.tool()
def ci_health(repo_path: str, workflow: Optional[str] = None,
              window: int = 50) -> str:
    """Workflow pass rate / duration trend. (Wave 2.)"""
    return _j(_CI_STUB)


# ============================ Prompts =======================================

@mcp.prompt()
def onboard_to_area(repo_path: str, path: str) -> str:
    """Orient someone new to a directory/subsystem (fully offline)."""
    return (
        f"Help me get oriented in `{path}` of the repo at `{repo_path}`.\n"
        f"1. Read git-activity://summary/{repo_path} for the big picture.\n"
        f"2. Call file_history(repo_path='{repo_path}', path='{path}') for how it evolved.\n"
        f"3. Call code_experts(repo_path='{repo_path}', path='{path}') for who to ask.\n"
        f"4. Call co_change(repo_path='{repo_path}', path='{path}') for coupled files.\n"
        f"5. Call bus_factor(repo_path='{repo_path}', path='{path}') for ownership risk.\n"
        f"Then synthesize a short orientation brief: purpose, key commits, "
        f"go-to people, coupled files, and risks."
    )


@mcp.prompt()
def hotspot_health_check(repo_path: str, time_range: str = "90d",
                         top_n: int = 20) -> str:
    """Scan for decay signals: churn x size, fix-prone, concentrated ownership."""
    return (
        f"Do a maintenance health check on the repo at `{repo_path}`.\n"
        f"1. Call risk_hotspots(repo_path='{repo_path}', time_range='{time_range}', top_n={top_n}).\n"
        f"2. Call fix_density(repo_path='{repo_path}', time_range='{time_range}', top_n={top_n}).\n"
        f"3. For the union of those files, call bus_factor(repo_path='{repo_path}', path=<file>).\n"
        f"Then produce a prioritized list: file, risk signals present "
        f"(churn/fixes/bus-factor), and recommended action."
    )


@mcp.prompt()
def pr_risk_report(repo_path: str, head: str, base: str = "main") -> str:
    """Assess PR risk: changes, hotspots, reviewers, CI (CI degrades offline)."""
    return (
        f"Assess the risk of `{head}` vs `{base}` in `{repo_path}`.\n"
        f"1. Call branch_diff(repo_path='{repo_path}', base='{base}', head='{head}').\n"
        f"2. For the changed files, call risk_hotspots and fix_density; "
        f"call co_change on the riskiest to spot missing companion edits.\n"
        f"3. Call suggest_reviewers(repo_path='{repo_path}', paths=<changed files>).\n"
        f"4. Call ci_status(repo_path='{repo_path}', ref='{head}') — if it "
        f"reports the wave-2 stub, note 'CI check unavailable offline'.\n"
        f"Then give a risk verdict (low/med/high) with rationale, reviewers, "
        f"CI state, and companion-edit hints."
    )


if __name__ == "__main__":
    mcp.run()  # stdio transport
