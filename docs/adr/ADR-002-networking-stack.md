# ADR-002: Standardize on async/await for networking

- Status: Accepted
- Date: 2025-10-14
- Deciders: Mobile team

## Context

Networking code used a mix of completion handlers, Combine publishers, and
ad-hoc callbacks. The inconsistency made error handling unpredictable.

## Decision

All networking goes through a single `APIClient` exposing `async throws`
methods. Completion-handler and Combine-based request APIs are deprecated and
must not be added to new code.

## Consequences

- Error handling is consistent via `try`/`catch`.
- `APIClient` is the only type permitted to perform URL requests. Higher layers
  must not construct `URLRequest` or call `URLSession` directly.
- How callers reach `APIClient` is governed by [[ADR-003-repository-pattern]].
