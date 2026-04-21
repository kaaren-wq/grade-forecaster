import SwiftUI

struct HomeView: View {
    var body: some View {
        NavigationStack {
            ZStack {
                Image("home_bg")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
                    .overlay(Color.black.opacity(0.45))
                
                VStack(spacing: 24) {
                    Spacer()
                    
                    Text("Grade Calculator")
                        .font(.system(size: 38, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("Choose your university")
                        .font(.title3)
                        .foregroundColor(.white.opacity(0.9))
                    
                    NavigationLink {
                        UniversityCalculatorView(university: .tmu)
                    } label: {
                        homeButtonLabel("TMU")
                    }
                    
                    NavigationLink {
                        UniversityCalculatorView(university: .uoft)
                    } label: {
                        homeButtonLabel("UofT")
                    }
                    
                    NavigationLink {
                        UniversityCalculatorView(university: .york)
                    } label: {
                        homeButtonLabel("York University")
                    }
                    
                    Spacer()
                    
                    VStack(spacing: 6) {
                        Text("© 2026 Dejavu Group")
                        Text("Version 1.0.0")
                    }
                    .font(.footnote)
                    .foregroundColor(.white.opacity(0.8))
                    .padding(.bottom, 24)
                }
                .padding(.horizontal, 24)
            }
        }
    }
    
    @ViewBuilder
    private func homeButtonLabel(_ title: String) -> some View {
        Text(title)
            .font(.headline)
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 18)
            .background(
                RoundedRectangle(cornerRadius: 18)
                    .fill(Color.black.opacity(0.45))
                    .overlay(
                        RoundedRectangle(cornerRadius: 18)
                            .stroke(Color.white.opacity(0.12), lineWidth: 1)
                    )
            )
    }
}

#Preview {
    HomeView()
}
