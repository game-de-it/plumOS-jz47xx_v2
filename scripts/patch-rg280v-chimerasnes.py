#!/usr/bin/env python3
"""Disable ChimeraSNES audio-driven frameskip by default on RG280V."""
from pathlib import Path
import re
import sys

path = Path(sys.argv[1]) / "libretro_core_options.h"
source = path.read_text()
pattern = r'("chimerasnes_frameskip",.*?\n\s*\},\n\s*)"auto"(\s*\n\s*\},)'
updated, count = re.subn(pattern, r'\1"disabled"\2', source, count=1, flags=re.S)
if count == 1:
    path.write_text(updated)
elif not re.search(pattern.replace('"auto"', '"disabled"'), source, re.S):
    raise SystemExit("ChimeraSNES Frameskip option changed upstream")
# This upstream Makefile does not track header dependencies. Force recompilation
# of the translation unit that includes libretro_core_options.h.
(path.parent / "libretro.o").unlink(missing_ok=True)
