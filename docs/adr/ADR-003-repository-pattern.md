# ADR-003: Access data through repositories, not the API client directly

- Status: Accepted
- Date: 2025-11-03
- Deciders: Mobile team

## Context

With MVVM in place ([[ADR-001-mvvm-architecture]]) and a single `APIClient`
([[ADR-002-networking-stack]]), ViewModels began calling `APIClient` directly.
This coupled presentation logic to the network layer, made caching impossible
to add in one place, and meant the same endpoint was decoded in several
ViewModels with slightly different models.

## Decision

ViewModels obtain data exclusively through a **Repository**. A repository is the
only type that may depend on `APIClient`. ViewModels depend on a repository
protocol (for example `UserRepository`), never on `APIClient` and never on
`URLSession`.

Rules:

- A `ViewModel` must not import or reference `APIClient`.
- A `ViewModel` must not construct a `URLRequest` or call `URLSession`.
- Each domain area exposes a repository protocol; concrete repositories live in
  the data layer and wrap `APIClient`.

## Consequences

- Caching, retries, and offline behavior can be added inside a repository
  without touching ViewModels.
- One canonical model per endpoint, owned by the repository.
- A ViewModel that calls the API directly is an architecture violation and
  should be reported, for example:
  "[MEDIUM] ViewModel calls API directly — violates ADR-003 (Repository Pattern)".
