#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
src="$root/output/rg280v-apps/stella-src"
revision=4c309195f666909e7c0a185bcc46da836fc234dd
if [ ! -d "$src/.git" ]; then
    git clone https://github.com/DavidKnight247/Stella-3.9.3.git "$src"
    git -C "$src" checkout --detach "$revision"
fi
[ "$(git -C "$src" rev-parse HEAD)" = "$revision" ]
patch="$root/patches/rg280v-stella-menu-input.patch"
if ! git -C "$src" apply --reverse --check "$patch" 2>/dev/null; then
    git -C "$src" apply --check "$patch"
    git -C "$src" apply "$patch"
fi
docker run --rm --platform linux/arm64 \
    -v "$root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm bash -euc '
    t=/workspace/output/rg280v/host
    work=/workspace/output/rg280v-apps
    cd "$work/stella-src"
    # Upstream checks timestamps on its committed generated configuration.
    touch config.mak
    make -j8 CXX="$t/bin/mipsel-gcw0-linux-uclibc-g++" LD="$t/bin/mipsel-gcw0-linux-uclibc-g++" \
        CXXFLAGS="-O3 -mips32r2 -msoft-float -fcommon -std=gnu++98 -DGCW0 -DPLUMOS_RG280V" \
        INCLUDES="-Isrc/emucore -Isrc/common -Isrc/common/tv_filters -Isrc/gui -Isrc/unix -Isrc/cheat -I$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL -D_GNU_SOURCE=1 -D_REENTRANT" \
        LIBS="-lSDL -lSDL_image -lpng -lz" >"$work/stella-build.log" 2>&1
    stage="$work/stella-menu-stage"
    "$t/bin/unsquashfs" -f -no-progress -d "$stage" "$work/rg350-catalog/Stella_2015-10-06.opk" >/dev/null
    cp stella "$stage/stella"
    "$t/bin/mipsel-gcw0-linux-uclibc-strip" "$stage/stella"
    "$t/bin/mipsel-gcw0-linux-uclibc-readelf" -A "$stage/stella" | grep "Soft float"
    # Do not mix the old global SDL_image/png14 closure with this png16 build.
    mkdir -p "$stage/lib"
    cp -L "$t/mipsel-gcw0-linux-uclibc/sysroot/usr/lib/libSDL_image.so" "$stage/lib/libSDL_image-1.2.so.0"
    cp -L "$t/mipsel-gcw0-linux-uclibc/sysroot/usr/lib/libpng16.so.16" "$stage/lib/libpng16.so.16"
    cat >"$stage/plumos-stella.sh" <<"EOF"
#!/bin/sh
export LD_LIBRARY_PATH=/opk/lib:${LD_LIBRARY_PATH:-/media/data/plumos/lib}
exec ./stella "$@"
EOF
    sed -i "s|^Exec=.*|Exec=/bin/sh ./plumos-stella.sh %f|" "$stage/default.gcw0.desktop"
    cat >"$stage/gcw0readme.txt" <<"EOF"
plumOS RG280V Stella
START + SELECT: open/close menu (release both before repeating)
SELECT alone: Atari Reset, on release
START alone: reserved for plumOS shortcuts (no Reset)
Game: D-pad moves, A fires, B selects game variation
Menu: D-pad selects widgets or adjusts their values, A confirms, B returns
Menu L/R: previous/next widget (also leaves lists and sliders)
Menu X/Y: next/previous tab
Power and volume controls belong to plumOS.
EOF
    dest="$work/stella-rg280v-menu.opk"
    rm -f "$dest"
    "$t/bin/mksquashfs" "$stage" "$dest" -all-root -noappend -no-exports -comp gzip -no-progress >/dev/null
    sha256sum "$dest"
    '
