#!/usr/bin/env python3
"""Re-encode an sRGB PNG as a Rec.2100 PQ HDR PNG so white pixels render above
SDR white on EDR-capable Apple displays.

Two things make the effect work, and we write both so it survives whichever
path an app takes:

  * an iCCP chunk carrying Apple's own "Rec. ITU-R BT.2100 PQ" ICC profile
    (dumped from CGColorSpace.itur_2100_PQ) -- this is what ColorSync-based
    apps read (Preview, Quick Look, Finder, Safari)
  * a cICP chunk (primaries 9 / transfer 16 / matrix 0 / full range), the
    PNG 3rd-edition way of declaring BT.2020 + PQ. Chromium reads this, and
    per spec it takes precedence over iCCP where both are understood.

Because PQ is an *absolute* transfer function, the pixel values now mean
nits rather than "whatever the display's white is". That is the whole trick:
we encode the logo's white at, say, 1000 nits while pegging everything else to
203 nits -- macOS's PQ reference white -- so non-white pixels render identical
to the SDR original while the white is asked for 4.93x reference and the OS
spends real EDR headroom on it.

Usage:
  python3 hdr_tag.py in.png -o out.png --white-nits 1000
  python3 hdr_tag.py mark.png -o out.png --white-nits 1000 --uniform
"""

import argparse
import os
import struct
import zlib

from PIL import Image

# ---------------------------------------------------------------- PQ / colour

# SMPTE ST 2084 constants
M1 = 2610.0 / 16384.0
M2 = 2523.0 / 4096.0 * 128.0
C1 = 3424.0 / 4096.0
C2 = 2413.0 / 4096.0 * 32.0
C3 = 2392.0 / 4096.0 * 32.0

PQ_PEAK = 10000.0  # nits, the ceiling PQ can address

# What macOS considers SDR reference white when it decodes PQ content -- i.e. the
# nit level that lands exactly on "normal" white. This is the BT.2408 graphics
# white convention, and it is *not* 100. Measured with refwhite.swift by pushing
# PQ patches through ColorSync into extendedLinearSRGB, where 1.0 is SDR white by
# definition; 203 nits came back as 0.9999, and the relationship is linear.
# Encoding a pixel below this makes it render dimmer than the SDR original.
SDR_WHITE_NITS = 203.0


def pq_encode(nits):
    """Absolute luminance (nits) -> PQ code value in 0..1 (ST 2084 inverse EOTF)."""
    y = max(0.0, min(1.0, nits / PQ_PEAK))
    yp = y**M1
    return ((C1 + C2 * yp) / (1.0 + C3 * yp)) ** M2


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


# BT.709/sRGB linear RGB -> BT.2020 linear RGB, both D65, so no chromatic
# adaptation needed. Derived from the two primary matrices via XYZ.
RGB709_TO_RGB2020 = (
    (0.6274039, 0.3292830, 0.0433131),
    (0.0690973, 0.9195404, 0.0113623),
    (0.0163914, 0.0880133, 0.8955953),
)


def to_rec2020(r, g, b):
    m = RGB709_TO_RGB2020
    return (
        m[0][0] * r + m[0][1] * g + m[0][2] * b,
        m[1][0] * r + m[1][1] * g + m[1][2] * b,
        m[2][0] * r + m[2][1] * g + m[2][2] * b,
    )


def smoothstep(x, lo, hi):
    if hi <= lo:
        return 1.0 if x >= hi else 0.0
    t = max(0.0, min(1.0, (x - lo) / (hi - lo)))
    return t * t * (3.0 - 2.0 * t)


# ---------------------------------------------------------------- pixel paths


def convert_pixel(rgb, base_nits, white_nits, lo, hi, uniform):
    """sRGB 8-bit tuple -> three PQ code values in 0..1.

    Colour is properly converted through linear light into BT.2020. Brightness
    is then assigned per pixel: how "white" a pixel is decides how many nits it
    asks for, ramping smoothly so anti-aliased edges glow into the boost
    instead of stepping into it.
    """
    r, g, b = (v / 255.0 for v in rgb)

    if uniform:
        w = 1.0
    else:
        w = smoothstep(min(r, g, b), lo, hi)
    nits = base_nits + (white_nits - base_nits) * w

    lin = to_rec2020(srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b))
    return tuple(pq_encode(max(0.0, c) * nits) for c in lin)


def assign_pixel(rgb):
    """The crude version: reinterpret the existing 8-bit values as PQ code
    values with no conversion. 255 then literally means 10,000 nits. Colours
    other than white shift noticeably, which is why this only looks right on
    white-on-transparent art."""
    return tuple(v / 255.0 for v in rgb)


