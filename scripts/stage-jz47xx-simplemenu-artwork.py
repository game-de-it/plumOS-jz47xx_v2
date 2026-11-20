#!/usr/bin/env python3
"""Replace six 0A images in a staged copy of the SimpleMenu theme."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ART = {
    "doom": ((79, 90), "#ee956c", "#392b2c", (
        ((4, 20), (4, 9), (9, 4), (15, 4), (20, 9), (20, 20)),
        ((8, 20), (8, 11), (10, 9), (14, 9), (16, 11), (16, 20)),
        ((2, 20), (22, 20)),
    )),
    "daphne": ((96, 96), "#cdb3f1", "#30263c", (
        ((3, 5), (21, 5), (21, 19), (3, 19), (3, 5)),
        ((7, 5), (7, 19)),
        ((17, 5), (17, 19)),
        ((11, 9), (15, 12), (11, 15), (11, 9)),
        ((3, 10), (7, 10)), ((3, 14), (7, 14)),
        ((17, 10), (21, 10)), ((17, 14), (21, 14)),
    )),
    "quake": ((80, 90), "#96d4ba", "#253834", (
        ((12, 3), (21, 8), (21, 16), (12, 21), (3, 16), (3, 8), (12, 3)),
        ((3, 8), (12, 13), (21, 8)),
        ((12, 13), (12, 21)),
    )),
}


def draw_symbol(strokes, accent):
    symbol = Image.new("RGBA", (24, 24))
    draw = ImageDraw.Draw(symbol)
    for stroke in strokes:
        draw.line(stroke, fill=accent, width=2)
    return symbol


def stage_theme(theme):
    font = ImageFont.truetype(str(ROOT / "assets/frontend/default.otf"), 26)
    for name, (size, accent, background, strokes) in ART.items():
        folder = theme / "resources" / name
        symbol = draw_symbol(strokes, accent)
        icon = Image.new("RGBA", size)
        raster = symbol.resize((72, 72), Image.Resampling.NEAREST)
        icon.alpha_composite(raster, ((size[0] - 72) // 2, (size[1] - 72) // 2))
        icon.save(folder / "system.png")

        card = Image.new("RGB", (320, 240), background)
        draw = ImageDraw.Draw(card)
        draw.rectangle((14, 14, 305, 225), outline=accent)
        raster = symbol.resize((96, 96), Image.Resampling.NEAREST)
        card.paste(raster, (112, 56), raster)
        draw.text((160, 174), name.upper(), font=font, fill="#ffffff", anchor="mm")
        card.save(folder / "logo.png")

    readme = theme / "README.md"
    note = (
        "\n### plumOS JZ47xx_v2 artwork changes\n\n"
        "plumOS replaced the Doom, Daphne and Quake system icons and cards with "
        "original geometric artwork and plain text. These changes to 0A are "
        "licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).\n"
    )
    if note not in readme.read_text():
        with readme.open("a") as stream:
            stream.write(note)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("theme", type=Path, nargs="+", help="Paths to staged 0A theme directories")
    for theme in parser.parse_args().theme:
        stage_theme(theme)
