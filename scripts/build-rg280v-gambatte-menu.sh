#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$repo_root/output/rg280v-emulators/lib"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm \
    bash -c '
        set -e
        cc=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc
        "$cc" -std=c99 -Os -fPIC -shared -Wl,-soname,libgambatte-menu.so \
            -o /workspace/output/rg280v-emulators/lib/libgambatte-menu.so.new \
            /workspace/scripts/rg280v-gambatte-menu.c -ldl
        mv /workspace/output/rg280v-emulators/lib/libgambatte-menu.so.new \
            /workspace/output/rg280v-emulators/lib/libgambatte-menu.so
    '
shasum -a 256 "$repo_root/output/rg280v-emulators/lib/libgambatte-menu.so"
