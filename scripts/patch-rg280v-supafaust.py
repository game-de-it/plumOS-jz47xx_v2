#!/usr/bin/env python3
"""Keep Supafaust from pinning its emulation thread to absent CPU 1."""
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "libretro.cpp"
source = path.read_text()
before = '"Emulation thread affinity mask; 0x2|0x0|0x1|'
after = '"Emulation thread affinity mask; 0x0|0x1|0x2|'
if before in source:
    path.write_text(source.replace(before, after, 1))
    (path.parent / "libretro.o").unlink(missing_ok=True)
elif after not in source:
    raise SystemExit("Supafaust emulation affinity option changed upstream")

source = path.read_text()
changes = {
    '"PPU renderer; mt|st"': '"PPU renderer; st|mt"',
    'MDFNI_SetSetting("snes_faust.renderer", "mt");':
        'MDFNI_SetSetting("snes_faust.renderer", "st");',
}
for old, new in changes.items():
    if old in source:
        source = source.replace(old, new, 1)
    elif new not in source:
        raise SystemExit(f"Supafaust renderer setting changed upstream: {old}")
if source != path.read_text():
    path.write_text(source)
    (path.parent / "libretro.o").unlink(missing_ok=True)
