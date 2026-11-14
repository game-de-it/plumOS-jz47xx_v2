#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
out=${1:-$repo_root/output/rg280v-fe/drm-screenshot.png}
raw=${out%.png}.raw
metadata=${out%.png}.drm.txt
binary="$repo_root/output/rg280v-fe/rg280v-drm-capture"
remote=/media/data/plumos/Logs/drm-capture.raw
mkdir -p "$(dirname "$out")"

if [[ ! -x "$binary" || "$repo_root/scripts/rg280v-drm-capture.c" -nt "$binary" ]]; then
    docker run --rm --platform linux/arm64 \
        --user "$(id -u):$(id -g)" -e HOME=/tmp \
        -v "$repo_root:/workspace" \
        -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
        -w /workspace plumos-jz47xx-build:bookworm \
        bash -c '
            set -e
            cc=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc
            sysroot=$($cc -print-sysroot)
            "$cc" -std=gnu99 -Os -Wall -Wextra -I"$sysroot/usr/include/libdrm" \
                /workspace/scripts/rg280v-drm-capture.c -o /workspace/output/rg280v-fe/rg280v-drm-capture -ldrm
        '
fi

adb -P "$port" -s "$serial" push "$binary" /media/data/plumos/bin/rg280v-drm-capture >/dev/null
adb -P "$port" -s "$serial" shell "chmod 0755 /media/data/plumos/bin/rg280v-drm-capture && /media/data/plumos/bin/rg280v-drm-capture $remote" >"$metadata" 2>&1
adb -P "$port" -s "$serial" pull "$remote" "$raw" >/dev/null
python3 - "$raw" "$metadata" "$out" <<'PY'
import re
import sys
from PIL import Image

raw_path, metadata_path, output_path = sys.argv[1:]
metadata = open(metadata_path, encoding='utf-8').read()
format_match = re.search(r'format=(\w{4})', metadata)
size_match = re.search(r'fb=\d+ size=(\d+)x(\d+) pitch=(\d+) bpp=(\d+)', metadata)
if not format_match or not size_match:
    raise SystemExit(f'could not read DRM format: {metadata_path}')
fmt = format_match.group(1)
width, height, pitch, bpp = map(int, size_match.groups())
data = open(raw_path, 'rb').read()
if len(data) != pitch * height:
    raise SystemExit(f'framebuffer size mismatch: {len(data)} != {pitch * height}')
if fmt == 'XB15' and bpp == 16:
    rgb = bytearray(width * height * 3)
    for y in range(height):
        for x in range(width):
            offset = y * pitch + x * 2
            pixel = int.from_bytes(data[offset:offset + 2], 'little')
            dst = (y * width + x) * 3
            rgb[dst:dst + 3] = bytes(((pixel & 31) * 255 // 31,
                                       ((pixel >> 5) & 31) * 255 // 31,
                                       ((pixel >> 10) & 31) * 255 // 31))
    image = Image.frombytes('RGB', (width, height), bytes(rgb))
elif fmt == 'XR24' and bpp == 32:
    image = Image.frombytes('RGB', (width, height), data, 'raw', 'BGRX', pitch, 1)
else:
    raise SystemExit(f'unsupported DRM format: {fmt}, {bpp} bpp')
image.save(output_path)
print(output_path)
PY
