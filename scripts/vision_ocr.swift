import AppKit
import Foundation
import PDFKit
import Vision

struct OCRLine: Codable {
    let text: String
    let confidence: Float
    let bbox: [Double]
}

struct OCRItem: Codable {
    let kind: String
    let index: Int
    let width: Double
    let height: Double
    let lines: [OCRLine]
    let text: String
}

struct OCRDocument: Codable {
    let path: String
    let items: [OCRItem]
}

enum OCRScriptError: Error {
    case usage(String)
    case unsupported(String)
    case cannotOpen(String)
    case cannotRender(String)
}

func makeRequest() -> VNRecognizeTextRequest {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["en-GB", "en-US"]
    return request
}

func sortedLines(from observations: [VNRecognizedTextObservation]) -> [OCRLine] {
    let sorted = observations.sorted { lhs, rhs in
        let ly = lhs.boundingBox.minY
        let ry = rhs.boundingBox.minY
        if abs(ly - ry) > 0.015 {
            return ly > ry
        }
        return lhs.boundingBox.minX < rhs.boundingBox.minX
    }
    return sorted.compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else {
            return nil
        }
        let text = candidate.string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return nil
        }
        let box = observation.boundingBox
        return OCRLine(
            text: text,
            confidence: candidate.confidence,
            bbox: [Double(box.minX), Double(box.minY), Double(box.width), Double(box.height)]
        )
    }
}

func ocr(cgImage: CGImage, kind: String, index: Int) throws -> OCRItem {
    let request = makeRequest()
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])
    let lines = sortedLines(from: request.results ?? [])
    return OCRItem(
        kind: kind,
        index: index,
        width: Double(cgImage.width),
        height: Double(cgImage.height),
        lines: lines,
        text: lines.map { $0.text }.joined(separator: "\n")
    )
}

func cgImage(from imagePath: String) -> CGImage? {
    let url = URL(fileURLWithPath: imagePath)
    guard let image = NSImage(contentsOf: url) else {
        return nil
    }
    var rect = NSRect(origin: .zero, size: image.size)
    return image.cgImage(forProposedRect: &rect, context: nil, hints: nil)
}

func pdfPageImage(_ page: PDFPage, width: CGFloat = 1800, height: CGFloat = 2400) -> CGImage? {
    let thumbnail = page.thumbnail(of: NSSize(width: width, height: height), for: .mediaBox)
    var rect = NSRect(origin: .zero, size: thumbnail.size)
    return thumbnail.cgImage(forProposedRect: &rect, context: nil, hints: nil)
}

func processPDF(_ path: String) throws -> OCRDocument {
    guard let document = PDFDocument(url: URL(fileURLWithPath: path)) else {
        throw OCRScriptError.cannotOpen(path)
    }
    var items: [OCRItem] = []
    for pageIndex in 0..<document.pageCount {
        guard let page = document.page(at: pageIndex), let image = pdfPageImage(page) else {
            throw OCRScriptError.cannotRender("\(path)#page\(pageIndex + 1)")
        }
        items.append(try ocr(cgImage: image, kind: "page", index: pageIndex + 1))
    }
    return OCRDocument(path: path, items: items)
}

func processImages(_ paths: [String]) throws -> OCRDocument {
    var items: [OCRItem] = []
    for (index, path) in paths.enumerated() {
        guard let image = cgImage(from: path) else {
            throw OCRScriptError.cannotOpen(path)
        }
        items.append(try ocr(cgImage: image, kind: "image", index: index + 1))
    }
    return OCRDocument(path: paths.joined(separator: ","), items: items)
}

let args = CommandLine.arguments.dropFirst()
guard !args.isEmpty else {
    throw OCRScriptError.usage("usage: swift vision_ocr.swift (--pdf PATH | --images PATH...)")
}

switch args.first! {
case "--pdf":
    let remainder = Array(args.dropFirst())
    guard remainder.count == 1 else {
        throw OCRScriptError.usage("expected one PDF path")
    }
    let result = try processPDF(remainder[0])
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    FileHandle.standardOutput.write(try encoder.encode(result))
case "--images":
    let remainder = Array(args.dropFirst())
    guard !remainder.isEmpty else {
        throw OCRScriptError.usage("expected one or more image paths")
    }
    let result = try processImages(remainder)
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    FileHandle.standardOutput.write(try encoder.encode(result))
default:
    throw OCRScriptError.unsupported(String(args.first!))
}
