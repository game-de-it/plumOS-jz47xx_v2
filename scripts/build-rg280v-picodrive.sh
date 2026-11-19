#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
src="$out/picodrive-source"
revision=9f46ee4e9680d108e548fb427e7c7e1aa1bb9d5a
mkdir -p "$out"

if [[ ! -d "$src/.git" ]]; then
    git clone --depth 1 https://github.com/irixxxx/picodrive.git "$src"
fi
if ! git -C "$src" cat-file -e "$revision^{commit}" 2>/dev/null; then
    git -C "$src" fetch --depth 1 origin "$revision"
fi
git -C "$src" checkout --detach "$revision"
git -C "$src" submodule update --init --depth 1

libpicofe="$src/platform/libpicofe"
patch="$repo_root/patches/rg280v-picodrive.patch"
vga_patch="$repo_root/patches/rg300x-picodrive-sega8-video.patch"
if ! git -C "$libpicofe" apply --reverse --check "$vga_patch" 2>/dev/null; then
    if ! git -C "$libpicofe" apply --reverse --check "$patch" 2>/dev/null; then
        git -C "$libpicofe" apply "$patch"
    fi
    git -C "$libpicofe" apply "$vga_patch"
fi
sega8_patch="$repo_root/patches/rg280v-picodrive-sega8.patch"
if git -C "$src" apply --reverse --check "$sega8_patch" 2>/dev/null; then
    :
else
    git -C "$src" apply "$sega8_patch"
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
        export SOURCE_DATE_EPOCH=0
        ./configure --platform=odbeta-gcw0
        make clean
        make -j4
        unset SOURCE_DATE_EPOCH
        mksquashfs .od_data PicoDrive.opk -all-root -noappend -no-exports \
            -no-xattrs -mkfs-time 0 -all-time 0
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            --exclude=.git --exclude="*.o" --exclude=.od_data \
            --exclude=picodrive --exclude=PicoDrive.opk \
            --exclude=picodrive.map \
            -czf /workspace/output/rg280v-emulators/PicoDrive_rg280v-source.tar.gz \
            -C /workspace/output/rg280v-emulators picodrive-source
    ' >"$out/picodrive-build.log" 2>&1

cp "$src/PicoDrive.opk" "$out/PicoDrive_rg280v.opk"
shasum -a 256 "$out/PicoDrive_rg280v.opk"
