---
name: "draft-release-notes"
description: "Draft release notes for the app from merged PRs. Triggered explicitly with /draft-release-notes <version>."
disable-model-invocation: true
---

## Rules

Before drafting the Features section, read `docs/product-glossary.md`.

If a PR title or description matches a term in the `Search term` column, use the corresponding value from the `Release notes name` column in the output instead of the original wording.

## Steps

1. Fetch all merged PRs from the repository's main branch since the last release using the GitHub MCP server.
2. Apply the `pr-label-format` skill to categorize each PR.
3. Delegate description cleanup to the `ticket-fetcher` subagent. Pass the PR numbers, titles, and descriptions as the task prompt. Receive the cleaned list.
4. Delegate categorization to the `categorizer` subagent. Pass `ticket-fetcher`'s output as the task prompt. Receive the sorted Markdown.
5. Present the complete draft to the user with the version number `$ARGUMENTS`. Ask: "Review complete. Approve to publish, or reply with edits."
6. After every completed review, append one line to `review_history.md`.
7. Only publish to GitHub releases after receiving explicit approval.


Use this format for review-history.md:
- Date: <year-month-day>
- PR: <PR number and title>
- Top finding: <short description>
- Severity: <severity>
