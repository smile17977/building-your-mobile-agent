# Test session 4

 /review-pr 3 in https://github.com/nebius-academy-templates/mobile-pr-review-practice

I'll review PR #3 in that repo. Let me start by fetching the PR.

  Called github 3 times

PR #3 has changes (one Kotlin file, 18 additions). Now I'll delegate to the three reviewers in parallel.

⏺ 3 agents finished
style-reviewer (Style review of PaymentService.kt) · 2 tool uses · 4.4k tokens
⎿  Done
security-reviewer (Security review of PaymentService.kt) · 1 tool use · 3.2k tokens
⎿  Done
architecture-reviewer (Architecture review of PaymentService.kt) · 10 tool uses · 6.1k tokens
⎿  Done

All three reviewers have reported. Here's the consolidated review.

---
PR Review: #3 — Add payment service

File: src/PaymentService.kt (+18) · Author: @ispaniuktripleten

---
🔴 Security

- [HIGH] Hardcoded live API key — PaymentService.kt:8
val API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c" is a live production secret committed to source. It's now in version-control history, visible to anyone with repo access, and will be caught by automated secret scanners. Rotate the key immediately, remove it from the code, and load it from BuildConfig/secure config instead of a source literal. This alone should block the merge.
- [MEDIUM] No input validation in charge() — PaymentService.kt:15
charge(amount: Int, token: String) accepts any input. Guard against non-positive amount, blank token, and an upper transaction limit.
- [MEDIUM] No TLS/certificate pinning — Retrofit is built with no certificate pinning for api.rideapp.com, leaving payment traffic exposed to MITM. Add pinning for the payments host.

🏗️ Architecture

- [HIGH] Retrofit instantiated inline (no DI) — PaymentService.kt:10
The Retrofit instance is constructed inside the class. Inject it via the constructor so the class is testable and decoupled.
- [HIGH] No repository layer — PaymentService exposes network details directly. Wrap it behind a PaymentRepository that offers a domain-level interface, per the repository pattern.
- [LOW] No MVVM flow — payment operations should be driven through a ViewModel that owns state/lifecycle; the service shouldn't be referenced directly from UI.

🎨 Style (Kotlin)

- [MEDIUM] Constant declaration style — PaymentService.kt:8
API_KEY uses correct UPPER_SNAKE_CASE naming, but as a secret it shouldn't live here at all. If a genuine constant were needed, it should be const val in a companion object, not a mutable class property. (Moot once the key is removed.)

⚙️ Minor

- Missing trailing newline at end of file.
- charge() is an empty stub (comment only) — no request, error handling, or coroutine scope. Full implementation can't be reviewed yet.

---
Bottom line: The hardcoded live payment API key is a critical, merge-blocking issue — rotate it now. Beyond that, the service needs DI + a repository abstraction and input validation before it's production-ready.

---
Would you like me to post this as a review comment on PR #3? I won't post anything until you confirm.