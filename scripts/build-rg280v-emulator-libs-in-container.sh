#!/usr/bin/env bash
set -euo pipefail

out=/workspace/output/rg280v-emulators
mkdir -p "$out/lib"
if ! make -C /workspace/work/buildroot O=/workspace/output/rg280v \
    BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace \
    sdl_image sdl_mixer > "$out/sdl-libs-build.log" 2>&1; then
    tail -60 "$out/sdl-libs-build.log" >&2
    exit 1
fi

syslibs=/workspace/output/rg280v/target/usr/lib
cp -L "$syslibs/libSDL_image-1.2.so.0" "$syslibs/libSDL_mixer-1.2.so.0" "$out/lib/"

build="$out/libpng14-build"
if [[ ! -f "$build/libpng-1.4.22/.libs/libpng14.so.14" ]]; then
    mkdir -p "$build"
    tar -xzf "$out/libpng-1.4.22.tar.gz" -C "$build"
    cd "$build/libpng-1.4.22"
    export PATH=/workspace/output/rg280v/host/bin:$PATH
    if ! ./configure --host=mipsel-gcw0-linux-uclibc --prefix=/usr \
        --disable-static --enable-shared > configure.log 2>&1; then
        tail -60 configure.log >&2
        exit 1
    fi
    if ! make -j4 > build.log 2>&1; then
        tail -60 build.log >&2
        exit 1
    fi
fi
cp -L "$build/libpng-1.4.22/.libs/libpng14.so.14" "$out/lib/libpng14.so.14"
strip=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-strip
"$strip" --strip-unneeded "$out/lib/"*
file "$out/lib/"*
sha256sum "$out/lib/"*
