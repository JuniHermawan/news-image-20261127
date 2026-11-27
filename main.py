#!/usr/bin/env python3
"""news-image-20261127 -- entrypoint.

Validates the finished newspaper front page (entry.png) and copies it
into the output directory the harness expects.

The image itself is a fixed asset: a 1024x1024 PNG front page for the
make.fun bounty "Sum up 27 November's world news in one image"
("THE WORLD IN ONE DAY", six stories from 26-27 Nov 2026). This script
does not generate or alter any pixel -- it only proves the asset is a
well-formed PNG of the right size and hands it over byte for byte.

Stdlib only. No network, no randomness, no timestamps: run it twice
and the output is identical every time.
"""

import hashlib
import os
import struct
import sys
import zlib

# The eight bytes every PNG file starts with.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
SOURCE_NAME = "entry.png"


def fail(message):
    """Print an error and stop with a non-zero exit code."""
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def read_chunks(data):
    """Walk the PNG chunk list, yielding (type, payload) pairs.

    Each chunk is: 4-byte big-endian length, 4-byte type, `length`
    bytes of data, 4-byte CRC. Parsing stops cleanly at IEND.
    """
    offset = len(PNG_SIGNATURE)
    while offset < len(data):
        if offset + 8 > len(data):
            fail("truncated chunk header at offset %d" % offset)
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        start = offset + 8
        end = start + length
        if end + 4 > len(data):
            fail("truncated %s chunk" % chunk_type.decode("latin-1"))
        stored_crc = struct.unpack(">I", data[end:end + 4])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(data[start:end], actual_crc)
        if actual_crc != stored_crc:
            fail("%s chunk failed its CRC check (file may be corrupt)"
                 % chunk_type.decode("latin-1"))
        yield chunk_type, data[start:end]
        offset = end + 4
        if chunk_type == b"IEND":
            break


def check_entry(path):
    """Read entry.png and confirm it is a 1024x1024 PNG with image data.

    Returns the raw bytes, ready to be copied unchanged.
    """
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        fail("cannot read %s: %s" % (path, exc))

    if len(data) < len(PNG_SIGNATURE) + 8:
        fail("entry.png is too small to be a PNG")
    if data[:8] != PNG_SIGNATURE:
        fail("entry.png does not start with the PNG signature")

    chunks = list(read_chunks(data))
    if not chunks or chunks[0][0] != b"IHDR":
        fail("first chunk is not IHDR")

    ihdr = chunks[0][1]
    if len(ihdr) != 13:
        fail("IHDR chunk is %d bytes, expected 13" % len(ihdr))
    width, height = struct.unpack(">II", ihdr[:8])
    if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
        fail("entry.png is %dx%d, expected %dx%d"
             % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))

    idat_bytes = sum(len(payload) for ctype, payload in chunks
                     if ctype == b"IDAT")
    if idat_bytes == 0:
        fail("entry.png has no IDAT image data")

    return data


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)

    data = check_entry(source)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./output")
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, SOURCE_NAME)
    with open(destination, "wb") as handle:
        handle.write(data)

    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)"
          % (destination, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
