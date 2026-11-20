#!/usr/bin/env python3
"""Drop unused legacy fonts from an audited, staged 350teric skins tree."""

import argparse
import hashlib
from pathlib import Path


ARIMO = "423a4c14d32d2846d5b54d9ba192eca17d1d56ee431601ddec09a76c6bc54692"
LEGACY_FONTS = {
    "OldBoy/font-upstream.ttf": ARIMO,
    "PSNextDark/font-upstream.ttf": ARIMO,
    "Zelda/font-upstream.ttf": "fa30bb258c39143cc7b0422ff380c22fb75ad6183aba2510d28672c73b6776cc",
    "Flat/fonts/pf_tempesta_seven_condensed.ttf": "53e28484e0a79d0f521f3f6dadfd5015b62b05c9693f98806d32de8f976fb132",
    "Flat/imgs/font.png": "ef4b0f1e58dd3669e98a2333339184c2152137c1d255f5633054c5343165876f",
}


def stage_skins(skins):
    for name in ("OldBoy", "PSNextDark", "Zelda", "Flat"):
        if not (skins / name / "skin.conf").is_file():
            raise ValueError(f"Missing staged skin: {skins / name}")
    for relative, expected in LEGACY_FONTS.items():
        path = skins / relative
        if path.is_symlink() or (path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != expected):
            raise ValueError(f"Unexpected legacy font: {path}")
    for relative in LEGACY_FONTS:
        (skins / relative).unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skins", type=Path, help="Path to a staged .esoteric/skins directory")
    stage_skins(parser.parse_args().skins)
