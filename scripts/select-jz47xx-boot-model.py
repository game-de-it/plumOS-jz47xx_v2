#!/usr/bin/env python3
"""Select a DTB on a mounted test boot volume; never access raw devices."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil


def select_model(boot, model):
    boot = boot.resolve(strict=True)
    for name in ("rootfs.squashfs", "modules.squashfs", "mininit-syspart", "uzImage.bin"):
        if not (boot / name).is_file():
            raise ValueError(f"Not a prepared plumOS boot volume: missing {name}")
    source = boot / "models" / f"{model}.bin"
    expected = dict(line.split(maxsplit=1)[::-1] for line in
                    (boot / "models" / "SHA256SUMS").read_text().splitlines())
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if expected.get(source.name) != digest or data[:4] != bytes.fromhex("27051956"):
        raise ValueError("Model kernel checksum/header mismatch")
    target = boot / "uzImage.bin"
    backup = boot / "uzImage.previous.bin"
    if not backup.exists():
        shutil.copyfile(target, backup)
    staging = boot / "uzImage.selecting"
    with staging.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if hashlib.sha256(staging.read_bytes()).hexdigest() != digest:
        raise ValueError("Staged kernel verification failed")
    os.replace(staging, target)
    (boot / "model.txt").write_text(model + "\n")
    os.sync()
    if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
        raise ValueError("Selected kernel verification failed")
    print(f"Selected {model}: {digest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boot-volume", required=True, type=Path)
    parser.add_argument("--model", required=True, choices=("rg300x", "rg350", "rg280v", "rg350m"))
    args = parser.parse_args()
    select_model(args.boot_volume, args.model)
