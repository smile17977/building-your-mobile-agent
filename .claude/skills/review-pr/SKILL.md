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
5. Compile findings into the output format, present them, and ask for 
6. Only post on yes or post.