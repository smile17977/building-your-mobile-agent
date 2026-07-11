import Foundation
import Combine

@MainActor
final class ProfileViewModel: ObservableObject {
    @Published private(set) var user: User?
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let userService: UserServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(userService: UserServiceProtocol) {
        self.userService = userService
    }

    func loadProfile(for userID: String) async {
        isLoading = true
        defer { isLoading = false }
        do {
            user = try await userService.fetchUser(id: userID)
        } catch {
            self.error = error
        }
    }

    func updateDisplayName(_ name: String) async {
        guard let current = user else { return }
        do {
            user = try await userService.updateUser(current, displayName: name)
        } catch {
            self.error = error
        }
    }
}
