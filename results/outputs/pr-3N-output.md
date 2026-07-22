PR #3 Review — Add payment service

File: src/PaymentService.kt (new)

🔒 Security

- [HIGH] Line 8 — Hardcoded live API key. val API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c" commits a live payment credential to source control. This is the most serious issue in the PR. Move it out of code (e.g. BuildConfig sourced from gradle.properties/CI secrets, or a runtime secrets manager), and rotate the leaked key — once committed, it must be considered compromised.
- [MEDIUM] Line 15 — No validation of amount. charge(amount: Int, ...) accepts any Int, including zero/negative values. Validate it is positive and within sane transaction bounds before charging.
- [MEDIUM] Line 15 — No validation of token. The payment token is accepted unchecked. Verify it is non-empty and matches the expected format.
- [LOW] Lines 16–17 — Empty body / TLS not verifiable. The method is a comment-only stub, so Authorization header construction and TLS/cert-pinning can't be confirmed. Ensure TLS is enforced (and consider certificate pinning) for the payments endpoint once implemented.


🏛️ Architecture

- [MEDIUM] Lines 10–13 — Retrofit instantiated in-class, no DI. The Retrofit instance is built inside the service instead of being injected. Inject it via the constructor for testability and loose coupling.
- [MEDIUM] Whole class — No repository pattern. A service directly owning the HTTP client bypasses the repository layer expected in the MVVM setup. Introduce a PaymentRepository abstraction that ViewModels depend on.
- [LOW] Lines 15–17 — Incomplete method. charge() has no implementation — implement it or clearly mark it as a documented placeholder.
- [LOW] Lines 15–17 — No error handling / async model. No return type, error path, or async mechanism. Use a suspend function (coroutines) with proper error handling to integrate with MVVM.

🎨 Style

- [MEDIUM] Line 8 — Naming convention. API_KEY uses SCREAMING_SNAKE_CASE but is a regular property, not a const val. Either rename to apiKey (camelCase) or move to a companion object { const val ... } (moot once the key is removed).
- [LOW] Line 8 — Visibility. The property is public by default; it should be private (again, moot once removed from source).

Summary

One HIGH blocker (hardcoded live API key — must be removed and rotated), several MEDIUM issues around input validation and architecture (DI + repository pattern), and minor style/completeness cleanups. I recommend this PR not be merged until at least the hardcoded key is remediated.
