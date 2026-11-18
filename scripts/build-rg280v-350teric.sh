#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
work="$root/output/rg280v-350teric"
revision=6e0a1ca1aa523ec5dff042c4a220582edc1767e9
mkdir -p "$work"
if [ ! -d "$work/source/.git" ]; then
 git clone https://github.com/podulator/esoteric.git "$work/source"
 git -C "$work/source" checkout --detach "$revision"
fi
[ "$(git -C "$work/source" rev-parse HEAD)" = "$revision" ]
if ! git -C "$work/source" apply --reverse --check "$root/patches/rg280v-350teric.patch" 2>/dev/null; then
 git -C "$work/source" apply --check "$root/patches/rg280v-350teric.patch"
 git -C "$work/source" apply "$root/patches/rg280v-350teric.patch"
fi
docker run --rm --platform linux/arm64 -v "$root:/workspace" \
 -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
 -w /workspace plumos-jz47xx-build:bookworm bash -euc '
 t=/workspace/output/rg280v/host
 w=/workspace/output/rg280v-350teric
 cd "$w/source"
 mkdir -p objs/plumos "$w/runtime/lib"
 flags="-O2 -std=gnu++11 -DPLUMOS_RG280V -DLOG_LEVEL=2 -DHAVE_LIBOPK -DENABLE_INOTIFY -DTARGET_RG350 -Wno-narrowing -I$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL -I$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/freetype2 -D_REENTRANT"
 export flags t
 printf "%s\n" src/*.cpp | xargs -P8 -I{} bash -euc '\''src="$1"; "$t/bin/mipsel-gcw0-linux-uclibc-g++" $flags -c "$src" -o "objs/plumos/$(basename "$src" .cpp).o"'\'' _ {}
 "$t/bin/mipsel-gcw0-linux-uclibc-g++" -o "$w/runtime/esoteric" objs/plumos/*.o -lfreetype -lSDL_image -lSDL_ttf -lSDL_gfx -lSDL_mixer -lSDL -lpthread -lopk -lpng -lasound
 "$t/bin/mipsel-gcw0-linux-uclibc-strip" "$w/runtime/esoteric"
 "$t/bin/mipsel-gcw0-linux-uclibc-readelf" -d "$w/runtime/esoteric" | grep NEEDED
 mkdir -p "$w/runtime/lib" "$w/image-objects"
 img=/workspace/output/rg280v/build/sdl_image-5d792dde2f764daf15dc48521774a3354330db69
 for src in "$img"/IMG*.c; do
  "$t/bin/mipsel-gcw0-linux-uclibc-gcc" -O2 -fPIC -DLOAD_PNG -DLOAD_JPG -DLOAD_BMP -DLOAD_GIF -DLOAD_XPM -I"$img" -I"$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL" -c "$src" -o "$w/image-objects/$(basename "$src" .c).o"
 done
 "$t/bin/mipsel-gcw0-linux-uclibc-gcc" -shared -Wl,-soname,libSDL_image-1.2.so.0 -o "$w/runtime/lib/libSDL_image-1.2.so.0" "$w"/image-objects/*.o -lSDL -lpng -ljpeg -lz
 cp -L "$t/mipsel-gcw0-linux-uclibc/sysroot/usr/lib/libjpeg.so.8" "$w/runtime/lib/"
 cp "$img/COPYING" "$w/runtime/SDL_image-COPYING"

 cp -L "$t/mipsel-gcw0-linux-uclibc/sysroot/usr/lib/libSDL_gfx.so.13" "$w/runtime/lib/"
 cp COPYING README.md about.txt "$w/runtime/"
 '
