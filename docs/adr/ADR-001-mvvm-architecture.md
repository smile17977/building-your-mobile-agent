# ADR-001: Adopt MVVM for the presentation layer

- Status: Accepted
- Date: 2025-09-02
- Deciders: Mobile team

## Context

The app's view controllers had grown to several hundred lines each, mixing UI
wiring, networking, and formatting logic. This made screens hard to test and
hard to reason about.

## Decision

We adopt the Model-View-ViewModel (MVVM) pattern for all new screens. A
`ViewController` (the View) owns layout and user input only. A `ViewModel`
exposes display-ready state and handles presentation logic. Views must not
contain business logic; ViewModels must not import UIKit.

## Consequences

- Screens become unit-testable through their ViewModels.
- A new ViewModel type is required for each screen, adding some boilerplate.
- See [[ADR-003-repository-pattern]] for how ViewModels obtain their data.
