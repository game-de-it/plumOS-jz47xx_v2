#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
src="$out/picodrive-source"
revision=9f46ee4e9680d108e548fb427e7c7e1aa1bb9d5a
mkdir -p "$out"

if [[ ! -d "$src/.git" ]]; then
    git clone https://github.com/irixxxx/picodrive.git "$src"
fi
git -C "$src" fetch origin "$revision"
git -C "$src" checkout --detach "$revision"
git -C "$src" submodule update --init

patch="$repo_root/patches/rg280v-picodrive.patch"
if git -C "$src/platform/libpicofe" apply --reverse --check "$patch" 2>/dev/null; then
    :
else
    git -C "$src/platform/libpicofe" apply "$patch"
fi

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace/output/rg280v-emulators/picodrive-source \
    plumos-jz47xx-build:bookworm bash -c '
        set -e
        export PATH=/workspace/output/rg280v/host/bin:$PATH
        export CROSS_COMPILE=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        export SYSROOT=/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot
        export SDL_CONFIG="$SYSROOT/usr/bin/sdl-config"
        ./configure --platform=odbeta-gcw0
        make -j4
    ' >"$out/picodrive-build.log" 2>&1

cp "$src/PicoDrive.opk" "$out/PicoDrive_rg280v.opk"
shasum -a 256 "$out/PicoDrive_rg280v.opk"
