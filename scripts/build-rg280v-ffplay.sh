#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
source="$out/ffplay-source"
stage="$out/ffplay-stage"
patch="$repo_root/scripts/patches/ffplay-rg280v.patch"
revision=0ffa36e68a70ef9e3a6d3555427c60df98453edc
image=plumos-jz47xx-build:bookworm
volume=plumos-jz47xx-rg280v-build
mkdir -p "$out"

if [[ ! -d "$source/.git" ]]; then
    git clone --depth 1 --branch release/2.1-gcw0 \
        https://github.com/denis-n-kuznetsov/FFmpeg-GCW0.git "$source"
fi
if [[ $(git -C "$source" rev-parse HEAD) != "$revision" ]]; then
    git -C "$source" fetch --depth 1 origin "$revision"
    git -C "$source" checkout --detach "$revision"
fi
[[ $(git -C "$source" rev-parse HEAD) == "$revision" ]]
if ! git -C "$source" apply --reverse --check "$patch" >/dev/null 2>&1; then
    git -C "$source" apply "$patch"
fi

"$repo_root/scripts/configure-rg280v.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        host=/workspace/output/rg280v/host
        ln -sf ../mipsel-gcw0-linux-uclibc/sysroot/usr/bin/sdl-config \
            "$host/bin/mipsel-gcw0-linux-uclibc-sdl-config"
        test -x "$host/bin/mipsel-gcw0-linux-uclibc-sdl-config"
    '

if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace/output/rg280v-apps/ffplay-source "$image" bash -lc '
        set -e
        host=/workspace/output/rg280v/host
        ./configure --enable-cross-compile --arch=mips --target-os=linux \
            --cross-prefix="$host/bin/mipsel-gcw0-linux-uclibc-" \
            --sysroot="$host/mipsel-gcw0-linux-uclibc/sysroot" \
            --disable-debug --disable-doc --disable-ffmpeg --disable-ffprobe \
            --disable-ffserver --disable-static --enable-shared --enable-ffplay \
            --disable-mipsfpu --disable-mipsdspr1 --disable-mipsdspr2 \
            --extra-cflags="-msoft-float -DPLUMOS_RG280V" \
            --extra-ldflags=-msoft-float \
            > /workspace/output/rg280v-apps/ffplay-configure.log 2>&1
        grep -q "SDL support *yes" /workspace/output/rg280v-apps/ffplay-configure.log
        make -j8 > /workspace/output/rg280v-apps/ffplay-build.log 2>&1
        "$host/bin/mipsel-gcw0-linux-uclibc-gcc" -O2 -msoft-float \
            -I"$host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL" \
            /workspace/assets/rg280v-apps/ffplay-picker.c \
            -L"$host/mipsel-gcw0-linux-uclibc/sysroot/usr/lib" \
            -lSDL_ttf -lSDL -o /workspace/output/rg280v-apps/ffplay-picker
    ' > "$out/ffplay-package-build.log" 2>&1; then
    tail -50 "$out/ffplay-package-build.log" >&2
    tail -50 "$out/ffplay-build.log" 2>/dev/null >&2 || true
    exit 1
fi

rm -rf "$stage"
mkdir -p "$stage/lib"
cp "$repo_root/assets/rg280v-apps/ffplay.sh" "$stage/ffplay.sh"
chmod 755 "$stage/ffplay.sh"
cp "$repo_root/assets/rg280v-apps/ffplay.gcw0.desktop" "$stage/"
cp "$source/ffplay-gcw0/ffplay.png" "$stage/"
cp "$source/ffplay-gcw0/README.txt" "$stage/"
cp "$source/LICENSE" "$source/COPYING.LGPLv2.1" "$stage/"
cp "$repo_root/assets/frontend/default.otf" "$stage/"
cp "$repo_root/assets/frontend/licenses/NotoSansJP-OFL.txt" "$stage/font-OFL.txt"

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        stage=$out/ffplay-stage
        cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        cp "$out/ffplay-source/ffplay" "$stage/ffplay"
        cp "$out/ffplay-picker" "$stage/ffplay-picker"
        for file in "$out"/ffplay-source/libav*/*.so.* \
                    "$out"/ffplay-source/libsw*/*.so.*; do
            cp -L "$file" "$stage/lib/"
        done
        ${cross}strip "$stage/ffplay" "$stage/ffplay-picker" "$stage"/lib/*
        ${cross}readelf -A "$stage/ffplay" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
        /workspace/output/rg280v/host/bin/mksquashfs "$stage" "$out/ffplay-rg280v.opk" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -mkfs-time 0 -all-time 0 >/dev/null
    '

source_export="$out/ffplay-source-export"
rm -rf "$source_export"
mkdir -p "$source_export/ffplay"
git -C "$source" archive "$revision" | tar -C "$source_export/ffplay" -xf -
git -C "$source_export/ffplay" apply "$patch"
cp "$repo_root/assets/rg280v-apps/ffplay-picker.c" \
   "$repo_root/assets/rg280v-apps/ffplay.sh" \
   "$repo_root/assets/rg280v-apps/ffplay.gcw0.desktop" \
   "$source_export/ffplay/ffplay-gcw0/"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -v "$repo_root:/workspace" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            -C "$out/ffplay-source-export" -czf "$out/ffplay-rg280v-source.tar.gz" ffplay
    '
shasum -a 256 "$out/ffplay-rg280v.opk" "$out/ffplay-rg280v-source.tar.gz"
