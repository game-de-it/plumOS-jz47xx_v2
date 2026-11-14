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
