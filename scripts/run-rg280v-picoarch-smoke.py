#!/usr/bin/env python3
"""Bounded PicoArch ROM smoke tests with DRM captures and audio/frame metrics."""

import argparse
import json
import os
import re
import shlex
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parent.parent
REMOTE = "/media/data/plumos"


def adb(args, timeout=20, check=True):
    command = ["adb", "-P", "5039", "-s", "10.1.1.2:5555", *args]
    return subprocess.run(command, capture_output=True, text=True,
                          timeout=timeout, check=check)


def shell(command, timeout=20, check=True):
    return adb(["shell", command], timeout=timeout, check=check)


def image_metrics(path):
    with Image.open(path) as original:
        image = original.convert("RGB")
        pixels = list(image.get_flattened_data())
        visible = sum(max(pixel) >= 16 for pixel in pixels)
        stats = ImageStat.Stat(image)
        return {
            "size": list(image.size),
            "nonblack_fraction": round(visible / len(pixels), 4),
            "mean_rgb": [round(value, 2) for value in stats.mean],
            "unique_colors": len(set(pixels)),
        }


def parse_health(text):
    result = {"video": [], "audio": []}
    for line in text.splitlines():
        fields = line.split("\t")
        if fields[0] not in result:
            continue
        record = {}
        for field in fields[1:]:
            if "=" not in field:
                continue
            key, value = field.split("=", 1)
            try:
                record[key] = float(value)
            except ValueError:
                record[key] = value
        result[fields[0]].append(record)
    return result


def run_one(entry, out_dir, seconds):
    core = entry["core"]
    if not re.fullmatch(r"[A-Za-z0-9_]+", core):
        raise ValueError(core)
    system = entry["system"]
    source = entry["source"]
    local_path = Path(entry["path"])
    remote_rom = entry["path"]
    staged = None
    if source == "rom2":
        staged = f"{REMOTE}/smoke/roms/{core}"
        remote_rom = f"{staged}/{local_path.name}"
        shell(f"mkdir -p {shlex.quote(staged)}")
        adb(["push", str(local_path), remote_rom], timeout=120)

    remote_log = f"{REMOTE}/Logs/picoarch/health-{core}.tsv"
    command = (
        f": > {shlex.quote(remote_log)}; "
        f"export PLUMOS_PICOARCH_HEALTH_LOG={shlex.quote(remote_log)} "
        f"LD_PRELOAD={shlex.quote(REMOTE + '/lib/libpicoarch-health.so')} "
        f"PLUMOS_PICOARCH_SYSTEM={shlex.quote(system)}; "
        f"{REMOTE}/bin/rg280v-smoke-watchdog {seconds} "
        f"{REMOTE}/bin/plumos-picoarch-launch {core} {shlex.quote(remote_rom)}; "
        "echo WATCHDOG_RC=$?"
    )
    process = subprocess.Popen(
        ["adb", "-P", "5039", "-s", "10.1.1.2:5555", "shell", command],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    captures = []
    for index, wait_until in enumerate((3.5, 7.0), start=1):
        elapsed = time.monotonic()
        # Tests are launched immediately before this loop; time relative to
        # first capture is enough for gross visual checks.
        if index == 1:
            start = elapsed
        sleep_for = wait_until - (time.monotonic() - start)
        if sleep_for > 0:
            time.sleep(sleep_for)
        if process.poll() is not None:
            break
        path = out_dir / f"{core}-{index}.png"
        capture = subprocess.run(
            [str(ROOT / "scripts/capture-rg280v-drm.sh"), str(path)],
            env={**os.environ, "ADB_SERVER_PORT": "5039"},
            capture_output=True, text=True, timeout=12,
        )
        if capture.returncode == 0 and path.is_file():
            captures.append({"file": str(path), **image_metrics(path)})
    try:
        stdout, stderr = process.communicate(timeout=seconds + 12)
    except subprocess.TimeoutExpired:
        process.terminate()
        raise RuntimeError(f"ADB shell timed out during {core}")

    local_log = out_dir / f"{core}-health.tsv"
    pulled = adb(["pull", remote_log, str(local_log)], check=False)
    health = parse_health(local_log.read_text()) if pulled.returncode == 0 else {}
    if staged:
        shell(f"rm -r {shlex.quote(staged)}", check=False)
    result = {
        "core": core, "system": system, "source": source,
        "rom_name": local_path.name, "adb_returncode": process.returncode,
        "runner_output": stdout.strip(), "runner_error": stderr.strip(),
        "captures": captures, "health": health,
    }
    video = health.get("video", [])
    audio = health.get("audio", [])
    result["last_fps_window"] = video[-1].get("fps_window") if video else None
    result["last_audio_zero_fraction"] = audio[-1].get("zero_frac") if audio else None
    result["screen_blank"] = bool(captures) and all(
        capture["unique_colors"] == 1 for capture in captures
    )
    return result


def restore_frontend():
    # Keep the ADB shell alive while the frontend detaches. A start in a
    # short-lived shell repeatedly left no process after that shell exited.
    for _ in range(3):
        started = shell("/media/data/local/init.d/S95frontend start; sleep 6; "
                        "ps | grep '[p]lumos-controller-ui'", timeout=20,
                        check=False)
        if "plumos-controller-ui --render" in started.stdout:
            return True
        shell("/media/data/local/init.d/S95frontend stop", timeout=10, check=False)
        time.sleep(2)
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--cores", help="comma-separated core IDs")
    parser.add_argument("--seconds", type=int, default=11)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    chosen = set(args.cores.split(",")) if args.cores else None
    entries = [entry for entry in json.loads(args.plan.read_text())
               if entry["status"] == "planned" and
               (chosen is None or entry["core"] in chosen)]
    if args.limit:
        entries = entries[:args.limit]
    results_path = args.out_dir / "results.jsonl"
    already = set()
    if results_path.exists():
        already = {json.loads(line)["core"] for line in results_path.read_text().splitlines()}
    shell("/media/data/local/init.d/S95frontend stop", timeout=15)
    try:
        for entry in entries:
            if entry["core"] in already:
                continue
            print("TEST", entry["core"], entry["system"], flush=True)
            result = run_one(entry, args.out_dir, args.seconds)
            with results_path.open("a") as out:
                out.write(json.dumps(result, ensure_ascii=False) + "\n")
            print("RESULT", entry["core"], result["last_fps_window"],
                  result["last_audio_zero_fraction"], result["screen_blank"],
                  result["runner_output"], flush=True)
            if "process remained after SIGKILL" in result["runner_output"]:
                raise RuntimeError("device process did not stop")
    finally:
        if not restore_frontend():
            print("FRONTEND_RESTORE_FAILED", flush=True)


if __name__ == "__main__":
    main()
