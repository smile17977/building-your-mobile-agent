# Test session 4

  /review-pr 3 in https://github.com/nebius-academy-templates/mobile-pr-review-practice

I'll review PR #3. Let me start by fetching the PR details.

  Called github 2 times

PR #3 has changes (18 additions in src/PaymentService.kt), so it's not empty. Now let me delegate to the three reviewers concurrently.

⏺ 3 agents finished
style-reviewer (Style review of PaymentService.kt) · 4 tool uses · 4.7k tokens
⎿  Done
security-reviewer (Security review of PaymentService.kt) · 1 tool use · 3.2k tokens
⎿  Done
architecture-reviewer (Architecture review of PaymentService.kt) · 4 tool uses · 4.6k tokens
⎿  Done

⏺ All three reviewers have reported. Here is the compiled review.

  ---
  PR Review — #3: Add payment service

  Repo: nebius-academy-templates/mobile-pr-review-practice
  File changed: src/PaymentService.kt (+18)
  Author: @ispaniuktripleten

  ---
  🔴 Security

  - [HIGH] Hardcoded live API key (line 8) — val API_KEY = "sk-live-..." embeds a production secret in source. It will land in Git history and be extractable from the compiled APK. This is the blocking issue. Move it to secure config (e.g. BuildConfig sourced from an untracked properties file / secrets manager) and rotate the exposed key immediately, since it's now been committed.
  - [MEDIUM] No input validation in charge() (line 15) — amount and token are used unvalidated. Add require(amount > 0) and require(token.isNotBlank()).
- [MEDIUM] No input validation in charge() (line 15) — amount and token are used unvalidated. Add require(amount > 0) and require(token.isNotBlank()).
- [MEDIUM] Key transmitted on every request (line 16) — the key is held in memory and sent in the Authorization header on each call; compounds the hardcoding risk.

🟠 Architecture

- [HIGH] Direct Retrofit instantiation (lines 10–13) — the HTTP client is built inside the class, blocking DI and testability. Inject the Retrofit/API interface instead.
- [HIGH] Missing repository layer — PaymentService implements networking directly; per MVVM it should sit behind a repository that ViewModels depend on.
- [LOW] No result/error abstraction (charge() returns Unit) — return a Result type or use coroutines/Flow so ViewModels can manage state.

🟡 Style

- [MEDIUM] API_KEY placement/modifier (line 8) — an instance val in UPPER_SNAKE_CASE. Constants belong in a companion object as const val (though per the security finding, it shouldn't be a source-level constant at all).
- [LOW] Blank line after class opening brace (line 7) — non-standard formatting.

---
Summary

This PR should not be merged as-is. The hardcoded live payment API key is a critical, must-fix issue (rotate + remove), and the class also needs restructuring for DI/repository pattern and input validation.

---
Would you like me to post this as a comment on PR #3? I won't post anything until you confirm.