---
name: review-pr
description: "The skill should make the agent follow the steps exactly as written. explicit invocation with /review-pr"
disable-model-invocation: true
---

## Steps

1. Fetch the PR using the GitHub MCP server.
2. Delegate style-reviewer style checking.
3. Delegate security-reviewer security checking.
4. Delegate architecture-reviewer architecture checking.
5. Consolidate the three reviewers' outputs (style, security, architecture) into a single review, grouped by category, and present it to the user. Then ask the user for explicit confirmation before posting.
6. Only post on yes or post.