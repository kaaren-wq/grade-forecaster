import SwiftUI

struct YorkCalculatorView: View {
    @State private var showCelebration = false
    @State private var animateBalloons = false
    @State private var currentGrade: Double = 75
    @State private var finalWeight: Double = 30
    @State private var finalScore: Double = 70
    @State private var useManualCurrentGrade = true
    @State private var gradeItems: [GradeItem] = [
        GradeItem(),
        GradeItem(),
        GradeItem(),
        GradeItem(),
        GradeItem()
    ]
    
    var completedWeight: Double {
        gradeItems.compactMap { Double($0.weight) }.reduce(0, +)
    }

    var maxFinalWeight: Double {
        max(0, 100 - completedWeight)
    }
    
    var isAPlus: Bool {
        rounded >= 90
    }
    
    var courseworkContribution: Double {
        currentGrade * (100 - finalWeight) / 100
    }
    
    var examContribution: Double {
        finalScore * finalWeight / 100
    }
    
    var finalResult: Double {
        courseworkContribution + examContribution
    }
    
    var rounded: Int {
        Int((finalResult).rounded())
    }
    
    var letter: String {
        switch rounded {
        case 90...100: return "A+"
        case 85...89: return "A"
        case 80...84: return "A-"
        case 77...79: return "B+"
        case 73...76: return "B"
        case 70...72: return "B-"
        case 67...69: return "C+"
        case 63...66: return "C"
        case 60...62: return "C-"
        case 57...59: return "D+"
        case 53...56: return "D"
        case 50...52: return "D-"
        default: return "F"
        }
    }
    
    var gpa: String {
        switch rounded {
        case 90...100: return "4.00"
        case 85...89: return "3.90"
        case 80...84: return "3.70"
        case 77...79: return "3.30"
        case 73...76: return "3.00"
        case 70...72: return "2.70"
        case 67...69: return "2.30"
        case 63...66: return "2.00"
        case 60...62: return "1.70"
        case 57...59: return "1.30"
        case 53...56: return "1.00"
        case 50...52: return "0.70"
        default: return "0.00"
        }
    }
    var body: some View {
        ZStack {
            Image("YorkU_bg")
                .resizable()
                .scaledToFit()
                .ignoresSafeArea()
                .overlay(
                    LinearGradient(
                        colors: [
                            Color.black.opacity(0.55),
                            Color.black.opacity(0.35),
                            Color.black.opacity(0.60)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    .onChange(of: completedWeight) {
                        if finalWeight > maxFinalWeight {
                            finalWeight = maxFinalWeight
                        }
                    } )
            if showCelebration {
                BalloonOverlay(animate: $animateBalloons)
                    .transition(.opacity)
                    .allowsHitTesting(false)
            }
            
            ScrollView(showsIndicators: true) {
                VStack(spacing: 18) {
                    
                    heroCard
                    
                    HStack(spacing: 12) {
                        statCard(
                            title: "Projected Overall",
                            value: "\(rounded)%",
                            subtitle: "Rounded YorkU result"
                        )
                        
                        statCard(
                            title: "Letter Grade",
                            value: letter,
                            subtitle: "GPA \(gpa)"
                        )
                    }
                    
                    HStack(spacing: 12) {
                        statCard(
                            title: "Coursework",
                            value: String(format: "%.1f%%", courseworkContribution),
                            subtitle: "Before final exam"
                        )
                        
                        statCard(
                            title: "Exam Impact",
                            value: String(format: "%.1f%%", examContribution),
                            subtitle: "Added by final"
                        )
                    }
                    
                    calculatorCard
                    currentGradeInputCard
                    resultBreakdownCard
                    neededCard
                }
                .padding()
            }
        }
        .preferredColorScheme(.dark)
        .onChange(of: rounded) { _, newValue in
            if newValue >= 90 {
                showCelebration = true
                animateBalloons = true
                
                DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                    showCelebration = false
                    animateBalloons = false
                }
            }
        }
    }
    
    var heroCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    Text("YorkU Grade Calculator")
                        .font(.system(size: 30, weight: .bold))
                        .foregroundColor(.white)
                    
                    Text("Grade predictor for YorkU students")
                        .font(.subheadline)
                        .foregroundColor(.white.opacity(0.75))
                }
                
