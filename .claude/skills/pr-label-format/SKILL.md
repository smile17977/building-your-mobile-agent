---
name: "pr-label-format"
description: "PR label conventions for the development team — how to map PR labels and commit prefixes to user-facing release note categories. Load when processing PR lists for release notes."
---

## Rules 
- Map `feat` or `type: feature` labels → Features section.
- Map `fix` or `type: fix` labels → Fixes section.
- Map `perf` or `type: improvement` labels → Improvements section.
- Exclude PRs labeled `chore`, `internal`, or `refactor`.

## Template

PR label: `feat` Category: Features
PR label: `chore` Action: Exclude from release notes
