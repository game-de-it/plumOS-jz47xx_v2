#!/usr/bin/env python3
"""Stage factory content and audit unpacked release payloads."""
import argparse
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path

ASSETS = Path("assets/frontend")
EMULATORS = Path("output/rg280v-emulators")
PACKAGES = Path("output/rg280v-opk-integration/packages")
APPS = Path("output/rg280v-apps")
FRONTEND = Path("output/rg280v-fe")
CORES = (
    "fceumm nestopia quicknes snes9x2005 chimerasnes snes9x2005_plus "
    "gambatte gearboy vbam picodrive gearsystem mednafen_pce_fast "
    "mednafen_supergrafx mednafen_wswan fmsx bluemsx mednafen_ngp"
).split()
STANDALONE = {
    "fceux": "fceux_gcw0-2.6.6-2023-08-30.opk",
    "gambatte": "gambatte-dms-rg280v.opk",
    "pocketsnes": "PocketSNES_2019-12-12.opk",
    "picodrive": "PicoDrive_rg280v.opk",
}
OPKS = (
    "fceux223 gambatte2020 ohboy stella handy oswan smsplusgg "
    "smsplusms pokemini race uae4all fba44"
).split()
APPLICATIONS = "calculator commander bard ffplay gmu st-sdl pdfviewer".split()
OPK_NOTICES = {
    "fba44.opk": {"FBA44-LICENSE.txt": "LICENSE.txt"},
    "pokemini.opk": {"PokeMini-NOTICE.txt": "LICENSE.txt", "PokeMini-GPL-3.0.txt": "COPYING"},
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHUNKS = {
    b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"cHRM", b"sRGB"
}
SENSITIVE = re.compile(
    rb"/(?:Users|Volumes|private/(?:tmp|var))/|"
    rb"\b192\.168\.10\.\d+\b|"
    rb"-----BEGIN (?:OPENSSH|RSA|EC|DSA|PGP) PRIVATE KEY(?: BLOCK)?-----\r?\n[A-Za-z0-9+/]{24,}|"
    rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"
)
GAME_EXT = {
    ".rom", ".nes", ".unf", ".fds", ".sfc", ".smc", ".gb", ".gbc", ".gba",
    ".gg", ".sms", ".pce", ".ngp", ".ws", ".wsc", ".atr", ".a26", ".adf",
    ".dsk", ".tap", ".sna", ".z80", ".prg", ".cue", ".chd", ".iso", ".m3u",
    ".sav", ".srm", ".state", ".mcr", ".mcd", ".nvram",
}
COMMON_LIBS = (
    "libSDL_image-1.2.so.0 libSDL_mixer-1.2.so.0 libSDL_sound-1.0.so.1 "
    "libSDL_net-1.2.so.0 libFLAC.so.12 libbz2.so.1.0 libvorbisidec.so.1 "
    "libvorbis.so.0 libvorbisfile.so.3 libogg.so.0 libtheoradec.so.1 "
    "libpng14.so.14 libshake.so.1 libintl.so.8 libjpeg.so.8 libsndfile.so.1 "
    "libfceux-menu.so libgambatte-menu.so"
).split()


def sanitize_png(path):
    content = path.read_bytes()
    if not content.startswith(PNG_SIGNATURE):
        raise ValueError(f"Invalid PNG: {path.name}")
    offset = len(PNG_SIGNATURE)
    result = bytearray(PNG_SIGNATURE)
    while offset + 12 <= len(content):
        size, tag = struct.unpack_from(">I4s", content, offset)
        end = offset + 12 + size
        if end > len(content):
            break
        if tag in PNG_CHUNKS:
            result.extend(content[offset:end])
        if tag == b"IEND":
            path.write_bytes(result)
            return
        offset = end
    raise ValueError(f"Truncated PNG: {path.name}")


def audit_tree(tree):
    files = 0
    for path in sorted(tree.rglob("*")):
        name = path.relative_to(tree).as_posix()
        if (path.suffix.lower() in GAME_EXT or re.search(r"(?i)\.(?:st[0-9]+|state[0-9]+)$", path.name)
                or path.name in {".git", ".ssh", ".bash_history", "known_hosts", "authorized_keys",
                                 "BOOTMOD.CFG", "multimodel-user-v1.complete", ".plumos-ready"}):
            raise ValueError(f"Unexpected file in image: {name}")
        if path.is_symlink():
            if SENSITIVE.search(path.readlink().as_posix().encode()):
                raise ValueError(f"Private link target in image: {name}")
            continue
        if not path.is_file():
            continue
        data = path.read_bytes()
        if SENSITIVE.search(data):
            raise ValueError(f"Private value in file: {name}")
        if data.startswith((b"NES\x1a", b"MComprHD", b"PS-X EXE", b"PK\x03\x04")):
            raise ValueError(f"Unreviewed payload in image: {name}")
        if re.search(r"(?i)(?:bios|kickstart|memcard|save).*\.(?:bin|dat|gz)$", path.name):
            raise ValueError(f"Firmware or save candidate in image: {name}")
        files += 1
    return files


def install(source, destination, executable=False):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    destination.chmod(0o755 if executable else 0o644)


def package(source, destination, workspace):
    tree = workspace / "opk-content"
    subprocess.run(["unsquashfs", "-no-progress", "-d", tree, source],
                   check=True, stdout=subprocess.DEVNULL)
    try:
        if source.name == "fba44.opk":
            for name in ("fbasdl_lepus.dge", "fba_explorer.lepus.desktop", "fba_ux.lepus.desktop"):
                (tree / name).unlink()
        for notice, filename in OPK_NOTICES.get(source.name, {}).items():
            install(ASSETS / "licenses" / notice, tree / filename)
        for desktop in tree.glob("*.desktop"):
            for line in desktop.read_text().splitlines():
                if line.startswith("X-OD-Manual="):
                    manual = line.partition("=")[2].strip()
                    if manual and not (tree / manual).is_file():
                        raise ValueError(f"{source.name}: missing OPK manual {manual}")
        audit_tree(tree)
        for image in tree.rglob("*.png"):
            sanitize_png(image)
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["mksquashfs", tree, destination, "-noappend", "-no-xattrs",
                        "-all-root", "-comp", "gzip", "-processors", "2", "-no-progress"],
                       check=True, stdout=subprocess.DEVNULL)
    finally:
        shutil.rmtree(tree)


