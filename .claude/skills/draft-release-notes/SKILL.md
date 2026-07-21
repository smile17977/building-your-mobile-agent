---
name: "draft-release-notes"
description: "Draft release notes for the app from merged PRs. Triggered explicitly with /draft-release-notes <version>."
disable-model-invocation: true
---

## Steps

1. Fetch all merged PRs from the repository's main branch since the last release using the GitHub MCP server.
2. Apply the `pr-label-format` skill to categorize each PR.
3. Delegate description cleanup to the `ticket-fetcher` subagent. Pass the PR numbers, titles, and descriptions as the task prompt. Receive the cleaned list.
4. Delegate categorization to the `categorizer` subagent. Pass `ticket-fetcher`'s output as the task prompt. Receive the sorted Markdown.
5. Present the complete draft to the user with the version number `$ARGUMENTS`. Ask: "Review complete. Approve to publish, or reply with edits."
6. Only publish to GitHub releases after receiving explicit approval.
