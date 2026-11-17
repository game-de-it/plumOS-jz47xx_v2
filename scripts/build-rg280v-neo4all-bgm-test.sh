#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
src="$root/output/rg280v-apps/neo4all-reference-src"
revision=407dcb3a46ca326d74f4bde4da1eadc8287be2a4
if [ ! -d "$src/.git" ]; then
    git clone https://github.com/nicodanyan/neo4all.git "$src"
    git -C "$src" checkout --detach "$revision"
fi
[ "$(git -C "$src" rev-parse HEAD)" = "$revision" ]
patch="$root/patches/rg280v-neo4all-bgm-test.patch"
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
    cd "$work/neo4all-reference-src"
    make -f Makefile.rg350 -j8 CROSS_COMPILE="$t/bin/mipsel-gcw0-linux-uclibc-" \
        SDL_CFLAGS="-I$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL -D_REENTRANT" \
        SDL_LIBS=-lSDL >"$work/neo4all-rg280v-build.log" 2>&1
    stage="$work/neo4all-bgm-test-stage"
    mkdir -p "$stage"
    cp -a neo4all/data "$stage/"
    cp neo4all/neo4all.dge neo4all/neo4all.png "$stage/"
    "$t/bin/mipsel-gcw0-linux-uclibc-readelf" -A "$stage/neo4all.dge" | grep "Soft float"
    cat >"$stage/bgm-test.sh" <<"EOF"
#!/bin/sh
export HOME=/media/data/local/rg350-missing-rom-retest/home-15
exec ./neo4all.dge "$1"
EOF
    chmod 755 "$stage/bgm-test.sh"
    cat >"$stage/default.gcw0.desktop" <<"EOF"
[Desktop Entry]
Name=TEST Neo4All BGM
Type=Application
Exec=/bin/sh ./bgm-test.sh %f
Icon=neo4all
Categories=emulators;
EOF
    dest="$work/neo4all-rg280v-bgm-test.opk"
    rm -f "$dest"
    "$t/bin/mksquashfs" "$stage" "$dest" -all-root -noappend -no-exports -comp gzip -no-progress >/dev/null
    sha256sum "$dest"
    '
