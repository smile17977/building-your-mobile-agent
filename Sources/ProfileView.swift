import SwiftUI

struct ProfileView: View {
    let user: User
    @State private var isEditing = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                AvatarView(url: user.avatarURL)
                    .frame(width: 64, height: 64)
                VStack(alignment: .leading) {
                    Text(user.displayName)
                        .font(.title2)
                        .fontWeight(.semibold)
                    Text(user.email)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }
            Divider()
            if isEditing {
                EditProfileForm(user: user)
            } else {
                ProfileDetailList(user: user)
            }
        }
        .padding()
        .toolbar {
            Button(isEditing ? "Done" : "Edit") {
                isEditing.toggle()
            }
        }
    }
}
