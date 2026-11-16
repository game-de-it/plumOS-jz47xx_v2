#!/usr/bin/env python3
"""Inventory RG350 OPK launchers and ELF dependencies without retaining extraction."""

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile


def run(*args):
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    return result.returncode, result.stdout, result.stderr


def inspect_elf(path):
    _, header, _ = run("readelf", "-h", str(path))
    _, attributes, _ = run("readelf", "-A", str(path))
    _, dynamic, _ = run("readelf", "-d", str(path))
    flags = re.search(r"Flags:\s*(.*)", header)
    fp_abi = re.search(r"FP ABI:\s*(.*)", attributes)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "type": "dynamic" if "INTERP" in run("readelf", "-l", str(path))[1] else "static",
        "flags": flags.group(1) if flags else None,
        "fp_abi": fp_abi.group(1) if fp_abi else "untagged",
        "needed": re.findall(r"Shared library: \[(.*?)\]", dynamic),
    }


def inspect_opk(opk, unsquashfs):
    entry = {"name": opk.name, "bytes": opk.stat().st_size}
    digest = hashlib.sha256()
    with opk.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    entry["sha256"] = digest.hexdigest()
    with tempfile.TemporaryDirectory(prefix="rg350-opk-", dir=opk.parent) as temporary:
        root = pathlib.Path(temporary)
        code, _, error = run(str(unsquashfs), "-f", "-no-progress", "-d", str(root), str(opk))
        if code:
            entry["error"] = error.strip()[-500:]
            return entry
        entry["desktop"] = []
        entry["elf"] = []
        for path in root.rglob("*"):
            if path.is_file() and path.suffix == ".desktop":
                text = path.read_text(encoding="utf-8", errors="replace")
                entry["desktop"].append({
                    "path": str(path.relative_to(root)),
                    "name": re.search(r"^Name=(.*)$", text, re.M).group(1)
                    if re.search(r"^Name=(.*)$", text, re.M) else None,
                    "exec": re.search(r"^Exec=(.*)$", text, re.M).group(1)
                    if re.search(r"^Exec=(.*)$", text, re.M) else None,
                })
            elif path.is_file() and path.stat().st_size >= 4:
                with path.open("rb") as stream:
                    if stream.read(4) != b"\x7fELF":
                        continue
                elf = inspect_elf(path)
                elf["path"] = str(path.relative_to(root))
                entry["elf"].append(elf)
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--unsquashfs", type=pathlib.Path, required=True)
    args = parser.parse_args()
    entries = []
    for opk in sorted(args.catalog.glob("*.opk")):
        entry = inspect_opk(opk, args.unsquashfs)
        entries.append(entry)
        print(opk.name, "ELF", len(entry.get("elf", [])), "error", bool(entry.get("error")), flush=True)
    args.output.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n")
    print(f"audited {len(entries)} OPKs -> {args.output}")


if __name__ == "__main__":
    main()
