#!/usr/bin/env python3
"""news-image-20261127: copy the day's front page to the output directory.

The entry image (entry.png, 1024x1024, a newspaper front page summing up
Friday 27 November 2026 world news) is shipped in this repository next to
this program. This program validates the PNG thoroughly, copies it
byte-for-byte to $MAKEFUN_OUTPUT_DIR/entry.png (default /output), and
re-validates the copy. Standard library only, no network, deterministic:
two runs write identical bytes.

Run: MAKEFUN_OUTPUT_DIR=out python3 main.py
Revision history (thinking_revised: this file took its final content
from at least two assistant messages that wrote or edited it):
  - v1: full program written (validate + copy + re-validate).
  - v2: added the IDAT payload check below (every IDAT chunk must be
    non-empty and their combined payload must be non-zero), so a PNG
    whose image data was stripped to empty IDAT chunks is rejected
    even though its structure and CRCs still walk cleanly.
  - v3: added an IHDR bit-depth / color-type sanity check.
"""
import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = (
    "6531a66ec0f27a71f3ecb646f476427cb196cbc5feeb5a97141d82ede60bcb4a"
)
EXPECTED_SIZE = 417979
MAX_BYTES = 1 << 20
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("error: " + msg, file=sys.stderr)
    raise SystemExit(1)


def validate_png(data):
    """Validate a whole PNG: magic, IHDR dims, CRC walk to IEND, IDAT."""
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % len(data))
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG magic bytes")
    pos = 8
    seen_idat = False
    seen_iend = False
    idat_bytes = 0
    first = True
    while pos < len(data):
        if pos + 8 > len(data):
            fail("truncated PNG chunk header at offset %d" % pos)
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            fail("truncated PNG chunk %r at offset %d" % (ctype, pos))
        chunk_data = data[pos + 8:pos + 8 + length]
        stored_crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        actual_crc = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail("bad CRC in %r chunk at offset %d" % (ctype, pos))
        if first:
            if ctype != b"IHDR":
                fail("first PNG chunk is %r, expected IHDR" % ctype)
            if length != 13:
                fail("IHDR length is %d, expected 13" % length)
            width, height = struct.unpack(">II", chunk_data[:8])
            if width == 0 or height == 0:
                fail("PNG has a zero dimension")
            if width > MAX_DIM or height > MAX_DIM:
                fail("PNG is %dx%d, over the 1024x1024 limit"
                     % (width, height))
            bit_depth, color_type = chunk_data[8], chunk_data[9]
            if bit_depth not in (1, 2, 4, 8, 16):
                fail("PNG has an invalid bit depth %d" % bit_depth)
            if color_type not in (0, 2, 3, 4, 6):
                fail("PNG has an invalid color type %d" % color_type)
            first = False
        if ctype == b"IDAT":
            seen_idat = True
            if length == 0:
                fail("empty IDAT chunk at offset %d" % pos)
            idat_bytes += length
        if ctype == b"IEND":
            if length != 0:
                fail("IEND chunk has a non-zero length")
            if end != len(data):
                fail("trailing bytes after IEND")
            seen_iend = True
            break
        pos = end
    if not seen_idat:
        fail("PNG has no IDAT chunk")
    if idat_bytes == 0:
        fail("PNG IDAT payload is empty")
    if not seen_iend:
        fail("PNG has no IEND chunk")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    try:
        with open(src, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        fail("cannot read entry.png: %s" % exc)
    if len(data) != EXPECTED_SIZE:
        fail("entry.png is %d bytes, expected %d"
             % (len(data), EXPECTED_SIZE))
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        fail("entry.png sha256 does not match the expected value")
    validate_png(data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)
    with open(dst, "rb") as fh:
        written = fh.read()
    if written != data:
        fail("written entry.png differs from the source bytes")
    if hashlib.sha256(written).hexdigest() != EXPECTED_SHA256:
        fail("written entry.png sha256 does not match the expected value")
    validate_png(written)
    print("wrote %s (%d bytes, sha256 %s)"
          % (dst, len(written), EXPECTED_SHA256))


if __name__ == "__main__":
    main()
