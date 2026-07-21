# Test session 4

/review-pr 3 in https://github.com/nebius-academy-templates/mobile-pr-review-practice

I'll review PR #3. Let me start by fetching it from the GitHub MCP server.

  Called github 2 times

The PR has changes (18 additions, 1 file). Now let me delegate to the three reviewers concurrently. Each is a read-only agent, so I'll pass them the diff directly.

⏺ 3 agents finished
style-reviewer (Style review of PR #3) · 1 tool use · 3.0k tokens
⎿  Done
security-reviewer (Security review of PR #3) · 1 tool use · 3.0k tokens
⎿  Done
architecture-reviewer (Architecture review of PR #3) · 2 tool uses · 4.2k tokens
⎿  Done

All three reviewers have reported. Here is the consolidated review.

---
PR #3 Review — Add payment service

File: src/PaymentService.kt (+18, new file)

🔒 Security

- 🔴 HIGH — Hardcoded live API key. val API_KEY = "sk-live-..." is a live secret committed to source. It leaks into git history, the compiled APK, and to anyone with repo access. Must be remediated before merge. Move it to BuildConfig (from Gradle properties / CI secrets), a secure config server, or the Android Keystore — and rotate the exposed key.
- 🟠 MEDIUM — No input validation in charge(). amount and token are used unchecked. Validate amount > 0 and that token is non-empty/well-formed before charging.
- 🟡 LOW — No transport hardening. No TLS certificate pinning or security interceptors on the Retrofit client for a payment endpoint.

🏗️ Architecture

- 🟠 MEDIUM — Retrofit instantiated in-class (DI violation). The Retrofit instance is built directly inside PaymentService. It should be injected (Hilt/Dagger) via the constructor for testability and configuration.
- 🟠 MEDIUM — Missing repository/layer separation. Network setup and business logic are combined in one class. Split into a data source (Retrofit API interface), a repository, and a use case/service, per MVVM + repository pattern.
- 🟡 LOW — charge() is not async-ready. For MVVM it should be suspend (or return Flow/Result) with proper error/state handling rather than a Unit-returning stub.

🎨 Style

- 🟠 MEDIUM — Constant naming. API_KEY uses SCREAMING_SNAKE_CASE but is a regular val. Kotlin reserves that casing for const val; use apiKey, or better, extract it out of the class entirely (see security).
- 🟡 LOW — Missing trailing newline at end of file.

Summary

The headline blocker is the hardcoded live payment API key — that alone should stop the merge until the secret is removed from source and rotated. Beyond that, the class needs DI + repository-layer separation and minor style fixes.

---
Would you like me to post this as a review comment on PR #3? I won't post anything until you confirm.
