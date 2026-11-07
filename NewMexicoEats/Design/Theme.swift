import SwiftUI
import UIKit
import CoreText

/// New Mexico palette, "Christmas" (red and green chile, provisional, 2026-11-06; Nick decides, playbook/05-naming.md), light only,
/// from state-prompts/NEW_MEXICO_PROMPT.md, with no Zia symbol and no team colors: chile red #8C1D18 (9.1:1 on white) for titles, tint
/// and accents; green chile #3F6B22 (white on it 6.3:1) for the hand-checked guide cards; turquoise #0E7C86 (white on it 4.9:1) for
/// honors chips; chile yellow #FFD700 only as a pin and card fill under chile-red text; adobe #FAF4E6 pages. The names `green`/`gold`
/// are kept from Wisconsin Eats so the shared views read the same; here `green` is chile red and `gold` is green chile.
enum Theme {
    static let green = Color(hex: 0x8C1D18)      // chile red: titles, tint, primary text accents
    static let green2 = Color(hex: 0xA8392F)
    static let gold = Color(hex: 0x3F6B22)       // green chile: card fills under white text
    static let goldSoft = Color(hex: 0xDDE8D2)   // soft green
    static let lime = Color(hex: 0xFFD700)       // chile yellow, fills only (hand-checked pins, the title shadow), under chile-red text
    static let limeSoft = Color(hex: 0xFFF4C2)
    static let sand = Color(hex: 0xFAF4E6)       // the Home background, adobe
    static let red = Color(hex: 0x0E7C86)        // honors chips, turquoise
    static let sandstone = Color(hex: 0x2E5019)  // a darker green chile (9.6:1 on white)
    static let teal = Color(hex: 0x0A5F66)       // a darker turquoise (7.2:1 on white)
    static let ink = Color(hex: 0x1A1A1A)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xF1EEE6)
    static let surface3 = Color(hex: 0xE4DFD3)
    static let rule = Color(hex: 0xE4DFD3)
    static let rule2 = Color(hex: 0xCCC4B3)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// New Mexico Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: the Sandia Mountains' long ridge in chile red, steep on the west, over a green-chile and a chile-red stripe ("red
/// or green?"). No Zia sun symbol (Zia Pueblo holds it sacred).
struct Stripes: View {
    var height: CGFloat = 6

    /// (x, rise) along the ridge: 0 is the stripes' top, 1 the band's top
    static let ridge: [(CGFloat, CGFloat)] = [(0, 0.10), (0.12, 0.16), (0.30, 0.22), (0.42, 0.62), (0.47, 0.92), (0.53, 1.0), (0.60, 0.86),
                                              (0.70, 0.70), (0.82, 0.48), (1, 0.30)]

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, base = h * 0.62, stripe = (h - base) / 2
            var p = Path()
            p.move(to: CGPoint(x: 0, y: base))
            for (x, rise) in Self.ridge { p.addLine(to: CGPoint(x: x * w, y: base - base * rise)) }
            p.addLine(to: CGPoint(x: w, y: base)); p.closeSubpath()
            ctx.fill(p, with: .color(Theme.green))
            ctx.fill(Path(CGRect(x: 0, y: base, width: w, height: stripe)), with: .color(Theme.gold))
            ctx.fill(Path(CGRect(x: 0, y: base + stripe, width: w, height: stripe)), with: .color(Theme.green))
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
