"""
cli.py — exercise every wave-1 tool from the terminal, no MCP SDK required.

Usage:
    python cli.py <tool> [--key value ...]
    python cli.py overview --repo_path .
    python cli.py analyze_hotspots --repo_path . --time_range all --top_n 10
    python cli.py code_experts --repo_path . --path Sources

This is a thin dispatcher over gitlib so the analysis can be validated before
the MCP wrapper (server.py) is installable.
"""
from __future__ import annotations

import argparse
import json
import sys

import gitlib

# tool name -> (callable, list of (arg, type, default))
TOOLS = {
    "overview":         (gitlib.repo_overview, [("repo_path", str, ".")]),
    "recent_commits":   (gitlib.recent_commits, [("repo_path", str, "."), ("branch", str, "main"), ("time_range", str, "7d"), ("author", str, None), ("top_n", int, 20)]),
    "file_history":     (gitlib.file_history, [("repo_path", str, "."), ("path", str, None), ("branch", str, "main"), ("top_n", int, 30)]),
    "line_history":     (gitlib.line_history, [("repo_path", str, "."), ("path", str, None), ("start_line", int, None), ("end_line", int, None)]),
    "search_commits":   (gitlib.search_commits, [("repo_path", str, "."), ("query", str, None), ("mode", str, "message"), ("top_n", int, 20)]),
    "branch_diff":      (gitlib.branch_diff, [("repo_path", str, "."), ("base", str, "main"), ("head", str, "HEAD")]),
    "commit_detail":    (gitlib.commit_detail, [("repo_path", str, "."), ("sha", str, None)]),
    "analyze_hotspots": (gitlib.analyze_hotspots, [("repo_path", str, "."), ("branch", str, "main"), ("time_range", str, "30d"), ("top_n", int, 10)]),
    "risk_hotspots":    (gitlib.risk_hotspots, [("repo_path", str, "."), ("branch", str, "main"), ("time_range", str, "90d"), ("top_n", int, 20)]),
    "co_change":        (gitlib.co_change, [("repo_path", str, "."), ("path", str, None), ("time_range", str, "90d"), ("top_n", int, 10)]),
    "fix_density":      (gitlib.fix_density, [("repo_path", str, "."), ("branch", str, "main"), ("time_range", str, "90d"), ("top_n", int, 20)]),
    "code_experts":     (gitlib.code_experts, [("repo_path", str, "."), ("path", str, None), ("top_n", int, 5)]),
    "bus_factor":       (gitlib.bus_factor, [("repo_path", str, "."), ("path", str, None)]),
    "suggest_reviewers":(gitlib.suggest_reviewers, [("repo_path", str, "."), ("paths", str, None), ("max_reviewers", int, 3)]),
}


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] not in TOOLS:
        print("tools:", ", ".join(TOOLS))
        return 1
    tool = argv[0]
    fn, spec = TOOLS[tool]
    ap = argparse.ArgumentParser(prog=f"cli.py {tool}")
    for name, typ, default in spec:
        ap.add_argument(f"--{name}", default=default)
    ns = ap.parse_args(argv[1:])
    kwargs = {}
    for name, typ, default in spec:
        val = getattr(ns, name)
        if val is None:
            continue
        if name == "paths":               # comma-separated list
            kwargs[name] = [p for p in str(val).split(",") if p]
        elif typ is int:
            kwargs[name] = int(val)
        else:
            kwargs[name] = val
    try:
        result = fn(**kwargs)
    except gitlib.GitError as e:
        print(json.dumps({"error": str(e)}, indent=2))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
