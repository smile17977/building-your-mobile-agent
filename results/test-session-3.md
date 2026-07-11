# Test session 3

Review the Swift files in PR #2 https://github.com/nebius-academy-templates/mobile-pr-review-practice for style issues.
1 skill available

I'm PR Review Agent. Let me load the Swift conventions skill and pull PR #2.

⏺ Skill(swift-conventions)
Successfully loaded skill

The skill has the Swift conventions I drafted earlier baked in. Let me pull the PR.

  Ran 1 shell command

One Swift file changed. Let me get the actual diff to review the code.

  Ran 1 shell command

```swift
import UIKit

class ProfileViewModel {
    var loading = false

    func FetchProfile(id: String, completion: @escaping (Profile?) -> Void) {
        let url = URL(string: "https://api.example.com/profiles/\(id)")!
        URLSession.shared.dataTask(with: url) { data, _, _ in
            let profile = try? JSONDecoder().decode(Profile.self, from: data!)
            completion(profile)
        }.resume()
    }
}
```

Reviewing src/ProfileViewModel.swift against the Swift conventions (naming, concurrency, UIKit/SwiftUI) and the project's MVVM/security criteria.

---
Conclusion

Needs work. The single added file has multiple style violations spanning naming, concurrency, MVVM, and UIKit/SwiftUI usage. None are blocking-critical security issues, but the concurrency and MVVM findings are HIGH severity and should be fixed before merge.

---
Findings

🔴 HIGH — ProfileViewModel.swift:9 — Function FetchProfile uses UpperCamelCase. Methods must be lowerCamelCase. → Rename to fetchProfile.

🔴 HIGH — ProfileViewModel.swift:9-13 — Uses a completion handler instead of async/await. → Convert to func fetchProfile(id: String) async throws -> Profile? and await the URLSession call.

🔴 HIGH — ProfileViewModel.swift:4 — ViewModel is not marked @MainActor and does not conform to ObservableObject. Per MVVM guidelines, a ViewModel must be @MainActor + ObservableObject. UI state updated from the URLSession callback will land off the main thread. → Add @MainActor final class ProfileViewModel: ObservableObject.

🟡 MEDIUM — ProfileViewModel.swift:6 — var loading is a Boolean that doesn't read as an assertion. → Rename to isLoading. Also, if it drives the UI it should be @Published private(set) var isLoading.

🟡 MEDIUM — ProfileViewModel.swift:1,4 — Imports UIKit for a new profile screen; the guideline is SwiftUI-first, and a ViewModel should not depend on UIKit at all. → Import Foundation (and use SwiftUI for the view layer) instead of UIKit.

🟢 LOW — ProfileViewModel.swift:11 — Network errors are silently discarded (data, _, _ ignores the error and response). → Surface errors rather than swallowing them, especially once converted to async throws.

---
Summary

ProfileViewModel.swift (14 lines added) has 6 findings: 3 HIGH (method naming, completion-handler vs async/await, missing @MainActor/ObservableObject), 2 MEDIUM (Boolean naming/@Published, UIKit dependency), and 1 LOW (swallowed errors). Recommend addressing the HIGH findings before merge.

I have not posted this anywhere. Would you like me to post it as a review comment on PR #2? If so, I'll restate and confirm with you before posting.

✻ Sautéed for 23s

❯ Review the Kotlin files in PR #4 from https://github.com/nebius-academy-templates/mobile-pr-review-practice for style issues.

I'm PR Review Agent. Let me load the Kotlin conventions skill and pull PR #4.

⏺ Skill(kotlin-conventions)
Successfully loaded skill

The skill now has the content I drafted earlier baked in. Let me pull PR #4.

  Ran 1 shell command

```kotlin
class TripViewModel(private val apiClient: ApiClient) : ViewModel() {

    private val _trips = MutableStateFlow<List<Trip>>(emptyList())
    val trips: StateFlow<List<Trip>> = _trips

    fun loadTrips(userId: String) {
        viewModelScope.launch {
            _trips.value = apiClient.get("/users/{userId}/trips")
        }
    }
}
```

