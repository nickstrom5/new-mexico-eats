// Prints a PDF's text, page by page (macOS PDFKit; no Python PDF library needed). Used by fetch_official.py for Albuquerque's
// weekly "Consumer Health Protection Inspections Performed" report.
// Usage: swift pipeline/pdf_text.swift in.pdf > out.txt
import Foundation
import PDFKit

guard CommandLine.arguments.count > 1, let doc = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1])) else {
    FileHandle.standardError.write("usage: swift pdf_text.swift in.pdf\n".data(using: .utf8)!); exit(1)
}
for i in 0..<doc.pageCount {
    print("=== PAGE \(i + 1)")
    print(doc.page(at: i)?.string ?? "")
}
