// New Mexico Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on a plain background in the state's colours (the palette in Design/Theme.swift), no backing shape, no text or texture,
// no Zia sun symbol (Zia Pueblo holds it sacred) and no team marks.
//   A  a ripe red chile pod with its stem, side view, on turquoise #0E7C86: pod #C2301F with a lighter top #E0563F, calyx #4E7A24,
//      stem #C9B27A (red, not green: Colorado Eats' icon is a green chile pod on navy)
//   B  a puffed sopaipilla with a honey drizzle, on turquoise #0E7C86: pastry #E2B05A with a lighter top #F1CE8A, honey #B0720F
//   C  a breakfast burrito smothered "Christmas" (red and green chile), on adobe #F3E3C3: tortilla #E9CF98 with a lighter top #F4E2BB,
//      red chile #A8321C, green chile #5E8F2B
// Usage, from nm-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let CHILERED: UInt32 = 0x8C1D18, TURQ: UInt32 = 0x0E7C86, ADOBE: UInt32 = 0xF3E3C3
let POD: UInt32 = 0xC2301F, PODTOP: UInt32 = 0xE0563F, CALYX: UInt32 = 0x4E7A24, STEM: UInt32 = 0xC9B27A
let PASTRY: UInt32 = 0xE2B05A, PASTRYTOP: UInt32 = 0xF1CE8A, HONEY: UInt32 = 0xB0720F
let TORT: UInt32 = 0xE9CF98, TORTTOP: UInt32 = 0xF4E2BB, REDCHILE: UInt32 = 0xA8321C, GREENCHILE: UInt32 = 0x5E8F2B

/// A: the red chile pod. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's chile().
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

/// B: a sopaipilla, puffed, with honey running over the top.
func sopaipilla(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    c.setFillColor(rgb(PASTRY)); c.addPath(R(0.15, 0.30, 0.70, 0.38, 0.16)); c.fillPath()
    c.setFillColor(rgb(PASTRYTOP)); c.addPath(R(0.22, 0.50, 0.56, 0.14, 0.07)); c.fillPath()
    c.setStrokeColor(rgb(HONEY)); c.setLineWidth(0.045 * s); c.setLineCap(.round)
    c.move(to: CGPoint(x: 0.30 * s, y: 0.62 * s))
    c.addCurve(to: CGPoint(x: 0.70 * s, y: 0.60 * s), control1: CGPoint(x: 0.42 * s, y: 0.52 * s), control2: CGPoint(x: 0.56 * s, y: 0.68 * s))
    c.strokePath()
    for (x, l) in [(0.40, 0.12), (0.62, 0.17)] as [(CGFloat, CGFloat)] {
        c.move(to: CGPoint(x: x * s, y: 0.58 * s)); c.addLine(to: CGPoint(x: x * s, y: (0.58 - l) * s)); c.strokePath()
    }
}

/// C: a breakfast burrito, side view, smothered half red, half green.
func burrito(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    c.setFillColor(rgb(TORT)); c.addPath(R(0.14, 0.32, 0.72, 0.30, 0.15)); c.fillPath()
    c.setFillColor(rgb(TORTTOP)); c.addPath(R(0.20, 0.50, 0.60, 0.08, 0.04)); c.fillPath()
    c.setFillColor(rgb(REDCHILE)); c.addPath(R(0.18, 0.54, 0.33, 0.14, 0.07)); c.fillPath()
    c.setFillColor(rgb(GREENCHILE)); c.addPath(R(0.49, 0.54, 0.33, 0.14, 0.07)); c.fillPath()
}

func render(_ n: Int, _ bg: UInt32, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(bg)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, TURQ, out + "/concept-a-1024.png", chile)
render(1024, TURQ, out + "/concept-b-1024.png", sopaipilla)
render(1024, ADOBE, out + "/concept-c-1024.png", burrito)
