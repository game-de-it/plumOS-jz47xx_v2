#!/usr/bin/env python3
"""Stage bundled ROMs for PicoArch smoke tests, then remove device copies."""

import argparse
import importlib.util
import json
import os
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROM2 = Path(os.environ.get("PLUMOS_ROM2_ROOT",
                           "<local-path>"))
OUT = ROOT / "output/validation/rg280v-picoarch-20261115/smoke"
REMOTE = "/media/data/plumos/smoke/special"
WANTED = None

spec = importlib.util.spec_from_file_location(
    "picoarch_smoke", ROOT / "scripts/run-rg280v-picoarch-smoke.py"
)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


def push(source, destination):
    smoke.adb(["push", str(source), destination], timeout=180)


def run(core, system, local_files, content):
    if WANTED is not None and core not in WANTED:
        return
    base = f"{REMOTE}/{core}"
    smoke.shell(f"mkdir -p {base}")
    try:
        for source in local_files:
            push(source, base + "/")
        entry = {"core": core, "system": system, "source": "staged",
                 "path": f"{base}/{content}"}
        result = smoke.run_one(entry, OUT, 12)
        result["rom_name"] = content
        with (OUT / "results.jsonl").open("a") as out:
            out.write(json.dumps(result, ensure_ascii=False) + "\n")
        print("RESULT", core, result["runner_output"],
              result["last_fps_window"], result["last_audio_zero_fraction"],
              flush=True)
    finally:
        smoke.shell(f"rm -rf {base}", timeout=30, check=False)


def main():
    global OUT, WANTED
    parser = argparse.ArgumentParser()
    parser.add_argument("--cores", help="comma-separated core IDs")
    parser.add_argument("--out-dir", type=Path, default=OUT)
    args = parser.parse_args()
    OUT = args.out_dir.resolve()
    WANTED = set(args.cores.split(",")) if args.cores else None
    OUT.mkdir(parents=True, exist_ok=True)
    smoke.shell("/media/data/local/init.d/S95frontend stop", timeout=15)
    try:
        with tempfile.TemporaryDirectory(prefix="rg280v-picoarch-special-") as temp:
            temp = Path(temp)
            for core, system, archive, suffix in [
                ("pokemini", "pokemini", ROM2 / "_etc/pokemini/Pichu Bros. Mini (Japan).zip", ".min"),
                ("gw", "gameandwatch", ROM2 / "_etc/gameandwatch/Tennis Menace.zip", ".mgw"),
            ]:
                with zipfile.ZipFile(archive) as zipped:
                    member = next(x for x in zipped.infolist() if x.filename.lower().endswith(suffix))
                    target = temp / Path(member.filename).name
                    target.write_bytes(zipped.read(member))
                run(core, system, [target], target.name)

            pcfx = ROM2 / "_etc/pcfx/SimpleBattle_FX"
            run("mednafen_pcfx", "pcfx", [pcfx / "simplebattle.bin",
                 pcfx / "simplebattle.cue"], "simplebattle.cue")

            cave = ROM2 / "_etc/cavestory/doukutsu"
            run("nxengine", "cavestory", [cave], "doukutsu/Doukutsu.exe")

            scumm = ROM2 / "scummvm/BASS-Floppy-1.3"
            descriptor = temp / "sky.scummvm"
            descriptor.write_text("sky\n")
            run("scummvm", "scummvm", [scumm / "sky.dnr", scumm / "sky.dsk",
                 descriptor], descriptor.name)

            run("pcsx_rearmed", "psx", [ROM2 / "psx/chroQW.img"], "chroQW.img")
            run("opera", "3do", [ROM2 / "_etc/3do/biofury.iso"], "biofury.iso")

            neocd = ROM2 / "_etc/neogeocd/Fatal Fury"
            run("neocd", "neogeocd", [neocd], "Fatal Fury/Fatal Fury.cue")

            run("fbalpha2012_neogeo", "neogeo", [
                ROM2 / "_etc/neogeo/ART OF FIGHTING/aof.zip",
                ROM2 / "bios/neogeo.zip",
            ], "aof.zip")

            dino = ROM2 / "_etc/dinothawr/dinothawr"
            run("dinothawr", "dinothawr", [dino],
                "dinothawr/dinothawr.game")

            outrun_roms = ROM2 / "_etc/cannonball/outrun-roms-master"
            marker = temp / "outrun.game"
            marker.touch()
            run("cannonball", "cannonball", [*outrun_roms.iterdir(), marker],
                marker.name)
    finally:
        print("FRONTEND_RESTORED", smoke.restore_frontend(), flush=True)


if __name__ == "__main__":
    main()
