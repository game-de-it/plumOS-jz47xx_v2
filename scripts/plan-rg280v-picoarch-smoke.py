#!/usr/bin/env python3
"""Choose small, read-only test content for installed PicoArch cores."""

import json
import os
import sys
from functools import lru_cache
from pathlib import Path


inspection_path, v90s_systems_path, sd2_list_path, rom2_root_path, output_path = map(
    Path, sys.argv[1:]
)
rom2_root = rom2_root_path
inspection = {}
for line in inspection_path.read_text().splitlines():
    fields = line.split("\t")
    if len(fields) >= 6:
        core = fields[0].removesuffix("_libretro.so")
        inspection[core] = set(fields[4].lower().split("|"))

systems = json.loads(v90s_systems_path.read_text())["systems"]
core_systems = {}
for system in systems:
    for profile in system.get("launch_profiles", []):
        if ":" not in profile:
            continue
        backend, core = profile.split(":", 1)
        if backend in ("retroarch", "picoarch"):
            core_systems.setdefault(core, [])
            if system["id"] not in core_systems[core]:
                core_systems[core].append(system["id"])

directory_map = {
    "nes": "nes", "fds": "nes", "sfc": "snes", "gb": "gb", "gbc": "gbc",
    "gba": "gba", "megadrive": "megadrive", "mastersystem": "mastersystem",
    "gamegear": "gamegear", "pcengine": "pcengine", "pcenginecd": "pcenginecd",
    "supergrafx": "_etc/supergrafx", "wonderswan": "wonderswan",
    "wonderswancolor": "wonderswan", "ngp": "ngpc", "ngpc": "ngpc",
    "msx": "msx2", "arcade": "fbneo", "fbneo": "fbneo",
    "neogeo": "_etc/neogeo", "neogeocd": "_etc/neogeocd",
    "atari2600": "ATARI/2600", "atari5200": "ATARI/5200",
    "atari7800": "ATARI/7800", "atari800": "ATARI/800",
    "jaguar": "ATARI/Jaguar", "pico8": "pico-8", "pc88": "pc88",
    "pc98": "_etc/pc-9800", "scummvm": "scummvm",
    "3do": "_etc/3do", "amiga": "_etc/amiga", "atarist": "_etc/atarist",
    "c64": "_etc/c64", "vic20": "_etc/vic20", "cannonball": "_etc/cannonball",
    "colecovision": "_etc/colecovision", "cpc": "_etc/cpc",
    "dinothawr": "_etc/dinothawr", "doom": "_etc/doom",
    "intellivision": "_etc/intellivision", "lowresnx": "_etc/lowresnx",
    "thomson": "_etc/moto", "odyssey2": "_etc/odyssey2",
    "pcfx": "_etc/pcfx", "pokemini": "_etc/pokemini",
    "quake": "_etc/quake", "sega32x": "_etc/sega32x",
    "segacd": "_etc/segacd", "supervision": "_etc/supervision",
    "zxspectrum": "_etc/zxspectrum", "music": "_etc/music",
    "microw8": "_etc/microw8", "lutro": "_etc/lutro",
    "j2me": "_etc/j2me", "psx": "psx", "gameandwatch": "_etc/gameandwatch",
    "vmu": "_etc/vmu", "channelf": "_etc/channelf", "uzebox": "_etc/uzebox",
    "ti83": "_etc/ti83", "cavestory": "_etc/cavestory",
}
priority = {
    "fceumm": ["nes", "fds"], "nestopia": ["nes", "fds"],
    "mednafen_supergrafx": ["supergrafx", "pcengine"],
    "fbneo": ["fbneo", "arcade"], "fbalpha2012": ["fbneo", "arcade"],
    "mednafen_wswan": ["wonderswan", "wonderswancolor"],
    "mednafen_ngp": ["ngpc", "ngp"],
    "atari800": ["atari800", "atari5200"],
    "mgba": ["gba", "gb"], "vbam": ["gba", "gb"],
    "vice_xvic": ["vic20"],
}
sd2_files = [line.strip() for line in sd2_list_path.read_text().splitlines()]
preferred_names = {
    "nes": ["Baseball.nes", "Super Mario Bros..nes"],
    "sfc": ["Super Mario World"],
    "gb": ["Super Mario Land"],
    "megadrive": ["Bare Knuckle"],
    "mastersystem": ["Wonder Boy 3"],
    "gamegear": ["Puyo Puyo.gg"],
    "pcengine": ["BlazingLazers_U.pce"],
    "fbneo": ["rtypeleo.zip", "airduelm72.zip"],
    "pico8": ["Celeste.p8"],
    "atari2600": ["Asteroids.bin"],
    "atari800": ["FoodFight.rom"],
    "msx": ["Ys2-p.dsk", "usas.rom"],
    "lutro": ["lutro-pong.lutro"],
    "cavestory": ["Doukutsu.exe"],
    "c64": ["inbread.d64"],
}


@lru_cache(maxsize=None)
def local_files(directory):
    if not directory.is_dir():
        return []
    found = []
    base_depth = len(directory.parts)
    for root, dirs, files in os.walk(directory):
        if len(Path(root).parts) - base_depth >= 2:
            dirs[:] = []
        for name in files:
            path = Path(root) / name
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if 0 < size <= 32 * 1024 * 1024:
                found.append((str(path), size))
    return found


def score(item, system):
    path, size, source = item
    name = Path(path).name.lower()
    preferred = preferred_names.get(system, [])
    named = next((i for i, value in enumerate(preferred) if value.lower() in name), 99)
    return (named, source != "sd2", size, name)


planned = []
for core in sorted(inspection):
    extensions = inspection[core]
    choices = priority.get(core, core_systems.get(core, []))
    entry = {"core": core, "systems": choices, "status": "no_content"}
    # These need a directory bundle or large disc image, not a standalone
    # BIOS file or the unrelated C64 ZIP selected by extension alone.
    if core in {"nxengine", "pcsx_rearmed"}:
        planned.append(entry)
        continue
    for system in choices:
        relative = directory_map.get(system)
        if not relative:
            continue
        candidates = []
        sd2_alias = {"sfc": "sfc", "pico8": "pico-8", "msx": "msx"}.get(
            system, relative.split("/")[-1]
        )
        sd2_dir = "/media/data/sd2/roms/" + sd2_alias + "/"
        for path in sd2_files:
            if path.startswith(sd2_dir):
                suffix = Path(path).suffix.lower().lstrip(".")
                if suffix in extensions and suffix not in ("cue", "ccd", "m3u"):
                    candidates.append((path, 0, "sd2"))
        for path, size in local_files(rom2_root / relative):
            suffix = Path(path).suffix.lower().lstrip(".")
            if suffix in extensions and suffix not in ("cue", "ccd", "m3u"):
                candidates.append((path, size, "rom2"))
        if candidates:
            selected = min(candidates, key=lambda item: score(item, system))
            entry.update(system=system, source=selected[2], path=selected[0],
                         bytes=selected[1], status="planned")
            break
    planned.append(entry)

output_path.write_text(json.dumps(planned, ensure_ascii=False, indent=2) + "\n")
print("cores", len(planned), "planned", sum(e["status"] == "planned" for e in planned))
for entry in planned:
    print(entry["core"], entry["status"], entry.get("system", "-"),
          entry.get("source", "-"), Path(entry["path"]).name if "path" in entry else "-")
