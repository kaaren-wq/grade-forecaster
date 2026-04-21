import SwiftUI

enum University {
    case tmu
    case uoft
    case york
}

struct UniversityCalculatorView: View {
    
    var university: University
    
    var body: some View {
        ZStack {
            // Background
            Image("toronto")
                .resizable()
                .scaledToFit()
                .ignoresSafeArea()
            
            Color.black.opacity(0.7)
                .ignoresSafeArea()
            
            VStack {
                
                // Top bar (back + menu)
                HStack {
                    
                    // Back button
                    NavigationLink(destination: HomeView()) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.white.opacity(0.1))
                            .clipShape(Circle())
                    }
                    
                    Spacer()
                    
                    // Menu button (for future dropdown)
                    Menu {
                        NavigationLink("Home", destination: HomeView())
                        NavigationLink("TMU", destination: UniversityCalculatorView(university: .tmu))
                        NavigationLink("UofT", destination: UniversityCalculatorView(university: .uoft))
                        NavigationLink("York", destination: UniversityCalculatorView(university: .york))
                    } label: {
                        Image(systemName: "line.3.horizontal")
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.white.opacity(0.1))
                            .clipShape(Circle())
                    }
                }
                .padding(.horizontal)
                .padding(.top, 20)
                
                Spacer()
                
                // TITLE
                Text(titleText)
                    .font(.largeTitle.bold())
                    .foregroundColor(.white)
                
                Spacer()
                
                // SWITCH BETWEEN CALCULATORS
                if university == .tmu {
                    ContentView()
                } else if university == .uoft {
                    UofTCalculatorView()
                } else {
                    YorkCalculatorView()
                }
                
                Spacer()
            }
        }
    }
    
    // Dynamic title
    var titleText: String {
        switch university {
        case .tmu:
            return "TMU"
        case .uoft:
            return "UofT"
        case .york:
            return "York"
        }
    }
}

#Preview {
    UniversityCalculatorView(university: .tmu)
}