Reviewing src/TripViewModel.kt against the Kotlin conventions (naming, coroutines, Jetpack/lifecycle) plus the project's MVVM/security criteria.

---
Conclusion

Needs work. The file is close to correct — scope and StateFlow usage are right — but there are a few style/architecture issues worth fixing before merge. Nothing is a critical security defect.

---
Findings

🟡 MEDIUM — TripViewModel.kt:19 — IO work runs on the default (main) dispatcher. apiClient.get(...) is a network call launched in viewModelScope.launch { } without withContext(Dispatchers.IO), so it runs on Dispatchers.Main. → Wrap the call: _trips.value = withContext(Dispatchers.IO) { apiClient.get(...) }.

🟡 MEDIUM — TripViewModel.kt:19 — ViewModel calls the API client directly instead of going through a repository (also flagged in the diff comment). This violates the MVVM/repository separation. → Inject a TripRepository and call it from the ViewModel.

🟡 MEDIUM — TripViewModel.kt:19 — The path string uses a literal "{userId}" placeholder that is never substituted, so userId is unused and every request hits the same malformed path. → Interpolate: apiClient.get("/users/$userId/trips").

🟢 LOW — TripViewModel.kt:16-20 — No error handling around the network call; a thrown exception will propagate and there's no error state for the UI. → Wrap in try/catch and expose an error/loading state.

🟢 LOW — TripViewModel.kt:14 — val trips exposes the backing flow directly. Consider .asStateFlow() for a clearer read-only contract: val trips: StateFlow<List<Trip>> = _trips.asStateFlow().

---
Summary

TripViewModel.kt (22 lines added) has 5 findings: 3 MEDIUM (IO off the main dispatcher, direct API call bypassing a repository, unsubstituted userId path placeholder) and 2 LOW (missing error handling, expose flow via asStateFlow()). Naming, coroutine scope (viewModelScope), and StateFlow backing-field pattern are all correct. Recommend addressing the MEDIUM findings before merge.

I have not posted this anywhere. Want me to post it as a review comment on PR #4? If so, I'll restate and confirm with you before posting.

✻ Sautéed for 21s

❯ /review-pr 1

I'm PR Review Agent. Running the review-pr flow for PR #1. Let me fetch it and its diff.

  Ran 1 shell command

```swift
import SwiftUI

@MainActor
final class RideHistoryViewModel: ObservableObject {
    @Published var rides: [Ride] = []
    @Published var isLoading = false

    private let repository: RideRepository

    init(repository: RideRepository) {
        self.repository = repository
    }

    func loadRides() async {
        isLoading = true
        defer { isLoading = false }
        rides = (try? await repository.recentRides()) ?? []
    }
}
```

This is a Swift file, so I'm applying the swift-conventions skill (naming, concurrency, UIKit/SwiftUI) plus security checks. This one is notably cleaner than #2.

---
Conclusion

Recommended to merge (with two LOW-severity polish suggestions). The file follows the conventions well: @MainActor + ObservableObject ViewModel, @Published state, proper async/await, dependency-injected repository, and SwiftUI-first (no UIKit). No security issues.

---
Findings

🟢 LOW — RideHistoryViewModel.swift:6 — @Published var isLoading and var rides are publicly settable. Per MVVM guidelines, expose UI state as read-only to the view. → Mark them @Published private(set) var.

🟢 LOW — RideHistoryViewModel.swift:17 — try? silently swallows any error from recentRides(); a load failure is indistinguishable from an empty result. → Consider a catch that surfaces an error state to the UI instead of collapsing to [].

---
Summary

RideHistoryViewModel.swift (19 lines added) has 2 LOW findings: publicly settable @Published properties (should be private(set)) and a swallowed error via try?. Naming, concurrency (async/await, @MainActor), and SwiftUI usage are all correct. No security concerns. Recommended to merge.

I have not posted this anywhere. Want me to post it as a review comment on PR #1? Reply "yes" or "post" and I'll restate and confirm before posting.

✻ Crunched for 14s

❯ no

Understood — I won't post anything. Let me know if you'd like anything else.
