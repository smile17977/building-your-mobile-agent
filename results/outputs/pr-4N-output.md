PR #4 Review — "Add trip list screen"

Repo: nebius-academy-templates/mobile-pr-review-practice
File changed: src/TripViewModel.kt (+22, new file)
Branch: pr-04-trip-repository-bypass

🏛 Architecture

[HIGH] ViewModel calls ApiClient directly — violates ADR-003 (Repository Pattern) — src/TripViewModel.kt:9-20
TripViewModel takes ApiClient in its constructor and calls apiClient.get() inside loadTrips(). ADR-003 requires ViewModels to obtain data exclusively through a repository and never reference ApiClient. The inline comment even acknowledges the bypass.never reference ApiClient. The inline comment even acknowledges the bypass.
→ Introduce a TripRepository that owns the API call; inject the repository into TripViewModel instead of ApiClient.

🔒 Security

[MEDIUM] No input validation / sanitization on userId — src/TripViewModel.kt:16
userId flows into the API path with no validation or encoding.

[MEDIUM] Unsafe URL construction — placeholder not interpolated — src/TripViewModel.kt:18
The path literal "/users/{userId}/trips" is passed verbatim; {userId} is never substituted with the parameter. Either the request is malformed, or substitution happens unsafely inside apiClient.get() without URL encoding (injection risk). Moving this into a repository with proper parameterization/encoding addresses both this and the finding above.

🎨 Style

[MEDIUM] Missing trailing newline — src/TripViewModel.kt:22 (EOF)
Kotlin convention requires files to end with a newline.

[LOW] Redundant "what" comment — src/TripViewModel.kt:17
The comment restates what the code does rather than why. (It's also flagging the architecture violation itself — resolving the HIGH finding removes the need for it.)

---
Top finding: HIGH — ViewModel bypasses repository pattern (calls ApiClient directly), violating ADR-003.