def stage_runtime(tree, workspace):
    plumos = tree / "plumos"
    for directory in ("home", "bios", "Saves", "Logs", "state/frontend"):
        (plumos / directory).mkdir(parents=True)
    for name in ("S00expand-multimodel-user", "S94hotkeys", "S95frontend", "S96remember-boot-model"):
        install(ASSETS / name, tree / "local/init.d" / name, executable=True)
    (plumos / "provision").mkdir()
    (plumos / "provision/multimodel-user-v1.pending").touch()
    for name in ("plumos-controller-ui", "plumos-text-ui", "plumos-library-scan",
                 "plumos-rg280v-hotkeys", "plumos-rg280v-power-menu",
                 "plumos-jz47xx-update-verify"):
        install(FRONTEND / name, plumos / "bin" / name, executable=True)
    install(ASSETS / "keys/jz47xx-update-public.pem",
            plumos / "share/plumos-update/public.pem")
    wrappers = (
        "fe-launch jz47xx-device-env jz47xx-media-env prepare-opk-input display-control volume-control "
        "safe-shutdown standalone-launch opk-emulator-launch picoarch-launch opk-app-launch fceux-prepare "
        "jz47xx-system-update"
    ).split()
    for name in wrappers:
        install(ASSETS / "bin" / f"plumos-{name}", plumos / "bin" / f"plumos-{name}", executable=True)
    install(EMULATORS / "pcsx4all_rg280v", plumos / "bin/pcsx4all", executable=True)
    install(EMULATORS / "picoarch-rg280v", plumos / "picoarch/bin/picoarch", executable=True)
    for name in CORES:
        filename = f"{name}_libretro.so"
        install(EMULATORS / filename, plumos / "picoarch/cores" / filename)
    for name in STANDALONE.values():
        package(EMULATORS / name, plumos / "emulators" / name, workspace)
    for name in OPKS:
        filename = f"{name}.opk"
        package(PACKAGES / filename, plumos / "emulators/opk" / filename, workspace)
    for name in APPLICATIONS:
        filename = f"{name}-rg280v.opk"
        package(APPS / filename, tree / "apps" / filename, workspace)
    for name in COMMON_LIBS:
        install(EMULATORS / "lib" / name, plumos / "lib" / name)
    for name in ("libncurses.so.5", "libreadline.so.6", "libao.so.4", "libcrypto.so.1.0.0"):
        install(PACKAGES.parent / "compat" / name, plumos / "lib/opk-compat" / name)
    for name in ("libSDL2-2.0.so.0", "libSDL2_image-2.0.so.0", "libSDL2_ttf-2.0.so.0"):
        install(APPS / "runtime-lib" / name, plumos / "lib" / name)
    for pattern, target in (
        ("lang/*.lang", "share/frontend/lang"),
        ("standalone-defaults/*", "config/standalone"),
        ("images/*.png", "themes/default/images"),
        ("logos/systems/*.png", "themes/default/logos/systems"),
        ("licenses/*.txt", "licenses"),
    ):
        for source in ASSETS.glob(pattern):
            path = plumos / target / source.name
            install(source, path)
            if path.suffix == ".png":
                sanitize_png(path)
    for name, target in (
        ("default.otf", "fonts/default.otf"), ("cjk-fallback.ttc", "fonts/cjk-fallback.ttc"),
        ("theme.json", "themes/default/theme.json"), ("settings.json", "config/frontend/settings.json"),
        ("menus.json", "config/frontend/menus.json"), ("VERSION", "VERSION"),
        ("system-settings.json", "config/system/settings.json"),
    ):
        install(ASSETS / name, plumos / target)
    install(Path("board/rg280v/overlay/etc/udev/rules.d/70-plumos-gpio-keys.rules"),
            plumos / "config/70-plumos-gpio-keys.rules")
    install(Path("src/frontend/LICENSE.V90S"), plumos / "licenses/plumOS-frontend-MIT.txt")
    for name in (
        "LICENSE", "THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.ja.md",
        "docs/developer/emulator-licenses.md", "docs/developer/emulator-licenses.ja.md",
        "docs/validation/jz47xx-v0.1.0-release-rights.md",
        "docs/validation/jz47xx-v0.1.0-release-rights.ja.md",
    ):
        install(Path(name), plumos / "licenses" / name)
    for source in (APPS / "runtime-lib").glob("*-LICENSE.txt"):
        install(source, plumos / "licenses" / source.name)
    install(EMULATORS / "picoarch-source/LICENSE", plumos / "licenses/PicoArch-LICENSE")
    install(EMULATORS / "pcsx4all-source/gpl.txt", plumos / "licenses/PCSX4ALL-GPL.txt")
    source_trees = {name: EMULATORS / "picoarch-cores" / name for name in CORES}
    source_trees.update({
        "FCEUX": EMULATORS / "fceux266-source",
        "Gambatte-DMS": EMULATORS / "gambatte-dms-source",
        "PicoDrive": EMULATORS / "picodrive-source",
        "Beetle-PCE-Fast": EMULATORS / "beetle-pce-fast-source",
    })
    for component, source in source_trees.items():
        if source.is_dir():
            for notice in sorted(source.iterdir()):
                if notice.is_file() and re.fullmatch(r"(?i)(license|copying)(?:\.txt|\.md)?", notice.name):
                    install(notice, plumos / "licenses" / component / notice.name)

    catalog = json.loads((ASSETS / "systems.json").read_text())
    allowed = {f"standalone:{name}" for name in (*STANDALONE, *OPKS, "pcsx4all")}
    allowed.update(f"picoarch:{name}" for name in CORES)
    for system in catalog["systems"]:
        profiles = [profile for profile in system["launch_profiles"] if profile in allowed]
        if system["id"] == "gba":
            profiles = ["picoarch:vbam"]
        if not profiles:
            system["enabled"] = False
        system["launch_profiles"] = profiles
        if profiles and system.get("default_launch_profile") not in profiles:
            system["default_launch_profile"] = profiles[0]
    config = plumos / "config/frontend"
    (config / "systems.json").write_text(json.dumps(catalog, indent=2) + "\n")
    # The controller UI discovers OPK apps from their desktop entries.
    install(ASSETS / "apps.json", config / "apps.json")
    enabled = [system for system in catalog["systems"] if system["enabled"]]
    print(f"Catalog: {len(enabled)} systems, {sum(len(system['launch_profiles']) for system in enabled)} routes")
    print("Held back:", ", ".join(system["id"] for system in catalog["systems"] if not system["enabled"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tree", type=Path)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    if args.stage:
        stage_runtime(args.tree, args.stage)
    print(f"Audited {audit_tree(args.tree)} regular files")


if __name__ == "__main__":
    main()
