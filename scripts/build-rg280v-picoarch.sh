#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
src="$out/picoarch-source"
revision=802047c276a5a931b0bf837c4ea4b8e238bdeabe
core_src="$out/beetle-pce-fast-source"
core_revision=2de1ce1c3f237b161c126c54ba407990bb86d1e9
mkdir -p "$out"

if [[ ! -d "$src/.git" ]]; then
    git clone --filter=blob:none https://github.com/shauninman/picoarch.git "$src"
fi
if ! git -C "$src" cat-file -e "$revision^{commit}" 2>/dev/null; then
    git -C "$src" fetch --depth 1 origin "$revision"
fi
git -C "$src" reset --hard "$revision"
git -C "$src" clean -ffdx
git -C "$src" submodule update --init --depth 1
git -C "$src/libpicofe" reset --hard HEAD
git -C "$src/libpicofe" clean -ffdx
python3 "$repo_root/scripts/patch-rg280v-picoarch.py" "$src"

if [[ ! -d "$core_src/.git" ]]; then
    git clone --depth 1 --recursive https://github.com/libretro/beetle-pce-fast-libretro.git "$core_src"
fi
if ! git -C "$core_src" cat-file -e "$core_revision^{commit}" 2>/dev/null; then
    git -C "$core_src" fetch --depth 1 origin "$core_revision"
fi
git -C "$core_src" reset --hard "$core_revision"
git -C "$core_src" clean -ffdx

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace/output/rg280v-emulators/picoarch-source \
    plumos-jz47xx-build:bookworm bash -c '
        set -e
        export PATH=/workspace/output/rg280v/host/bin:$PATH
        export CROSS_COMPILE=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        make platform=unix MMENU=0 libpicofe/.patched
        make platform=unix MMENU=0 -j4 picoarch
        cd /workspace/output/rg280v-emulators/beetle-pce-fast-source
        make -j4 platform=unix \
            CC=mipsel-gcw0-linux-uclibc-gcc \
            CXX=mipsel-gcw0-linux-uclibc-g++ \
            AR=mipsel-gcw0-linux-uclibc-ar
        out=/workspace/output/rg280v-emulators
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            --exclude=.git --exclude="*.o" --exclude="*.so" \
            --exclude=picoarch --exclude="*.a" --exclude="*.d" \
            -czf "$out/picoarch-rg280v-source.tar.gz" -C "$out" picoarch-source
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            --exclude=.git --exclude="*.o" --exclude="*.so" \
            --exclude="*.a" --exclude="*.d" \
            -czf "$out/mednafen_pce_fast-rg280v-source.tar.gz" \
            -C "$out" beetle-pce-fast-source
    ' >"$out/picoarch-build.log" 2>&1

cp "$src/picoarch" "$out/picoarch-rg280v"
cp "$core_src/mednafen_pce_fast_libretro.so" "$out/mednafen_pce_fast_libretro.so"
shasum -a 256 "$out/picoarch-rg280v" "$out/mednafen_pce_fast_libretro.so"
