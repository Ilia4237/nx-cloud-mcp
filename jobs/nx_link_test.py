import os
import struct
import zlib
from pathlib import Path
import NXOpen

folder = Path(os.environ["SIEMENS_JOB_DIR"]).resolve()
if NXOpen.Session.GetSession() is None:
    raise RuntimeError("NX session unavailable")
image = folder / "LINK_TEST.png"
report = folder / "LINK_TEST.txt"
if image.exists() or report.exists():
    raise RuntimeError("Refusing to overwrite link test files")
width, height = 320, 180
rows = []
for y in range(height):
    row = bytearray()
    for x in range(width):
        border = x < 6 or y < 6 or x >= width-6 or y >= height-6
        bar = 24 <= x < 296 and 124 <= y < 150
        color = (35,190,120) if bar else ((50,120,210) if border else (24,32,48))
        row.extend(color)
    rows.append(b"\x00" + bytes(row))
def chunk(kind, payload):
    return struct.pack(">I",len(payload))+kind+payload+struct.pack(">I",zlib.crc32(kind+payload)&0xffffffff)
header = struct.pack(">IIBBBBB",width,height,8,2,0,0,0)
label = b"Description\x00Synthetic link test. Not an NX model rendering or screenshot."
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR",header) + chunk(b"tEXt",label)
png += chunk(b"IDAT",zlib.compress(b"".join(rows))) + chunk(b"IEND",b"")
image.write_bytes(png)
report.write_text("LINK_TEST_OK\nSynthetic PNG transport test only; not an NX model image.\nNo part was opened, modified or saved.\n",encoding="utf-8")
print("LINK_TEST_OK: LINK_TEST.png and LINK_TEST.txt generated")
