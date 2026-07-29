// Dump the system's own HDR ICC profiles so we embed exactly what the OS uses
// rather than a hand-rolled approximation. Apple ships these inside
// CoreGraphics, not as files under /System/Library/ColorSync/Profiles.
//
//   swiftc -O dumpicc.swift -o /tmp/dumpicc && /tmp/dumpicc [output-dir]
//
// Output dir defaults to the current directory.

import CoreGraphics
import Foundation

let outDir = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "."

let names: [(String, CFString)] = [
  ("Rec2100PQ", CGColorSpace.itur_2100_PQ),
  ("Rec2100HLG", CGColorSpace.itur_2100_HLG),
  ("Rec2020", CGColorSpace.itur_2020),
]

for (label, name) in names {
  guard let cs = CGColorSpace(name: name) else {
    print("\(label): UNAVAILABLE on this OS")
    continue
  }
  guard let icc = cs.copyICCData() as Data? else {
    print("\(label): no ICC data")
    continue
  }
  let url = URL(fileURLWithPath: outDir).appendingPathComponent("\(label).icc")
  do {
    try icc.write(to: url)
    print("\(label): \(icc.count) bytes -> \(url.path)")
  } catch {
    print("\(label): write failed - \(error.localizedDescription)")
  }
}
