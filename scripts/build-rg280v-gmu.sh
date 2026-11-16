#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
source="$out/gmu-source"
stage="$out/gmu-stage"
revision=d0ef466fa52297a7f6e92db1c39d0c59d3158740
patch="$repo_root/scripts/patches/gmu-rg280v.patch"
image=plumos-jz47xx-build:bookworm
volume=plumos-jz47xx-rg280v-build
mkdir -p "$out"

if [[ ! -d "$source/.git" ]]; then
    git clone --depth 1 --branch 0.10.1-gcw0 \
        https://github.com/denis-n-kuznetsov/gmu.git "$source"
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
    -w /workspace "$image" \
    make -C /workspace/work/buildroot O=/workspace/output/rg280v \
        BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace \
        mpg123 flac tremor > "$out/gmu-dependencies-build.log" 2>&1

cp "$repo_root/assets/rg280v-apps/gmu-build.mk" "$source/config.mk"
if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace/output/rg280v-apps/gmu-source "$image" \
    bash -lc 'make -j8' > "$out/gmu-build.log" 2>&1; then
    tail -50 "$out/gmu-build.log" >&2
    exit 1
fi

rm -rf "$stage"
mkdir -p "$stage"/{decoders,frontends,lib}
cp "$source/gmu.bin" "$stage/"
cp "$source/frontends/sdl.so" "$stage/frontends/"
cp "$source/decoders/"{mpg123,vorbis,flac}.so "$stage/decoders/"
cp -R "$source/themes" "$stage/"
cp "$source/gmu.bmp" "$source/gmu.png" "$source/README.txt" \
   "$source/COPYING" "$stage/"
for name in gmu-rg280v.sh gmu.rg280v.desktop gmu.rg280v.conf \
            gmu.rg280v.keymap gmuinput.rg280v.conf; do
    cp "$repo_root/assets/rg280v-apps/$name" "$stage/"
done
chmod 755 "$stage/gmu-rg280v.sh"

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        stage=$out/gmu-stage
        cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        sysroot=/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot
        for name in libmpg123.so.0 libFLAC.so.12 libvorbisidec.so.1 libogg.so.0; do
            cp -L "$sysroot/usr/lib/$name" "$stage/lib/$name"
        done
        ${cross}strip "$stage/gmu.bin" "$stage"/frontends/*.so \
            "$stage"/decoders/*.so "$stage"/lib/*.so.*
        ${cross}readelf -A "$stage/gmu.bin" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
        /workspace/output/rg280v/host/bin/mksquashfs "$stage" "$out/gmu-rg280v.opk" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -mkfs-time 0 -all-time 0 >/dev/null
    '

export_dir="$out/gmu-source-export"
rm -rf "$export_dir"
mkdir -p "$export_dir/gmu"
git -C "$source" archive "$revision" | tar -C "$export_dir/gmu" -xf -
git -C "$export_dir/gmu" apply "$patch"
cp "$repo_root/assets/rg280v-apps/"{gmu-build.mk,gmu-rg280v.sh,gmu.rg280v.desktop,gmu.rg280v.conf,gmu.rg280v.keymap,gmuinput.rg280v.conf} \
    "$export_dir/gmu/"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -v "$repo_root:/workspace" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            -C "$out/gmu-source-export" -czf "$out/gmu-rg280v-source.tar.gz" gmu
    '
shasum -a 256 "$out/gmu-rg280v.opk" "$out/gmu-rg280v-source.tar.gz"
