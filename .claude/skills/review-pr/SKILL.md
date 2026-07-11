---
name: review-pr
description: "The skill should make the agent follow the steps exactly as written. explicit invocation with /review-pr"
disable-model-invocation: true
---

## Steps

1. Fetch the PR using the GitHub MCP server.
2. Apply the `swift-conventions` skill to Swift files.
3. Apply the `kotlin-conventions` skill to Kotlin files.
4. Flag security issues.
5. Compile findings into the output format, present them, and ask for 
6. Only post on yes or post.
