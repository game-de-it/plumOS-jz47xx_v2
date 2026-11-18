#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
work="$root/output/rg280v-simplemenu"
revision=e70a861b1f05fd83cd1b19be53be11c0a0ecd510
mkdir -p "$work"
if [ ! -d "$work/source/.git" ]; then
    git clone https://github.com/fgl82/simplemenu.git "$work/source"
    git -C "$work/source" checkout --detach "$revision"
fi
[ "$(git -C "$work/source" rev-parse HEAD)" = "$revision" ]
if ! git -C "$work/source" apply --reverse --check "$root/patches/rg280v-simplemenu.patch" 2>/dev/null; then
    git -C "$work/source" apply --check "$root/patches/rg280v-simplemenu.patch"
    git -C "$work/source" apply "$root/patches/rg280v-simplemenu.patch"
fi
docker run --rm --platform linux/arm64 \
    -v "$root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm bash -euc '
    t=/workspace/output/rg280v/host
    work=/workspace/output/rg280v-simplemenu
    cd "$work/source/simplemenu"
    mkdir -p simplemenu-portable
    make clean
    make -j8 TARGET=rg350 CROSS_COMPILE="$t/bin/mipsel-gcw0-linux-uclibc-" \
      CFLAGS="-DRG350 -DPLUMOS_RG280V -I$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL -D_REENTRANT -O2 -std=gnu99 -fcommon" \
      LIBS="-lSDL -lSDL_image -lSDL_ttf -lSDL_mixer -lpng -ljpeg -lz -lm -pthread -lopk"
    "$t/bin/mipsel-gcw0-linux-uclibc-readelf" -A simplemenu-portable/simplemenu | grep "Soft float"
    mkdir -p "$work/runtime/resources" "$work/runtime/licenses"
    cp simplemenu-portable/simplemenu "$work/runtime/simplemenu"
    "$t/bin/mipsel-gcw0-linux-uclibc-strip" "$work/runtime/simplemenu"
    cp -a output/resources/. "$work/runtime/resources/"
    cp /usr/share/common-licenses/GPL-3 "$work/runtime/licenses/SimpleMenu-GPL-3.txt"
    cp ../README.md "$work/runtime/licenses/SimpleMenu-README.md"
    '
cp "$root/assets/frontend/bin/plumos-simplemenu-invoker" "$work/runtime/invoker.dge"
chmod 755 "$work/runtime/invoker.dge"
