#!/usr/bin/env python3
"""Stage isolated RG350 OPK visual comparisons in the RG280V Apps menu.

Only the explicit test files below are copied. ROMs and legacy libraries stay
outside Git and outside the normal emulator/FE paths.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROM_ROOT = pathlib.Path("<local-path>")
REMOTE = "/media/data/local/rg350-visual-tests"
APPS = "/media/data/plumos/config/frontend/apps.json"
ADB = ["adb", "-P", "5041", "-s", "10.1.1.2:5555"]
TESTS = [
    ("atari_caverns", "Atari Caverns", "atari.opk", "atari/CavernsOfMars.rom", "ATARI/800/CavernsOfMars.rom"),
    ("atari_miner", "Atari Miner 2049er", "atari.opk", "atari/Miner2049er.rom", "ATARI/800/Miner2049er.rom"),
    ("atari_food", "Atari Food Fight", "atari.opk", "atari/FoodFight.rom", "ATARI/800/FoodFight.rom"),
    ("fba_kungfum", "FBA Kung-Fu Master", "fba.opk", "fba/kungfum.zip", "fbneo/kungfum.zip"),
    ("fba_bchopper", "FBA Battle Chopper", "fba.opk", "fba/bchopper.zip", "fbneo/bchopper.zip"),
    ("fba_nspirit", "FBA Ninja Spirit", "fba.opk", "fba/nspirit.zip", "fbneo/nspirit.zip"),
    ("temper_airzonk", "Temper Air Zonk", "temper.opk", "", "pcengine/AirZonk_U.pce"),
    ("temper_blazing", "Temper Blazing Lazers", "temper.opk", "", "pcengine/BlazingLazers_U.pce"),
    ("temper_bonk", "Temper Bonk Revenge", "temper.opk", "", "pcengine/BONKs_REVENGE.PCE"),
]
OPKS = {
    "atari.opk": ROOT / "output/rg280v-apps/rg350-catalog/Atari800_2020-02-14.opk",
    "fba.opk": ROOT / "output/rg280v-apps/fba44-romarg-test.opk",
    "temper.opk": ROOT / "output/rg280v-apps/rg350-catalog/Temper_2016-10-20.opk",
}
LIBS = ["libreadline.so.6", "libncurses.so.5", "libncursesw.so",
        "libcrypto.so.1.0.0", "libao.so.4"]
WRAPPER = ROOT / "assets/frontend/bin/plumos-rg350-visual-test"


def run(*args, input_text=None):
    result = subprocess.run(args, input=input_text, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{args!r}: {result.stderr or result.stdout}")
    return result.stdout


def shell(command):
    return run(*ADB, "shell", command)


def push(source, dest):
    run(*ADB, "push", str(source), dest)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    result = shell(f"sha256sum '{dest}'")
    if result.split()[0] != source_hash:
        raise RuntimeError(f"hash mismatch: {dest}")
    print(f"verified {dest}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", action="store_true", help="remove only visual-test entries and files")
    args = parser.parse_args()
    if shell("test -f '" + APPS + "' && echo yes").strip() != "yes":
        raise RuntimeError("device apps.json missing")
    current = json.loads(shell("cat '" + APPS + "'"))
    out = ROOT / "output/rg280v-apps/rg350-visual-tests"
    out.mkdir(parents=True, exist_ok=True)
    if not args.remove and not (out / "apps-before.json").exists():
        (out / "apps-before.json").write_text(json.dumps(current, indent=2) + "\n")
    if args.remove:
        current["apps"] = [x for x in current["apps"] if not x.get("id", "").startswith("rg350_test_")]
        shell("rm -rf '" + REMOTE + "'")
    else:
        files = {"bin/plumos-rg350-visual-test": WRAPPER}
        files.update(("opk/" + name, path) for name, path in OPKS.items())
        files.update(("lib/" + name, ROOT / "output/rg280v-emulators/legacy-lib" / name) for name in LIBS)
        for ident, _, _, rom, source in TESTS:
            if rom:
                files["rom/" + rom] = ROM_ROOT / source
        for _, name, _, rom, source in TESTS:
            if not rom:
                # Temper uses the already populated SD2 PC Engine collection.
                if shell("test -f '/media/data/sd2/roms/" + source + "' && echo yes").strip() != "yes":
                    raise RuntimeError(f"SD2 ROM missing: {source}")
        missing = [str(path) for path in files.values() if not path.is_file()]
        if missing:
            raise RuntimeError("missing sources: " + ", ".join(missing))
        for relative, path in files.items():
            dest = REMOTE + "/" + relative
            shell("mkdir -p '" + str(pathlib.PurePosixPath(dest).parent) + "'")
            push(path, dest)
        shell("chmod 755 '" + REMOTE + "/bin/plumos-rg350-visual-test'")
        current["apps"] = [x for x in current["apps"] if not x.get("id", "").startswith("rg350_test_")]
        current["apps"].extend({
            "id": "rg350_test_" + ident,
            "display_name": "TEST " + name,
            "menu": "apps", "kind": "shell", "visible": True,
            "launch_profile": "shell:" + REMOTE + "/bin/plumos-rg350-visual-test " + ident,
        } for ident, name, *_ in TESTS)
    (out / "apps-applied.json").write_text(json.dumps(current, indent=2) + "\n")
    payload = json.dumps(current, ensure_ascii=False, separators=(",", ":")) + "\n"
    local_apps = out / "apps-upload.json"
    local_apps.write_text(payload)
    push(local_apps, APPS + ".tmp")
    shell("mv '" + APPS + ".tmp' '" + APPS + "'")
    check = json.loads(shell("cat '" + APPS + "'"))
    if check != current:
        raise RuntimeError("apps.json verification failed")
    print("Apps entries verified:", len([a for a in check["apps"] if a["id"].startswith("rg350_test_")]))
    print("Open START > Apps to refresh the list.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
