#!/usr/bin/env bash
set -euo pipefail

out=/workspace/output/rg280v-emulators
mkdir -p "$out/lib"
if ! make -C /workspace/work/buildroot O=/workspace/output/rg280v \
    BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace \
    sdl_image sdl_mixer sdl_sound sdl_net bzip2 libtheora libvorbis flac \
    jpeg-turbo gettext-gnu libsndfile \
    > "$out/sdl-libs-build.log" 2>&1; then
    tail -60 "$out/sdl-libs-build.log" >&2
    exit 1
fi

syslibs=/workspace/output/rg280v/target/usr/lib
cp -L "$syslibs/libSDL_image-1.2.so.0" "$syslibs/libSDL_mixer-1.2.so.0" "$out/lib/"
for name in libSDL_sound-1.0.so.1 libSDL_net-1.2.so.0 \
    libvorbisidec.so.1 libFLAC.so.12 libbz2.so.1.0 libtheoradec.so.1 \
    libintl.so.8 libjpeg.so.8 libsndfile.so.1; do
    cp -L "$syslibs/$name" "$out/lib/$name"
done

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
shake="$out/libshake-v0.3.0-source"
make -C "$shake" BACKEND=LINUX \
    CC=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc \
    STRIP=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-strip
cp "$shake/libshake.so.1" "$out/lib/libshake.so.1"
strip=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-strip
"$strip" --strip-unneeded "$out/lib/"*
file "$out/lib/"*
sha256sum "$out/lib/"*
