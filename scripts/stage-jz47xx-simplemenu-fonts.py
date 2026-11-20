#!/usr/bin/env python3
"""Replace the audited fonts in a staged SimpleMenu tree."""
import argparse
import hashlib
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("runtime", type=Path)
parser.add_argument("theme", type=Path, nargs="+")
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
font = "/media/data/plumos/fonts/default.otf"
notice = repo / "assets/frontend/licenses/NotoSansJP-OFL.txt"
legacy_archive_hashes = {
    "4d0c10eed6cdd84e63dc5ba63dd242bc470274a968d47378fe38350c0e09c48c",  # SD image
    "a601b8283468ab8ae189921eda5b0ab7036601b291460b8197cc803392d1b8ea",  # upstream tree
}


def replace_font(path: Path):
    path.unlink(missing_ok=True)
    path.symlink_to(font)


# The upstream archive is unused at runtime and carries copies of the old fonts.
for theme in args.theme:
    archive = theme / "resources/general.zip"
    if archive.exists() and hashlib.sha256(archive.read_bytes()).hexdigest() not in legacy_archive_hashes:
        raise ValueError(f"Unexpected 0A resource archive: {archive}")
    if any("acre.otf" in ini.read_text(errors="replace").lower() for ini in theme.rglob("*.ini")):
        raise ValueError(f"Acre is referenced by a theme configuration in {theme}")

replace_font(args.runtime / "resources/akashi.ttf")
shutil.copyfile(notice, args.runtime / "licenses/NotoSansJP-OFL.txt")
for theme in args.theme:
    resources = theme / "resources/general"
    config = theme / "theme.ini"
    replace_font(resources / "Pmc.ttf")
    replace_font(resources / "akashi.ttf")
    (resources / "Acre.otf").unlink(missing_ok=True)
    (theme / "resources/general.zip").unlink(missing_ok=True)
    text = config.read_text()
    for before, after in (("\nfont_size = 16\n", "\nfont_size = 13\n"),
                          ("\ntext1_font_size = 40\n", "\ntext1_font_size = 32\n")):
        text = text.replace(before, after)
    config.write_text(text)
    readme = theme / "README.md"
    note = (
        "\n### plumOS JZ47xx_v2 font changes\n\n"
        "The theme uses plumOS's Noto Sans JP (SIL OFL 1.1) for labels and game counts. "
        "List and heading sizes were adjusted, and the unused Acre font was removed. "
        "Theme changes are shared under CC BY-NC-SA 4.0.\n"
    )
    archive_note = "\nThe unused upstream general.zip archive was omitted because it contains the original fonts.\n"
    current_readme = readme.read_text()
    additions = "".join(part for part in (note, archive_note) if part not in current_readme)
    if additions:
        with readme.open("a") as stream:
            stream.write(additions)
