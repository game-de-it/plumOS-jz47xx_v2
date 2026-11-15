#!/usr/bin/env python3
"""Run short, reversible FCEUX A/B measurements on the connected RG280V."""
import hashlib
import re
import statistics
import subprocess
import time
from pathlib import Path

ADB = ["adb", "-P", "5039", "-s", "10.1.1.2:5555"]
REPO = Path(__file__).resolve().parents[1]
BACKUP = REPO / "output/validation/rg280v-fceux-performance-20261116/backup/akumajou.cfg"
CONFIG = "/media/data/plumos/home/.fceux/cfg/Akumajou Densetsu.cfg"
ROM = "/media/data/sd2/roms/nes/Akumajou Densetsu.nes"
LOG_DIR = "/media/data/plumos/Logs"


def adb(*args, timeout=30):
    return subprocess.run(ADB + list(args), check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=timeout).stdout


def variant(name, edits):
    config = BACKUP.read_text()
    for key, val in edits.items():
        pattern = rf"(?m)^{re.escape(key)} = .*?$"
        config, count = re.subn(pattern, f"{key} = {val}", config)
        if count != 1:
            raise RuntimeError(f"{key}: expected one config line, got {count}")
    local = BACKUP.parent / f"{name}.cfg"
    local.write_text(config)
    adb("push", str(local), CONFIG)
    log = f"{LOG_DIR}/fceux-flip-{name}.tsv"
    adb("shell", f"rm -f {log}")
    cmd = ("LD_PRELOAD=/media/data/plumos/lib/libfceux-flip-probe.so "
           f"PLUMOS_FCEUX_FLIP_LOG={log} "
           "/media/data/plumos/bin/rg280v-smoke-watchdog 12 "
           f"/media/data/plumos/bin/plumos-standalone-launch fceux '{ROM}'")
    output = adb("shell", cmd, timeout=30)
    print(name, "run_tail:", " | ".join(output.splitlines()[-4:]), flush=True)
    rows = [line.split() for line in adb("shell", f"cat {log}").splitlines() if line.strip()]
    fps = [float(row[2]) for row in rows[1:]]
    flip = [float(row[3]) for row in rows[1:]]
    print(name, "rows:", rows, flush=True)
    print(name, "steady_fps:", round(statistics.mean(fps), 2),
          "flip_ms:", round(statistics.mean(flip), 3), flush=True)


def main():
    original = BACKUP.read_bytes()
    expected = hashlib.sha256(original).hexdigest()
    remote = adb("shell", f"sha256sum '{CONFIG}'").split()[0]
    if remote != expected:
        raise RuntimeError(f"live config differs from backup: {remote} != {expected}")
    print("backup_sha256:", expected, flush=True)
    try:
        adb("shell", "/media/data/local/init.d/S95frontend stop")
        variant("sound-off", {"SDL.Sound": "0"})
        variant("sound-32k", {"SDL.Sound.Rate": "32000"})
        variant("frameskip-6", {"SDL.Frameskip": "6"})
    finally:
        adb("push", str(BACKUP), CONFIG)
        remote = adb("shell", f"sha256sum '{CONFIG}'")
        print("restored:", remote.strip(), flush=True)
        adb("shell", "/media/data/local/init.d/S95frontend start")
        for _ in range(10):
            process = adb("shell", "ps | grep '[p]lumos-controller-ui'").strip()
            if process:
                print("frontend:", process, flush=True)
                break
            time.sleep(1)
        else:
            adb("shell", "/media/data/local/init.d/S95frontend restart")
            time.sleep(3)
            print("frontend:", adb("shell", "ps | grep '[p]lumos-controller-ui'").strip(), flush=True)


if __name__ == "__main__":
    main()
