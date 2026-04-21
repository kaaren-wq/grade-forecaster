import Foundation

enum UniversityType: String, CaseIterable, Identifiable {
    case tmu = "TMU"
    case uoft = "UofT"
    case york = "York University"
    
    var id: String { rawValue }
}
