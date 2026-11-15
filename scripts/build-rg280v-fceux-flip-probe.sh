#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$repo_root/output/rg280v-emulators/lib"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm bash -c '
        cc=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc
        "$cc" -std=gnu99 -O2 -fPIC -shared \
            -o /workspace/output/rg280v-emulators/lib/libfceux-flip-probe.so \
            /workspace/scripts/rg280v-fceux-flip-probe.c -ldl -lrt
    '
shasum -a 256 "$repo_root/output/rg280v-emulators/lib/libfceux-flip-probe.so"
