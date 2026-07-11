---
name: kotlin-conventions
description: "Check kotlin conventions. File must name .kt as the load trigger"
---

## Rules

- Classes and objects use UpperCamelCase; functions, properties, and parameters use lowerCamelCase; top-level const and enum entries use UPPER_SNAKE_CASE. Booleans read as assertions (is, has, should). Avoid Hungarian notation and abbreviations.

- Launch coroutines in the correct scope (viewModelScope in a ViewModel, never GlobalScope). Do blocking or IO work on Dispatchers.IO, not the main thread. Make suspend functions main-safe and never block with runBlocking on the UI path. Respect structured concurrency so work is cancelled with its scope.

- Collect flows in a lifecycle-aware way (repeatOnLifecycle / flowWithLifecycle) so collection stops when the UI is not visible. Hold UI state in a ViewModel, not in the Activity/Fragment, and never leak Context/View references into a ViewModel. In Compose, respect recomposition and remember state correctly.

- Use Severity tags (HIGH / MEDIUM / LOW)

## Template

✅ Compliant
```kotlin
class UserProfile(
    val displayName: String,
    val isVerified: Boolean,
) {
    companion object {
        const val MAX_NAME_LENGTH = 50
    }

    fun fetchAvatar(): Uri? { ... }
}
```

❌ Non-compliant
```kotlin
class user_profile(
    val strDisplayName: String,   // abbreviation prefix + wrong style
    val verified: Boolean,        // boolean doesn't read as an assertion
) {
    val MaxNameLength = 50         // const-style value, wrong case, not const

    fun GetAvatar(): Uri? { ... }  // function should be lowerCamelCase
}
```

--

✅ Compliant
```kotlin
class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    fun loadProfile() {
        viewModelScope.launch {
            val profile = withContext(Dispatchers.IO) { repo.fetchProfile() }
            _uiState.value = UiState.Loaded(profile)
        }
    }
}
```

❌ Non-compliant
```kotlin
class ProfileViewModel(private val repo: ProfileRepository) : ViewModel() {
    fun loadProfile() {
        GlobalScope.launch {                 // escapes structured concurrency; leaks past ViewModel
            val profile = runBlocking { repo.fetchProfile() }  // blocks the thread
            _uiState.value = UiState.Loaded(profile)
        }
    }
}
```

--

✅ Compliant
```kotlin
class ProfileFragment : Fragment() {
    private val viewModel: ProfileViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { render(it) }
            }
        }
    }
}
```

❌ Non-compliant
```kotlin
class ProfileFragment : Fragment() {
    private val viewModel = ProfileViewModel(applicationContext)  // Context leaked into ViewModel

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            viewModel.uiState.collect { render(it) }  // collects even when stopped; keeps running in background
        }
    }
}
```


