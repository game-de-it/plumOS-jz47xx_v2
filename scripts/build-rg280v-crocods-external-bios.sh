#!/usr/bin/env bash
# Build CrocoDS from an extracted CrocoDS source supplement on Linux.
set -euo pipefail

if [[ $# -ne 2 ]]; then
    printf 'Usage: %s SOURCE_DIR BUILDROOT_HOST_DIR\n' "$0" >&2
    exit 2
fi
source_dir=$(cd "$1" && pwd)
host_dir=$(cd "$2" && pwd)
cross="$host_dir/bin/mipsel-gcw0-linux-uclibc-"
sysroot=$("${cross}gcc" -print-sysroot)
# Preserve the timestamp embedded by CrocoDS in its help output.
export SOURCE_DATE_EPOCH=1795155116

make -C "$source_dir/standalone/build" -j"${JOBS:-6}" OS=linux PREFIX="$cross" \
    "SDL_CFLAGS=-I$sysroot/usr/include/SDL2 -I$sysroot/usr/include/libdrm -D_REENTRANT -DSDL2 -DPLUMOS_HANDHELD" \
    "SDL_LDFLAGS=-lSDL2 -ldrm" OPTIMIZATION=-O2 crocods_linux
make -C "$source_dir/libretro" -j"${JOBS:-6}" platform=unix CC="${cross}gcc" \
    GIT_VERSION=f1b4b91-plumos

output="$source_dir/output"
mkdir -p "$output"
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
cp -R "$source_dir/opk"/. "$scratch/"
"${cross}strip" -o "$scratch/crocods" "$source_dir/standalone/build/crocods_linux"
"${cross}strip" -o "$output/crocods_libretro.so" "$source_dir/libretro/crocods_libretro.so"
"$host_dir/bin/mksquashfs" "$scratch" "$output/crocods.opk" -all-root -noappend \
    -no-exports -no-xattrs -comp gzip -no-progress
(
    cd "$output"
    sha256sum crocods.opk crocods_libretro.so > SHA256SUMS
)
