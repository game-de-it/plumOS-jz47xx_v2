#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
"$repo_root/scripts/fetch-rg280v-emulators.sh"

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm \
    bash -c '
        set -euo pipefail
        out=/workspace/output/rg280v-emulators
        tools=/workspace/output/rg280v/host/bin
        stage=$out/regba-repack-stage
        rm -rf "$stage"
        "$tools/unsquashfs" -f -d "$stage" "$out/ReGBA_1.9.2_rg350.opk" >/dev/null
        cp "$out/ReGBA_1.9.2-GPL-2.0.txt" "$stage/LICENSE"
        "$tools/mksquashfs" "$stage" "$out/ReGBA_1.9.2_rg280v.opk.new" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -all-time 0 -mkfs-time 0 >/dev/null
        mv "$out/ReGBA_1.9.2_rg280v.opk.new" "$out/ReGBA_1.9.2_rg280v.opk"
        rm -rf "$stage"
        mkdir -p "$out/lib"
        "$tools/mipsel-gcw0-linux-uclibc-gcc" -std=c99 -Os -fPIC -shared \
            -Wl,-soname,libregba-doublebuf.so \
            -o "$out/lib/libregba-doublebuf.so.new" \
            /workspace/scripts/rg280v-regba-doublebuf.c -ldl
        mv "$out/lib/libregba-doublebuf.so.new" "$out/lib/libregba-doublebuf.so"
    '
shasum -a 256 "$out/ReGBA_1.9.2_rg280v.opk"
shasum -a 256 "$out/lib/libregba-doublebuf.so"
