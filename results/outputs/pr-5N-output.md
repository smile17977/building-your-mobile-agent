PR #5 Review — "Add checkout flow"

Author: @ispaniuktripleten · Branch: pr-05-checkout-mixed · 2 files, +29

This PR touches a Kotlin ViewModel and a Swift view. Findings are grouped by category below.

🔒 Security

┌──────────┬─────────────────────────┬─────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Severity │        File:Line        │                             Finding                             │                                  Fix                                   │
├──────────┼─────────────────────────┼─────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ HIGH     │ CheckoutViewModel.kt:11 │ Hardcoded production API secret (sk-live-…) committed in        │ Move to BuildConfig/secure remote config; rotate the leaked key        │
│          │                         │ source.                                                         │ immediately.                                                           │
├──────────┼─────────────────────────┼─────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ HIGH     │ CheckoutViewModel.kt:16 │ Client secret transmitted in the request body from the client.  │ Remove client-side secret; authenticate the request server-side (or    │
│          │                         │ Server-side auth should hold the secret.                        │ via an auth header issued by the backend).                             │
└──────────┴─────────────────────────┴─────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘

🏛 Architecture

┌──────────┬─────────────────────────┬───────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Severity │        File:Line        │                                Finding                                │                               Fix                               │
├──────────┼─────────────────────────┼───────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ HIGH     │ CheckoutViewModel.kt:8  │ ViewModel depends on ApiClient directly, bypassing the repository     │ Inject a Repository/UseCase abstraction; ViewModel should not   │
│          │                         │ layer (MVVM/Repository violation).                                    │ know about the API client.                                      │
├──────────┼─────────────────────────┼───────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ HIGH     │ CheckoutViewModel.kt:15 │ GlobalScope.launch bypasses the ViewModel lifecycle — leaks and       │ Use viewModelScope.launch.                                      │
│          │                         │ unmanaged work.                                                       │                                                                 │
└──────────┴─────────────────────────┴───────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘

🎨 Style

┌──────────┬─────────────────────────┬──────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┐
│ Severity │        File:Line        │                                 Finding                                  │                             Fix                              │
├──────────┼─────────────────────────┼──────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ MEDIUM   │ CheckoutViewModel.kt:11 │ CLIENT_SECRET uses SCREAMING_SNAKE_CASE for a mutable property (reserved │ Rename to clientSecret, or make it a real const val in a     │
│          │                         │  for const val).                                                         │ companion object.                                            │
├──────────┼─────────────────────────┼──────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ MEDIUM   │ CouponView.swift:7      │ ApplyCoupon uses PascalCase; Swift methods should be lowerCamelCase.     │ Rename to applyCoupon.                                       │
├──────────┼─────────────────────────┼──────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
│ LOW      │ CouponView.swift:7      │ Completion-handler callback instead of modern async/await.               │ Refactor to func applyCoupon(code: String) async -> Bool.    │
└──────────┴─────────────────────────┴──────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘

Summary

- 2 HIGH security, 2 HIGH architecture, 2 MEDIUM + 1 LOW style.
- Top concern: a live API secret is hardcoded and shipped to the client — this needs to be rotated and removed before merge.
