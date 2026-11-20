#!/usr/bin/env python3
"""Stage license notices and the replacement font for the 320x240 SimUI theme."""

import argparse
import hashlib
from pathlib import Path
import shutil


LICENSES = Path(__file__).resolve().parents[1] / "assets/frontend/licenses"
ORIGINAL_FONTS = {
    "BPreplayBold.ttf": "9577df6f1f4c31a99194801feb3e0ec72b032d2b33baddd99b9bf9f38793b1f7",
    "BPreplayBold-unhinted.otf": "33d0f588ec40928dbc62ec2a90bb248ec6fcab1d63f82b0275cf9e7f59facf92",
}
FONT_NAME = "NotoSansJP.otf"
FONT_TARGET = "/media/data/plumos/fonts/default.otf"


def stage_theme(theme):
    config = theme / "theme.ini"
    text = config.read_text()
    resources = theme / "resources/general"
    font = resources / FONT_NAME
    originals = [resources / name for name in ORIGINAL_FONTS]
    staged = (font.is_symlink() and str(font.readlink()) == FONT_TARGET
              and all(not path.exists() for path in originals)
              and text.count("resources/general/" + FONT_NAME) == 3)
    if not staged:
        for path in originals:
            if hashlib.sha256(path.read_bytes()).hexdigest() != ORIGINAL_FONTS[path.name]:
                raise ValueError(f"Unexpected SimUI font: {path}")
        if text.count("resources/general/BPreplayBold.ttf") != 3 or font.is_symlink() or font.exists():
            raise ValueError(f"Unexpected SimUI font configuration: {theme}")
        font.symlink_to(FONT_TARGET)
        config.write_text(text.replace("resources/general/BPreplayBold.ttf",
                                       "resources/general/" + FONT_NAME))
        for path in originals:
            path.unlink()

    shutil.copyfile(LICENSES / "SimUI-MIT.txt", theme / "LICENSE")
    shutil.copyfile(LICENSES / "NotoSansJP-OFL.txt", theme / "NotoSansJP-OFL.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("theme", type=Path, help="Path to a staged 320x240 SimUI theme directory")
    stage_theme(parser.parse_args().theme)