# ---------------------------------------------------------------- PNG writing


def _chunk(kind, data):
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png16(path, width, height, rows, icc_bytes, icc_name=b"Rec2100PQ"):
    """Write a 16-bit RGB/RGBA PNG with cICP + iCCP. Pillow can't do 16-bit
    per channel colour, so we emit the container ourselves."""
    has_alpha = len(rows[0]) == width * 4
    colour_type = 6 if has_alpha else 2

    ihdr = struct.pack(">IIBBBBB", width, height, 16, colour_type, 0, 0, 0)

    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter type: None
        raw.extend(struct.pack(">%dH" % len(row), *row))

    cicp = bytes((9, 16, 0, 1))  # BT.2020 primaries, PQ transfer, RGB, full range
    iccp = icc_name + b"\x00\x00" + zlib.compress(icc_bytes, 9)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_chunk(b"IHDR", ihdr))
        f.write(_chunk(b"cICP", cicp))
        f.write(_chunk(b"iCCP", iccp))
        f.write(_chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(_chunk(b"IEND", b""))


# ---------------------------------------------------------------------- main


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("-o", "--out", required=True)
    # Resolve next to this script, not the cwd, so it works from anywhere.
    default_icc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Rec2100PQ.icc")
    p.add_argument("--icc", default=default_icc,
                   help="Rec.2100 PQ ICC profile to embed (default: alongside this script)")
    p.add_argument("--mode", choices=("convert", "assign"), default="convert")
    p.add_argument("--white-nits", type=float, default=1000.0,
                   help="nits requested for pure-white pixels (default 1000)")
    p.add_argument("--base-nits", type=float, default=SDR_WHITE_NITS,
                   help="nits for everything else. Default %(default)g is macOS's PQ "
                        "reference white, so non-white pixels render identically to "
                        "the SDR original. Lower it and they get *dimmer*.")
    p.add_argument("--white-lo", type=float, default=0.55,
                   help="min-channel value where the boost starts ramping in")
    p.add_argument("--white-hi", type=float, default=0.98,
                   help="min-channel value where the boost reaches full")
    p.add_argument("--uniform", action="store_true",
                   help="boost every pixel to --white-nits, ignoring whiteness")
    p.add_argument("--flatten", metavar="HEX",
                   help="composite transparency onto this colour first, e.g. 3C9CFC")
    a = p.parse_args()

    if not os.path.exists(a.icc):
        p.error(f"missing ICC profile {a.icc}\n"
                f"Generate it from the system first:\n"
                f"  swiftc -O dumpicc.swift -o /tmp/dumpicc && "
                f"/tmp/dumpicc {os.path.dirname(a.icc) or '.'}")
    icc = open(a.icc, "rb").read()

    img = Image.open(a.input).convert("RGBA")
    if a.flatten:
        h = a.flatten.lstrip("#")
        bg = Image.new("RGBA", img.size, tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
        img = Image.alpha_composite(bg, img)

    w, h = img.size
    px = img.load()

    # Logo art has few distinct colours, so memoizing the per-colour maths keeps
    # this fast without needing numpy.
    cache = {}
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b, alpha = px[x, y]
            key = (r, g, b)
            out = cache.get(key)
            if out is None:
                if a.mode == "assign":
                    vals = assign_pixel(key)
                else:
                    vals = convert_pixel(key, a.base_nits, a.white_nits,
                                         a.white_lo, a.white_hi, a.uniform)
                out = tuple(min(65535, max(0, round(v * 65535.0))) for v in vals)
                cache[key] = out
            row.extend(out)
            row.append(alpha * 257)
        rows.append(row)

    write_png16(a.out, w, h, rows, icc)

    peak = pq_encode(a.white_nits)
    print(f"wrote {a.out}  {w}x{h} RGBA 16-bit  Rec.2100 PQ")
    print(f"  mode={a.mode}  unique colours={len(cache)}")
    if a.mode == "convert":
        base_x = a.base_nits / SDR_WHITE_NITS
        white_x = a.white_nits / SDR_WHITE_NITS
        print(f"  base  {a.base_nits:7.1f} nits = {base_x:5.2f}x SDR white"
              f"{'  (unshifted)' if abs(base_x - 1) < 0.01 else '  <-- NOT 1.00x, colours will shift'}")
        print(f"  white {a.white_nits:7.1f} nits = {white_x:5.2f}x SDR white  (PQ code {peak:.4f})")
    else:
        print("  8-bit values reinterpreted as PQ code; 255 = 10,000 nits")
    print("  chunks: IHDR, cICP(9/16/0/1), iCCP(Rec2100PQ), IDAT, IEND")


if __name__ == "__main__":
    main()
