---
PR #2 Review — Add profile screen

Author: @ispaniuktripleten · Branch: pr-02-profile-style → main · File: src/ProfileViewModel.swift (+14)

---
🏛 Architecture

┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Severity │                                                                              Finding                                                                               │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ HIGH     │ ViewModel calls URLSession directly. FetchProfile instantiates URLSession.shared.dataTask inside the ViewModel, coupling it to the network layer and breaking MVVM │
│          │  separation. Networking should sit behind a Repository.                                                                                                            │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ HIGH     │ No dependency injection. URLSession.shared is hardcoded, so the session/repository can't be mocked — the ViewModel is effectively untestable. Inject the           │
│          │ dependency through the initializer.                                                                                                                                │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM   │ UIKit vs. SwiftUI inconsistency. The comment notes the screen is "written in UIKit instead of SwiftUI," diverging from the presentation-layer convention. Needs a  │
│          │ clear justification or alignment.                                                                                                                                  │
└──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🔒 Security

┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Severity │                                                                              Finding                                                                               │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM   │ No input validation on id. id is passed straight into profileURL(id) with no nil/empty/malformed checks, risking malformed URLs or injection.                      │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM   │ Errors silently swallowed. The error from dataTask is discarded (_); network failures pass unnoticed and the caller can't distinguish "not found" from "request    │
│          │ failed."                                                                                                                                                           │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM   │ Unsafe response parsing. data.flatMap(Profile.init) parses raw network data with no validation of shape/content.                                                   │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Note     │ No hardcoded credentials and no insecure storage (UserDefaults/Keychain misuse) found.                                                                             │
└──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

🎨 Style

┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Severity │                                                                        Finding                                                                         │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM   │ Function name is PascalCase. func FetchProfile(...) should be fetchProfile(...) — Swift function names use lowerCamelCase (only types use PascalCase). │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM   │ Boolean lacks prefix. var loading should be var isLoading (use is/has/can/should).                                                                     │
├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ LOW      │ Completion handler over async/await. Prefer an async function returning Profile instead of @escaping callbacks (modernization).                        │
└──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

---
Summary: 2 HIGH (architecture), 6 MEDIUM (mixed), 1 LOW. Top concern is the ViewModel bypassing the repository pattern and DI — that's the blocker.

---
Per the review guardrails, I've recorded this to review history. Would you like me to post this as a comment on PR #2? I won't post anything until you confirm.

Let me append the history line now.
