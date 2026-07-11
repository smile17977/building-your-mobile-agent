import XCTest
@testable import MobileApp

final class ProfileViewModelTests: XCTestCase {
    private var sut: ProfileViewModel!
    private var mockService: MockUserService!

    override func setUp() {
        super.setUp()
        mockService = MockUserService()
        sut = ProfileViewModel(userService: mockService)
    }

    override func tearDown() {
        sut = nil
        mockService = nil
        super.tearDown()
    }

    func testLoadProfileSetsUser() async {
        mockService.stubbedUser = User.fixture()
        await sut.loadProfile(for: "user-123")
        XCTAssertNotNil(sut.user)
    }

    func testLoadProfileSetsErrorOnFailure() async {
        mockService.shouldThrow = true
        await sut.loadProfile(for: "user-123")
        XCTAssertNotNil(sut.error)
    }
}
