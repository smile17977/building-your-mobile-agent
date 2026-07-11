---
name: swift-conventions
description: "Check swift conventions. The file must name .swift as the load trigger"
---

<!--
TODO: Swift conventions knowledge skill.
- Description: load only when reviewing Swift code (name .swift).
- Body: at least three rules covering naming, concurrency (async/await), and UIKit/SwiftUI.
- Template: one compliant and one non-compliant Swift snippet.
-->

## Rules
- Types use UpperCamelCase; properties, functions, and cases use lowerCamelCase. Names should be descriptive and avoid abbreviations. Booleans read as assertions (is, has, should). Don't prefix types with NS/My or restate the type in the name.
- Use async/await rather than nested completion handlers. Never block a thread with a semaphore to await async work. UI state must be updated on the main actor — mark UI-facing types or methods @MainActor instead of manually hopping with DispatchQueue.main.async.
- In SwiftUI, keep views small and declarative: decompose large body blocks into subviews, place each view modifier on its own line, and drive state with the correct property wrapper (@State for local value state, @StateObject for owned reference models, @ObservedObject for injected ones). Don't reach into UIKit (UIApplication, manual frame math) when a SwiftUI-native API exists.

## Template

✅ Compliant
struct UserProfile {
    let displayName: String
    var isVerified: Bool

    func fetchAvatar() -> URL? { ... }
}

❌ Non-compliant
struct user_profile {          // wrong case for a type
    let str_DisplayName: String // abbreviation + inconsistent case
    var verified: Bool          // boolean doesn't read as an assertion

    func GetAvatarURL() -> URL? { ... } // method should be lowerCamelCase
}

--

✅ Compliant
@MainActor
func loadProfile() async {
    do {
        let profile = try await service.fetchProfile()
        self.profile = profile        // already on the main actor
    } catch {
        self.errorMessage = error.localizedDescription
    }
}

❌ Non-compliant
func loadProfile() {
    let semaphore = DispatchSemaphore(value: 0)   // blocks the thread
    service.fetchProfile { result in
        DispatchQueue.main.async {                // manual hop, easy to forget
            self.profile = try? result.get()
        }
        semaphore.signal()
    }
    semaphore.wait()
}

--


✅ Compliant
struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()

    var body: some View {
        VStack(spacing: 12) {
            AvatarView(url: viewModel.avatarURL)
            NameLabel(name: viewModel.displayName)
        }
        .padding()
        .task { await viewModel.load() }
    }
}

❌ Non-compliant
struct ProfileView: View {
    @ObservedObject var viewModel = ProfileViewModel()  // recreated on redraw; should be @StateObject

    var body: some View {
        VStack { AvatarView(url: viewModel.avatarURL); NameLabel(name: viewModel.displayName) }.padding().onAppear { DispatchQueue.main.async { UIApplication.shared.windows.first?.endEditing(true) } }  // cramped, UIKit reach-in, modifiers not on new lines
    }
}
