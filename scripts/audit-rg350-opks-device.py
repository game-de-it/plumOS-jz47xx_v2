#!/usr/bin/env python3
"""Sequential, time-limited RG280V smoke test of the RG350 OPK catalog."""
import argparse
import json
import os
import pathlib
import re
import shlex
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ["adb", "-P", "5041", "-s", "10.1.1.2:5555"]
BASE = "/media/data/sd2/roms"
ROM = {
    11: "nes/Baseball.nes", 12: "megadrive/Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md",
    16: "nes/Baseball.nes", 18: "wonderswan/Armored Unit (J).ws",
    19: "megadrive/Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md",
    20: "snes/Adventures of the Rocketeer.sfc", 24: "ngpc/Baseball Stars Color (World) (En,Ja).ngc",
    25: "ngpc/Baseball Stars Color (World) (En,Ja).ngc",
    26: "gba/Castlevania - Aria of Sorrow (European Version - Restored Audio).gba",
    27: "snes/Adventures of the Rocketeer.sfc", 29: "pcengine/AirZonk_U.pce",
    35: "gb/Aretha (Japan).gb", 36: "gb/Aretha (Japan).gb",
    37: "gb/Aretha (Japan).gb", 38: "gbc/Akumanor Gaiden DX v1.0.gbc",
    40: "gba/Castlevania - Aria of Sorrow (European Version - Restored Audio).gba",
    43: "mame/1942a.zip", 44: "mame/1942a.zip",
    46: "pcengine/AirZonk_U.pce", 49: "gb/Aretha (Japan).gb",
    51: "psx/GUNDAM_CHARs_Counter_Attack_taikenban.cue",
    52: "sega32x/After Burner (Japan, USA).32x",
    53: "segacd/Fatal Fury Special (Europe) (Demo).chd",
    54: "megadrive/Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md",
    57: "gamegear/Columns [V1.0].gg", 58: "mastersystem/Frontier Force (V1.1).sms",
}


def cmd(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, **kwargs)


def shell(script, **kwargs):
    return cmd(ADB + ["shell", script], **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=62)
    parser.add_argument("--seconds", type=int, default=8)
    parser.add_argument("--tag", default="", help="Suffix for the ignored evidence directory")
    parser.add_argument("--only", type=int, nargs="*", help="Catalog positions to retest")
    parser.add_argument("--fe-env", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--raw-env", action="store_true", help="Diagnostic only: omit the frontend environment")
    parser.add_argument("--extra-lib-dir", default="", help="Additional remote library directory for isolated tests")
    args = parser.parse_args()
    audit = json.loads((ROOT / "output/rg280v-apps/rg350-catalog-audit.json").read_text())
    out = ROOT / "output/rg280v-apps" / ("rg350-device-audit" + ("-" + args.tag if args.tag else ""))
    out.mkdir(parents=True, exist_ok=True)
    results = out / "results.jsonl"
    env = dict(os.environ, ADB_SERVER_PORT="5041")
    for number, item in enumerate(audit, 1):
        if not args.start <= number <= args.end:
            continue
        if args.only and number not in args.only:
            continue
        name = item["name"]
        path = ROOT / "output/rg280v-apps/rg350-catalog" / name
        log = out / f"{number:02d}.log"
        png = out / f"{number:02d}.png"
        remote = "/media/data/local/rg350-audit-candidate.opk"
        pushed = cmd(ADB + ["push", str(path), remote], env=env)
        if pushed.returncode:
            record = {"number": number, "name": name, "error": pushed.stderr.strip()}
            with results.open("a") as fh: fh.write(json.dumps(record) + "\n")
            print(f"{number:02d}/62 {name}: push failed", flush=True)
            continue
        shell("/media/data/local/init.d/S95frontend stop", env=env)
        remote_log = f"/tmp/rg350-audit-{number:02d}.tsv"
        remote_out = f"/tmp/rg350-audit-{number:02d}.out"
        rom = f"{BASE}/{ROM[number]}" if number in ROM else None
        library_path = (args.extra_lib_dir + ":" if args.extra_lib_dir else "") + "/media/data/plumos/lib"
        launch_env = ("PLUMOS_ROOT=/media/data/plumos HOME=/media/data/plumos/home "
                      "SDL_VIDEODRIVER=kmsdrm LD_LIBRARY_PATH=" + shlex.quote(library_path) + " ") if not args.raw_env else "HOME=/media/data/local "
        call = (launch_env + "PLUMOS_STANDALONE_HEALTH_LOG=" + shlex.quote(remote_log) +
                " LD_PRELOAD=/media/data/plumos/lib/libstandalone-health.so " +
                "/media/data/local/rg280v-opk-timeout " + str(args.seconds) + " " +
                shlex.quote(remote) + (" " + shlex.quote(rom) if rom else "") +
                " >" + shlex.quote(remote_out) + " 2>&1; echo RC=$?")
        started = time.monotonic()
        process = subprocess.Popen(ADB + ["shell", call], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=env)
        time.sleep(3)
        screenshot = cmd([str(ROOT / "scripts/capture-rg280v-drm.sh"), str(png)],
                         env=env, timeout=20)
        try:
            stdout, stderr = process.communicate(timeout=args.seconds + 20)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        output = shell("cat " + shlex.quote(remote_out) + "; cat " + shlex.quote(remote_log), env=env)
        log.write_text(output.stdout + "\n" + output.stderr)
        shell("/media/data/local/init.d/S95frontend start", env=env)
        time.sleep(1)
        check = shell("ps | grep plumos-controller | grep -v grep", env=env)
        if not check.stdout.strip():
            shell("/media/data/local/init.d/S95frontend restart", env=env)
            time.sleep(1)
            check = shell("ps | grep plumos-controller | grep -v grep", env=env)
        shell("rm -f " + shlex.quote(remote), env=env)
        telemetry = output.stdout
        # Several old OPKs overwrite the health hook's state. Discard impossible rates.
        fps = [value for value in (float(raw) for raw in re.findall(r"fps_window=([0-9.]+)", telemetry))
               if 0 < value <= 240]
        audio = re.findall(r"audio[^\n]*", telemetry)
        record = {"number": number, "name": name, "rom": rom, "elapsed_s": round(time.monotonic()-started, 1),
                  "exit": stdout.decode(errors="replace").strip(),
                  "fps_windows": fps, "audio": audio[-1] if audio else None,
                  "screenshot": str(png) if screenshot.returncode == 0 else None,
                  "log": str(log), "fe_restored": bool(check.stdout.strip())}
        with results.open("a") as fh: fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{number:02d}/62 {name}: {record['exit']} fps={fps[-2:]} audio={'yes' if audio else 'no'} FE={record['fe_restored']}", flush=True)
    shell("/media/data/local/init.d/S95frontend start", env=env)


if __name__ == "__main__":
    main()
