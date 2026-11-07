import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, chileburgers, burritos, treasures, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // Albuquerque's Old Town Plaza, so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 35.0961, longitude: -106.6697)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Frontier", "Albuquerque"), pick("Mary & Tito's Cafe", "Albuquerque"), pick("The Owl Bar & Cafe", "San Antonio")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "chileburgers": open(.chileBurgers)
        case "burritos": open(.burritos)
        case "treasures": open(.treasures)
        case "honors":
            // Santa Fe's Plaza, among the MICHELIN places
            model.screenshotLocation = CLLocation(latitude: 35.6870, longitude: -105.9378)
            open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Mary & Tito's: a Culinary Treasure with its 1963 founding year, America's Classics and its note
            open(.treasures)
            if let p = pick("Mary & Tito's Cafe", "Albuquerque") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("Frontier", "Albuquerque")
        case "chileburgers": pick("Bob's Burgers", "Albuquerque")
        case "burritos": pick("Frontier", "Albuquerque")
        case "treasures": pick("Mary & Tito's Cafe", "Albuquerque")
        case "map": pick("Frontier", "Albuquerque")
        case "honors": pick("La Choza", "Santa Fe")
        case "oldest": pick("El Farol", "Santa Fe")
        case "saved": pick("Mary & Tito's Cafe", "Albuquerque")
        case "about": nil
        default: pick("Frontier", "Albuquerque")
        }
        model.selectedPlace = place
    }
}
