#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
source="$out/bard-source"
stage="$out/bard-stage"
patch="$repo_root/scripts/patches/bard-rg280v.patch"
revision=d2b5b3330c646897a886381144975b63afce045a
image=plumos-jz47xx-build:bookworm
volume=plumos-jz47xx-rg280v-build
mkdir -p "$out"

if [[ ! -d "$source/.git" ]]; then
    git clone https://github.com/festvox/bard.git "$source"
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
if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" make -C /workspace/work/buildroot \
    O=/workspace/output/rg280v \
    BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace \
    flite libzip sdl_ttf sdl_gfx > "$out/bard-dependencies-build.log" 2>&1; then
    tail -60 "$out/bard-dependencies-build.log" >&2
    exit 1
fi

if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace/output/rg280v-apps/bard-source "$image" bash -lc '
        set -e
        host=/workspace/output/rg280v/host
        cross=$host/bin/mipsel-gcw0-linux-uclibc-
        export CC=${cross}gcc AR=${cross}ar RANLIB=${cross}ranlib
        export FLITEDIR=$host/mipsel-gcw0-linux-uclibc/sysroot/usr
        export DEFAULTFONT=/opk/default.otf
        export CFLAGS="-O2 -msoft-float -DGCW0 -DPLUMOS_RG280V"
        export LDFLAGS=-msoft-float
        export ac_cv_header_harfbuzz_hb_h=no
        "$host/bin/autoconf"
        ./configure --host=mipsel-gcw0-linux-uclibc --build=aarch64-unknown-linux-gnu
        make -j8
    ' > "$out/bard-build.log" 2>&1; then
    tail -60 "$out/bard-build.log" >&2
    exit 1
fi

rm -rf "$stage"
mkdir -p "$stage/lib"
cp "$repo_root/assets/rg280v-apps/bard.sh" "$stage/bard.sh"
chmod 755 "$stage/bard.sh"
cp "$source/gcw0/default.gcw0.desktop" "$stage/"
cp "$source/gcw0/Bard_Help.html" "$source/Bard32.png" "$stage/"
cp "$source/COPYING" "$stage/Bard-COPYING"
cp "$repo_root/assets/frontend/default.otf" "$stage/"
cp "$repo_root/assets/frontend/licenses/NotoSansJP-OFL.txt" "$stage/font-OFL.txt"

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        stage=$out/bard-stage
        cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        sysroot=/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr
        cp "$out/bard-source/bin/bard" "$stage/bard"
        ${cross}strip "$stage/bard"
        for name in libzip.so.5 libflite.so.1 libflite_usenglish.so.1 \
                    libflite_cmulex.so.1 libflite_cmu_indic_lang.so.1 \
                    libflite_cmu_indic_lex.so.1 libflite_cmu_us_kal.so.1; do
            cp -L "$sysroot/lib/$name" "$stage/lib/$name" 2>/dev/null || \
                cp -L "$sysroot/usr/lib/$name" "$stage/lib/$name"
        done
        cp /workspace/output/rg280v/build/flite-2.2/COPYING "$stage/flite-COPYING"
        cp /workspace/output/rg280v/build/libzip-1.10.1/LICENSE "$stage/libzip-LICENSE"
        /workspace/output/rg280v/host/bin/mksquashfs "$stage" "$out/bard-rg280v.opk" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -mkfs-time 0 -all-time 0 >/dev/null
        ${cross}readelf -A "$stage/bard" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
    '

source_export="$out/bard-source-export"
rm -rf "$source_export"
mkdir -p "$source_export/bard"
git -C "$source" archive "$revision" | tar -C "$source_export/bard" -xf -
git -C "$source_export/bard" apply "$patch"
cp "$repo_root/assets/rg280v-apps/bard.sh" "$source_export/bard/plumos-rg280v-bard.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -v "$repo_root:/workspace" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            -C "$out/bard-source-export" -czf "$out/bard-rg280v-source.tar.gz" bard
    '
shasum -a 256 "$out/bard-rg280v.opk" "$out/bard-rg280v-source.tar.gz"
