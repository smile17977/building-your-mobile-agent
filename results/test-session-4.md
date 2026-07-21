# Test session 4

 /review-pr 3 in https://github.com/nebius-academy-templates/mobile-pr-review-practice

I'll review PR #3 in that repository. Let me start by fetching the PR.

  Called github 3 times

PR #3 has one Kotlin file. Let me apply the review skills. I'll load the kotlin-conventions skill (.kt file trigger) and run the specialized reviewers in parallel.

⏺ Skill(kotlin-conventions)
Successfully loaded skill

⏺ 2 background agents launched (↓ to manage)
security-reviewer (Security review of PaymentService.kt)
architecture-reviewer (Architecture review of PaymentService.kt)

I have the kotlin-conventions loaded. The three reviewers are running in the background. I'll wait for their results before compiling the review.

✻ Waiting for 3 background agents to finish

⏺ Agent "Security review of PaymentService.kt" finished · 10s

Security reviewer done. Waiting on architecture and style reviewers.

✻ Waiting for 2 background agents to finish

⏺ Agent "Style review of PaymentService.kt" finished · 13s

Style reviewer done. Waiting on the architecture reviewer.

✻ Waiting for 1 background agent to finish

⏺ Agent "Architecture review of PaymentService.kt" finished · 27s

All three reviewers have completed. Here is the compiled review.

---
PR #3 Review — Add payment service

File reviewed: src/PaymentService.kt (new, +18)

▎ ⚠️ This PR introduces a live production credential in source code. This must be resolved before merge, and the leaked key should be treated as compromised and rotated immediately.

🔒 Security

- [HIGH] Hardcoded live API key — src/PaymentService.kt:8
val API_KEY = "sk-live-..." is a live (sk-live-) payment credential committed to source. It compiles into the APK and is now in git history — anyone with repo or binary access can extract it and charge real transactions. Rotate the key now, remove it from the code, and load it from a backend proxy, BuildConfig field, or the Android Keystore. Never route a live payment secret through the client.
- [HIGH] Missing TLS hardening — src/PaymentService.kt:10-13
The Retrofit client has no certificate pinning, no explicit TLS enforcement, and no timeouts, leaving the payment endpoint open to MITM. Add certificate pinning and timeout configuration.
- [MEDIUM] No input validation in charge() — src/PaymentService.kt:15
amount: Int and token: String are unvalidated — negative/zero amounts and empty/malformed tokens flow straight through. Validate amount > 0 and a non-empty, well-formed token.

🏗️ Architecture

- [HIGH] Direct Retrofit instantiation (no DI) — src/PaymentService.kt:10-13
The class builds its own Retrofit instance instead of receiving it via dependency injection. This tightly couples transport to the service and makes it unmockable in tests. Provide the client through DI (Hilt/Dagger).
- [HIGH] No repository abstraction — src/PaymentService.kt:6
Network transport and payment logic live in one class with no repository layer. Expected flow: ViewModel → PaymentRepository (interface) → PaymentService (data source).

🎨 Style (kotlin-conventions)

- [MEDIUM] API_KEY naming/const violation — src/PaymentService.kt:8
A class instance property named in UPPER_SNAKE_CASE. Instance properties use lowerCamelCase (apiKey); true constants belong in a companion object as private const val. (Moot once the key is removed per the security finding.)

📝 Other

- [LOW] charge() is an unimplemented stub — src/PaymentService.kt:15-17
The body is only a comment, so request signing, error handling, and response validation can't be assessed. Complete or mark clearly as WIP.

Summary: 4 HIGH, 2 MEDIUM, 1 LOW. The hardcoded live key is a blocker — do not merge as-is.

---
I have not posted anything. Would you like me to post this as a review comment on PR #3? I won't post until you confirm.