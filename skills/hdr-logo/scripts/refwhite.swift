import CoreGraphics
import Foundation

// ST 2084 inverse EOTF: nits -> PQ code
let M1 = 2610.0/16384.0, M2 = 2523.0/4096.0*128.0
let C1 = 3424.0/4096.0, C2 = 2413.0/4096.0*32.0, C3 = 2392.0/4096.0*32.0
func pq(_ nits: Double) -> Double {
  let y = max(0, min(1, nits/10000)); let yp = pow(y, M1)
  return pow((C1 + C2*yp)/(1 + C3*yp), M2)
}

let pqCS = CGColorSpace(name: CGColorSpace.itur_2100_PQ)!
// In extendedLinearSRGB, 1.0 is *defined* as SDR reference white.
let linCS = CGColorSpace(name: CGColorSpace.extendedLinearSRGB)!

func probe(_ nits: Double) -> Float {
  // 1x1 grey patch at `nits`, encoded PQ
  let code = UInt16(pq(nits) * 65535.0)
  var px: [UInt16] = [code, code, code, 65535]
  let src = CGContext(data: &px, width: 1, height: 1, bitsPerComponent: 16,
                      bytesPerRow: 8, space: pqCS,
                      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
                                | CGBitmapInfo.byteOrder16Little.rawValue)!
  let img = src.makeImage()!

  var out = [Float](repeating: 0, count: 4)
  let dst = CGContext(data: &out, width: 1, height: 1, bitsPerComponent: 32,
                      bytesPerRow: 16, space: linCS,
                      bitmapInfo: CGBitmapInfo.floatComponents.rawValue
                                | CGImageAlphaInfo.premultipliedLast.rawValue
                                | CGBitmapInfo.byteOrder32Little.rawValue)!
  dst.draw(img, in: CGRect(x: 0, y: 0, width: 1, height: 1))
  return out[0]
}

print("PQ nits -> extendedLinearSRGB (1.0 == SDR reference white)")
for n in [10.0, 50, 80, 100, 150, 203, 250, 300, 400, 1000, 4000, 10000] {
  let v = probe(n)
  let mark = abs(v - 1.0) < 0.02 ? "   <-- SDR white" : ""
  print(String(format: "  %7.0f nits  ->  %8.4f%@", n, v, mark))
}
