#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-status"
mkdir -p "$out"

rsvg-convert "$repo_root/board/rg280v/assets/adb-ready.svg" -o "$out/adb-ready.png"
magick "$out/adb-ready.png" -resize '320x480!' -depth 8 ppm:"$out/adb-ready.ppm"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" \
    -v plumos-jz47xx-rg280v-build:/build \
    -v "$repo_root:/workspace" -w /workspace \
    plumos-jz47xx-build:bookworm \
    /build/host/bin/mipsel-gcw0-linux-uclibc-gcc \
        -Os -Wall -Wextra tools/rg280v-fbshow.c -o output/rg280v-status/rg280v-fbshow

adb connect 10.1.1.2:5555
adb -s 10.1.1.2:5555 shell \
    'mkdir -p /media/data/local/bin /media/data/local/share /media/data/local/init.d'
adb -s 10.1.1.2:5555 push "$out/rg280v-fbshow" /media/data/local/bin/rg280v-fbshow
adb -s 10.1.1.2:5555 push "$out/adb-ready.ppm" /media/data/local/share/adb-ready.ppm
adb -s 10.1.1.2:5555 push "$repo_root/board/rg280v/adb/S90status" \
    /media/data/local/init.d/S90status
adb -s 10.1.1.2:5555 shell \
    'chmod 0755 /media/data/local/bin/rg280v-fbshow /media/data/local/init.d/S90status; /media/data/local/init.d/S90status start'
