// New Mexico Eats brand (provisional, 2026-11-06; Nick picks the name, icon and palette): the app icon is concept A of
// scripts/icon-concepts.swift, a ripe red chile pod with its stem, on turquoise (not green: Colorado Eats' icon is a green chile); the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No Zia sun symbol (Zia Pueblo holds it sacred), no state flag, no team marks.
// Usage, from nm-eats/: swift scripts/make-brand.swift   -> NewMexicoEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}

let TURQ: UInt32 = 0x0E7C86, CHILERED: UInt32 = 0x8C1D18, ADOBE: UInt32 = 0xFAF4E6, GREEN: UInt32 = 0x3F6B22, YELLOW: UInt32 = 0xFFD700
let POD: UInt32 = 0xC2301F, PODTOP: UInt32 = 0xE0563F, CALYX: UInt32 = 0x4E7A24, STEM: UInt32 = 0xC9B27A

/// The red chile pod (concept A of icon-concepts.swift; keep the two identical). CoreGraphics y-up, s = canvas size.
func chile(_ c: CGContext, _ s: CGFloat) {
    func P(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x * s, y: y * s) }
    c.saveGState(); defer { c.restoreGState() }
    c.translateBy(x: s / 2, y: s / 2); c.scaleBy(x: 0.95, y: 0.95); c.translateBy(x: -s / 2, y: -s / 2)   // within the 0.68-0.74 band
    // the pod: a long, gently curved body, its stem end rounded on the left and its tip curling down at the right
    let pod = CGMutablePath()
    pod.move(to: P(0.26, 0.60))
    pod.addCurve(to: P(0.80, 0.52), control1: P(0.42, 0.70), control2: P(0.66, 0.66))
    pod.addQuadCurve(to: P(0.86, 0.30), control: P(0.92, 0.42))
    pod.addCurve(to: P(0.26, 0.38), control1: P(0.70, 0.36), control2: P(0.44, 0.28))
    pod.addQuadCurve(to: P(0.26, 0.60), control: P(0.18, 0.49))
    pod.closeSubpath()
    c.setFillColor(rgb(POD)); c.addPath(pod); c.fillPath()
    // the lighter top plane
    let top = CGMutablePath()
    top.move(to: P(0.30, 0.59))
    top.addCurve(to: P(0.76, 0.54), control1: P(0.44, 0.67), control2: P(0.64, 0.63))
    top.addCurve(to: P(0.30, 0.53), control1: P(0.62, 0.58), control2: P(0.44, 0.60))
    top.closeSubpath()
    c.setFillColor(rgb(PODTOP)); c.addPath(top); c.fillPath()
    // the calyx cap and the stem
    c.setFillColor(rgb(CALYX))
    c.addPath(CGPath(roundedRect: CGRect(x: 0.18 * s, y: 0.41 * s, width: 0.10 * s, height: 0.17 * s), cornerWidth: 0.04 * s, cornerHeight: 0.04 * s, transform: nil))
    c.fillPath()
    c.setStrokeColor(rgb(STEM)); c.setLineWidth(0.045 * s); c.setLineCap(.round)
    c.move(to: P(0.20, 0.53)); c.addQuadCurve(to: P(0.15, 0.68), control: P(0.13, 0.58)); c.strokePath()
}


func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(TURQ)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    chile(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "NewMexicoEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): turquoise, the chile at the left, the name and tagline at the right, and the app's header band along
/// the bottom: the Sandia Mountains' ridge in chile red over a green-chile and a chile-red stripe, on adobe (Theme.swift's Stripes).
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(TURQ)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    let band: CGFloat = 70, stripe: CGFloat = 10
    ctx.setFillColor(rgb(ADOBE)); ctx.fill(CGRect(x: 0, y: 0, width: CGFloat(W), height: band))
    let ridge: [(CGFloat, CGFloat)] = [(0, 0.10), (0.12, 0.16), (0.30, 0.22), (0.42, 0.62), (0.47, 0.92), (0.53, 1.0), (0.60, 0.86),
                                       (0.70, 0.70), (0.82, 0.48), (1, 0.30)]
    let base = 2 * stripe
    let rp = CGMutablePath(); rp.move(to: CGPoint(x: 0, y: base))
    for (x, r) in ridge { rp.addLine(to: CGPoint(x: x * CGFloat(W), y: base + (band - base) * r)) }
    rp.addLine(to: CGPoint(x: CGFloat(W), y: base)); rp.closeSubpath()
    ctx.setFillColor(rgb(CHILERED)); ctx.addPath(rp); ctx.fillPath()
    ctx.setFillColor(rgb(GREEN)); ctx.fill(CGRect(x: 0, y: stripe, width: CGFloat(W), height: stripe))
    ctx.setFillColor(rgb(CHILERED)); ctx.fill(CGRect(x: 0, y: 0, width: CGFloat(W), height: stripe))
    ctx.saveGState(); ctx.translateBy(x: 40, y: 90); chile(ctx, 500); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 80) ?? NSFont.boldSystemFont(ofSize: 70)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 34) ?? NSFont.boldSystemFont(ofSize: 30)
    NSAttributedString(string: "NEW MEXICO", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 380))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 296))
    NSAttributedString(string: "GREEN CHILE, BURRITOS & MORE", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 1.0, green: 0.843, blue: 0.0, alpha: 1)]).draw(at: NSPoint(x: 564, y: 246))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
