#!/usr/bin/env python3
"""Summarize RG280V MIPS PC samples using a process map and unstripped core."""

import argparse
from bisect import bisect_right
from collections import Counter
from pathlib import Path
import struct
import subprocess


def read_maps(path: Path):
    mappings = []
    for line in path.read_text().splitlines():
        parts = line.split(maxsplit=5)
        if len(parts) < 5:
            continue
        first, last = (int(value, 16) for value in parts[0].split("-"))
        mappings.append((first, last, int(parts[2], 16), parts[5] if len(parts) > 5 else "[anonymous]"))
    return mappings


def read_symbols(path: Path):
    result = subprocess.run(["nm", "-n", str(path)], check=True, capture_output=True, text=True)
    symbols = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[1] in {"t", "T", "w", "W"}:
            try:
                symbols.append((int(parts[0], 16), parts[2]))
            except ValueError:
                pass
    symbols.sort()
    return [item[0] for item in symbols], [item[1] for item in symbols]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path)
    parser.add_argument("maps", type=Path)
    parser.add_argument("core", type=Path)
    parser.add_argument("--skip-bytes", type=int, default=0)
    parser.add_argument("--limit-bytes", type=int)
    args = parser.parse_args()
    data = args.samples.read_bytes()[args.skip_bytes:args.limit_bytes]
    if len(data) % 4:
        parser.error("sample file length is not a multiple of four")
    mappings = read_maps(args.maps)
    addresses, names = read_symbols(args.core)
    counts = Counter()
    regions = Counter()
    for (pc,) in struct.iter_unpack("<I", data):
        region = next((m for m in mappings if m[0] <= pc < m[1]), None)
        if not region:
            category = "[unmapped]"
            label = f"{pc:08x}"
        else:
            start, _, offset, path = region
            if path.endswith("/" + args.core.name):
                address = pc - start + offset
                index = bisect_right(addresses, address) - 1
                category = "PCSX ReARMed core"
                label = names[index] if index >= 0 else f"core+{address:x}"
            elif 0x10800000 <= pc < 0x11000000:
                category = "Lightrec generated MIPS code"
                label = category
            else:
                category = path.rsplit("/", 1)[-1] if path.startswith("/") else path
                label = category
        regions[category] += 1
        counts[(category, label)] += 1
    total = sum(regions.values())
    print(f"samples: {total}")
    if not total:
        return
    print("\nRegions:")
    for name, count in regions.most_common():
        print(f"{count:6d} {count / total * 100:5.1f}% {name}")
    print("\nTop functions/regions:")
    for (region, name), count in counts.most_common(35):
        print(f"{count:6d} {count / total * 100:5.1f}% {name} [{region}]")


if __name__ == "__main__":
    main()
