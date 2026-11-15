#!/usr/bin/env python3
"""Use the FCEUX default NES colors for the RG280V QuickNES build."""

import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
source = pathlib.Path(sys.argv[1]) / "nes_emu/Nes_Emu.cpp"
palette_file = root / "assets/emulators/fceux-default-palette.hex"
colors = [token for line in palette_file.read_text().splitlines()
          if not line.startswith("#") for token in line.split()]
if len(colors) != 64 or any(not re.fullmatch(r"[0-9A-F]{6}", value)
                            for value in colors):
    raise SystemExit("expected 64 RGB palette entries")
data = source.read_text()
start = data.index("Nes_Emu::rgb_t const Nes_Emu::nes_colors [color_table_size] =")
opening = data.index("{", start)
entries = list(re.finditer(r"\{\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\}", data[opening:]))
if len(entries) < 64:
    raise SystemExit("QuickNES default palette layout changed")
first, last = entries[0], entries[63]
replacement = ",\n\t".join(
    "{{{},{},{}}}".format(*bytes.fromhex(value))
    for value in colors
)
begin = opening + first.start()
end = opening + last.end()
source.write_text(data[:begin] + replacement + data[end:])
