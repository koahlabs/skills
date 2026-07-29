import AppKit
import ImageIO
import CoreGraphics

_ = NSApplication.shared
for s in NSScreen.screens {
  let hr = s.maximumExtendedDynamicRangeColorComponentValue
  let pot = s.maximumPotentialExtendedDynamicRangeColorComponentValue
  print(String(format: "display %@  EDR headroom now=%.2fx  potential=%.2fx  (~%.0f nits peak white)",
               s.localizedName, hr, pot, pot * 100))
}
print("")
for path in CommandLine.arguments.dropFirst() {
  guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
        let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    print("\(path): FAILED to decode"); continue
  }
  let cs = img.colorSpace
  let isHDR = cs.map { CGColorSpaceUsesITUR_2100TF($0) } ?? false
  let name = (cs?.name as String?) ?? "(unnamed)"
  print(String(format: "%-26@  usesITUR_2100TF=%@  bpc=%d  %@",
               (path as NSString).lastPathComponent as NSString,
               isHDR ? "YES" : "no ", img.bitsPerComponent, name as NSString))
}
