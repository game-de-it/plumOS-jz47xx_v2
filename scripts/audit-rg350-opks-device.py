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
import threading
import hashlib

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
    return subprocess.run(args, text=True, errors="replace", capture_output=True, **kwargs)


def shell(script, **kwargs):
    return cmd(ADB + ["shell", script], **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=62)
    parser.add_argument("--seconds", type=int, default=8)
    parser.add_argument("--screenshot-delay", type=float, default=3.0)
    parser.add_argument("--sdl-driver", default="kmsdrm", choices=("kmsdrm", "fbcon"))
    parser.add_argument("--trace", action="store_true", help="Collect file/process/signal syscalls for startup failures")
    parser.add_argument("--preload", default="", help="Additional remote LD_PRELOAD library")
    parser.add_argument("--tag", default="", help="Suffix for the ignored evidence directory")
    parser.add_argument("--only", type=int, nargs="*", help="Catalog positions to retest")
    parser.add_argument("--fe-env", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--raw-env", action="store_true", help="Diagnostic only: omit the frontend environment")
    parser.add_argument("--extra-lib-dir", default="", help="Additional remote library directory for isolated tests")
    parser.add_argument("--rom", action="append", default=[], metavar="NUMBER=REMOTE_PATH",
                        help="Override the ROM path for a catalog entry")
    parser.add_argument("--opk", action="append", default=[], metavar="NUMBER=LOCAL_PATH",
                        help="Use a locally modified OPK for a catalog entry")
    parser.add_argument("--start-presses", type=int, default=0,
                        help="Inject START repeatedly at 3 second intervals after launch")
    parser.add_argument("--key-event", action="append", default=[],
                        help="Inject SECONDS:KEYCODE:DURATION_MS[:SECOND_KEYCODE]")
    args = parser.parse_args()
    key_events = [(3 * (i + 1), 28, 120, None) for i in range(args.start_presses)]
    for value in args.key_event:
        parts = value.split(":")
        if len(parts) not in (3, 4):
            parser.error("--key-event requires SECONDS:KEYCODE:DURATION_MS[:SECOND_KEYCODE]")
        key_events.append((float(parts[0]), int(parts[1]), int(parts[2]),
                           int(parts[3]) if len(parts) == 4 else None))
    key_events.sort()
    overrides = {}
    for item in args.rom:
        number, separator, path = item.partition("=")
        if not separator or not number.isdigit() or not path.startswith("/"):
            parser.error("--rom requires NUMBER=/absolute/remote/path")
        overrides[int(number)] = path
    opk_overrides = {}
    for item in args.opk:
        number, separator, path = item.partition("=")
        if not separator or not number.isdigit() or not pathlib.Path(path).is_file():
            parser.error("--opk requires NUMBER=existing/local/path")
        opk_overrides[int(number)] = pathlib.Path(path)
    audit = json.loads((ROOT / "output/rg280v-apps/rg350-catalog-audit.json").read_text())
    out = ROOT / "output/rg280v-apps" / ("rg350-device-audit" + ("-" + args.tag if args.tag else ""))
    out.mkdir(parents=True, exist_ok=True)
    results = out / "results.jsonl"
    results.write_text("")
    env = dict(os.environ, ADB_SERVER_PORT="5041")
    for number, item in enumerate(audit, 1):
        if not args.start <= number <= args.end:
            continue
        if args.only and number not in args.only:
            continue
        name = item["name"]
        path = opk_overrides.get(number, ROOT / "output/rg280v-apps/rg350-catalog" / name)
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
        cleared = shell("rm -f " + shlex.quote(remote_log) + " " + shlex.quote(remote_out), env=env)
        if cleared.returncode:
            raise RuntimeError(f"cannot clear stale probe files for {number}: {cleared.stderr}")
        rom = overrides.get(number, f"{BASE}/{ROM[number]}" if number in ROM else None)
        library_path = (args.extra_lib_dir + ":" if args.extra_lib_dir else "") + "/media/data/plumos/lib"
        launch_env = ("PLUMOS_ROOT=/media/data/plumos HOME=/media/data/plumos/home "
                      "SDL_VIDEODRIVER=" + args.sdl_driver + " LD_LIBRARY_PATH=" +
                      shlex.quote(library_path) + " ") if not args.raw_env else "HOME=/media/data/local "
        preloads = ["/media/data/plumos/lib/libstandalone-health.so"]
        if args.preload:
            preloads.append(args.preload)
        call = (launch_env + "PLUMOS_STANDALONE_HEALTH_LOG=" + shlex.quote(remote_log) +
                " LD_PRELOAD=" + shlex.quote(":".join(preloads)) + " " +
                (("strace -f -e trace=file,process,signal -o /tmp/rg350-source-trace-" + str(number) + " ") if args.trace else "") +
                "/media/data/local/rg280v-opk-timeout " + str(args.seconds) + " " +
                shlex.quote(remote) + (" " + shlex.quote(rom) if rom else "") +
                " >" + shlex.quote(remote_out) + " 2>&1; echo RC=$?")
        started = time.monotonic()
        process = subprocess.Popen(ADB + ["shell", call], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=env)
        input_done = threading.Event()
        def advance_game():
            for offset, keycode, duration, second in key_events:
                if input_done.wait(max(0, started + offset - time.monotonic())):
                    return
                command = f"/media/data/plumos/bin/rg280v-inject-key /dev/input/event2 {keycode} {duration}"
                if second is not None:
                    command += f" {second}"
                shell(command, env=env)
        input_thread = threading.Thread(target=advance_game, daemon=True)
        input_thread.start()
        capture_at = time.monotonic() + args.screenshot_delay
        while process.poll() is None and time.monotonic() < capture_at:
            time.sleep(0.1)
        screenshot = None
        if process.poll() is None:
            screenshot = cmd([str(ROOT / "scripts/capture-rg280v-drm.sh"), str(png)],
                             env=env, timeout=20)
        try:
            stdout, stderr = process.communicate(timeout=args.seconds + 20)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        input_done.set()
        input_thread.join()
        output = shell("cat " + shlex.quote(remote_out) + "; cat " + shlex.quote(remote_log), env=env)
        log.write_text(output.stdout + "\n" + output.stderr)
        if args.trace:
            trace = shell("cat /tmp/rg350-source-trace-" + str(number), env=env)
            (out / f"{number:02d}.strace").write_text(trace.stdout + trace.stderr)
        shell("/media/data/local/init.d/S95frontend start", env=env)
        time.sleep(1)
        check = shell("ps | grep plumos-controller | grep -v grep", env=env)
        if not check.stdout.strip():
            shell("/media/data/local/init.d/S95frontend restart", env=env)
            for _ in range(10):
                time.sleep(1)
                check = shell("ps | grep plumos-controller | grep -v grep", env=env)
                if check.stdout.strip():
                    break
            if not check.stdout.strip():
                shell("/media/data/local/init.d/S95frontend restart", env=env)
                time.sleep(2)
                check = shell("ps | grep plumos-controller | grep -v grep", env=env)
        shell("rm -f " + shlex.quote(remote), env=env)
        telemetry = output.stdout
        child_exits = [int(x) for x in re.findall(r"PLUMOS_EMULATOR_EXIT=(\d+)", output.stdout)]
        # Several old OPKs overwrite the health hook's state. Discard impossible rates.
        fps = [value for value in (float(raw) for raw in re.findall(r"fps_window=([0-9.]+)", telemetry))
               if 0 < value <= 240]
        audio = re.findall(r"audio[^\n]*", telemetry)
        audio_signal = any(int(peak) > 0 for peak in re.findall(r"audio[^\n]*peak=(\d+)", telemetry))
        ranges = re.findall(r"audio[^\n]*min=(-?\d+)\tmax=(-?\d+)", telemetry)
        if ranges:
            audio_signal = audio_signal and any(int(high) - int(low) >= 128 for low, high in ranges)
        runtime_errors = [line for line in telemetry.splitlines()
                          if re.search(r"Segmentation fault|Signal 11|[Aa]ssertion .*failed|ALSA write failed|No available video device|No exec image found|Accessing a corrupted shared library", line)]
        if re.search(r"RC=(10|11|13[459])$", stdout.decode(errors="replace").strip()):
            runtime_errors.append("Abnormal process exit: " + stdout.decode(errors="replace").strip())
        if any(child_exits):
            runtime_errors.append("Emulator returned " + str(child_exits))
        signal = "signal" if audio_signal else ("silent callback" if audio else "none")
        if ranges and not audio_signal and any(int(low) == int(high) != 0 for low, high in ranges):
            signal = "constant/DC output"
        record = {"number": number, "name": name, "rom": rom, "elapsed_s": round(time.monotonic()-started, 1),
                  "tested_opk": str(path), "tested_opk_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "exit": stdout.decode(errors="replace").strip(),
                  "emulator_exits": child_exits, "fps_windows": fps, "audio": audio[-1] if audio else None,
                  "audio_signal": audio_signal,
                  "audio_assessment": signal,
                  "runtime_errors": runtime_errors,
                  "key_events": key_events,
                  "screenshot": str(png) if screenshot is not None and screenshot.returncode == 0 else None,
                  "log": str(log), "fe_restored": bool(check.stdout.strip())}
        with results.open("a") as fh: fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"{number:02d}/62 {name}: {record['exit']} fps={fps[-2:]} audio={signal} FE={record['fe_restored']}", flush=True)
    shell("/media/data/local/init.d/S95frontend start", env=env)


if __name__ == "__main__":
    main()