                Spacer()
                
                ZStack {
                    Circle()
                        .fill(Color.green.opacity(0.18))
                        .frame(width: 54, height: 54)
                    
                    Image(systemName: "chart.line.uptrend.xyaxis")
                        .font(.title2)
                        .foregroundColor(.green)
                }
            }
            
            HStack(spacing: 10) {
                tag("YorkU 4.33 GPA")
                tag("Live Sliders")
                tag("Final Predictor")
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 26)
                .fill(
                    LinearGradient(
                        colors: [
                            Color.white.opacity(0.08),
                            Color.green.opacity(0.10),
                            Color.blue.opacity(0.08)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 26)
                        .stroke(Color.white.opacity(0.08), lineWidth: 1)
                )
        )
    }
    
    var currentGradeInputCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Toggle("I know my current grade", isOn: $useManualCurrentGrade)
                .foregroundColor(.white)

            if !useManualCurrentGrade {
                VStack(spacing: 10) {
                    ForEach($gradeItems) { $item in
                        HStack {
                            TextField("Name", text: $item.name)
                            TextField("Grade", text: $item.grade)
                            TextField("Weight", text: $item.weight)
                        }
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                }
            }
        }
        .padding(20)
        .background(cardBackground)
    }
    
    var calculatorCard: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Final Exam Simulator")
                .font(.title3.bold())
                .foregroundColor(.white)
            
            if useManualCurrentGrade {
                sliderBlock(
                    title: "Current Grade",
                    value: currentGrade,
                    color: .green
                ) {
                    Slider(value: $currentGrade, in: 0...100)
                        .tint(.green)
                }
            } else {
                VStack(alignment: .leading, spacing: 10) {
                    HStack {
                        Text("Calculated Current Grade")
                            .foregroundColor(.white)
                        Spacer()
                        Text(String(format: "%.1f%%", effectiveCurrentGrade))
                            .foregroundColor(.green)
                            .fontWeight(.bold)
                    }
                    
                    Text("Based on your assignment and exam entries")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.65))
                }
            }
            
            sliderBlock(
                title: "Final Weight",
                value: finalWeight,
                color: .blue
            ) {
                Slider(value: $finalWeight, in: 0...maxFinalWeight)
                    .tint(.blue)
            }
            Text("Available remaining weight: \(Int(maxFinalWeight))%")
                .font(.caption)
                .foregroundColor(.white.opacity(0.65))
            sliderBlock(
                title: "Final Exam Score",
                value: finalScore,
                color: .mint
            ) {
                Slider(value: $finalScore, in: 0...100)
                    .tint(.mint)
            }
        }
        .padding(20)
        .background(cardBackground)
    }
    
    var resultBreakdownCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Grade Build")
                .font(.title3.bold())
                .foregroundColor(.white)
            
            VStack(alignment: .leading, spacing: 10) {
                Text("Current + Final Contribution")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.72))
                
                GeometryReader { geo in
                    let totalWidth = geo.size.width
                    let courseWidth = totalWidth * CGFloat(courseworkContribution / 100)
                    let examWidth = totalWidth * CGFloat(examContribution / 100)
                    
                    HStack(spacing: 0) {
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color.green.opacity(0.8))
                            .frame(width: max(courseWidth, 6))
                        
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color.blue.opacity(0.85))
                            .frame(width: max(examWidth, 6))
                    }
                    .frame(height: 28)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .fill(Color.white.opacity(0.06))
                    )
                }
                .frame(height: 28)
                
                HStack {
                    Label("Coursework", systemImage: "square.fill")
                        .foregroundColor(.green)
                    Spacer()
                    Text(String(format: "%.1f%%", courseworkContribution))
                        .foregroundColor(.white)
                }
                
                HStack {
                    Label("Final Exam", systemImage: "square.fill")
                        .foregroundColor(.blue)
                    Spacer()
                    Text(String(format: "+%.1f%%", examContribution))
                        .foregroundColor(.white)
                }
            }
        }
        .padding(20)
        .background(cardBackground)
    }
    
    var neededCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Needed on Final")
                .font(.title3.bold())
                .foregroundColor(.white)
            
            HStack(spacing: 12) {
                neededMiniCard(title: "Pass", score: neededFor(target: 50))
                neededMiniCard(title: "C+", score: neededFor(target: 67))
            }
            
            HStack(spacing: 12) {
                neededMiniCard(title: "A-", score: neededFor(target: 80))
                neededMiniCard(title: "A+", score: neededFor(target: 90))
            }
        }
        .padding(20)
        .background(cardBackground)
    }
    
    func statCard(title: String, value: String, subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased())
                .font(.caption)
                .foregroundColor(.white.opacity(0.55))
            
            Text(value)
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(.white)
            
            Text(subtitle)
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.72))
        }
        .frame(maxWidth: .infinity, minHeight: 120, alignment: .leading)
        .padding(18)
        .background(cardBackground)
    }
    
    func sliderBlock<Content: View>(title: String, value: Double, color: Color, @ViewBuilder slider: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(title)
                    .foregroundColor(.white)
                Spacer()
                Text("\(Int(value))%")
                    .foregroundColor(color)
                    .fontWeight(.bold)
            }
            slider()
        }
    }
    
    func neededMiniCard(title: String, score: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundColor(.white.opacity(0.6))
            Text(score)
                .font(.title3.bold())
                .foregroundColor(.white)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 18)
                .fill(Color.white.opacity(0.05))
        )
    }
    
    func tag(_ text: String) -> some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .foregroundColor(.white.opacity(0.92))
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                Capsule()
                    .fill(Color.white.opacity(0.08))
            )
    }
    
    var cardBackground: some View {
        RoundedRectangle(cornerRadius: 24)
            .fill(Color.white.opacity(0.06))
            .overlay(
                RoundedRectangle(cornerRadius: 24)
                    .stroke(Color.white.opacity(0.06), lineWidth: 1)
            )
    }
    
    func neededFor(target: Double) -> String {
        guard finalWeight > 0 else { return "N/A" }
        
        // Scan from 0.0 to 100.0 in 0.1% steps
        for step in 0...1000 {
            let examScore = Double(step) / 10.0
            let overall = courseworkContribution + (examScore * finalWeight / 100)
            let roundedOverall = Int(overall.rounded())
            
            if Double(roundedOverall) >= target {
                return String(format: "%.1f%%", examScore)
            }
        }
        
        return "Impossible"
    }
    
    func gradeToPercent(_ input: String) -> Double? {
        let trimmed = input.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()

        if let value = Double(trimmed) {
            return value
        }

        switch trimmed {
        case "A+": return 95
        case "A": return 87
        case "A-": return 82
        case "B+": return 78
        case "B": return 75
        case "B-": return 71
        case "C+": return 68
        case "C": return 65
        case "C-": return 61
        case "D+": return 58
        case "D": return 55
        case "D-": return 51
        case "F": return 25
        default: return nil
        }
    }

    func calculatedCurrentGrade(from items: [GradeItem]) -> Double {
        var totalEarned = 0.0
        var totalWeight = 0.0

        for item in items {
            guard
                let percent = gradeToPercent(item.grade),
                let weight = Double(item.weight),
                weight > 0
            else { continue }

            totalEarned += percent * weight
            totalWeight += weight
        }

        guard totalWeight > 0 else { return 0 }
        return totalEarned / totalWeight
    }

    var effectiveCurrentGrade: Double {
        useManualCurrentGrade
            ? currentGrade
            : calculatedCurrentGrade(from: gradeItems)
    }
    struct BalloonOverlay: View {
        @Binding var animate: Bool
        
        let balloons = ["🎈","🎈","🎈","🎉","🎊","🎈","🎈"]
        
        var body: some View {
            GeometryReader { geo in
                ZStack {
                    ForEach(0..<balloons.count, id: \.self) { index in
                        Text(balloons[index])
                            .font(.system(size: CGFloat(40 + index * 3)))
                            .position(
                                x: CGFloat(50 + index * 45),
                                y: animate ? -80 : geo.size.height + CGFloat(index * 60)
                            )
                            .animation(
                                .easeOut(duration: Double(2 + index % 3)),
                                value: animate
                            )
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
    }
    struct GradeItem: Identifiable {
        let id = UUID()
        var name: String = ""
        var grade: String = ""
        var weight: String = ""
    }
}
#Preview {
    YorkCalculatorView()
}
