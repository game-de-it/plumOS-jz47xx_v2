#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
source="$out/st-sdl-source"
stage="$out/st-sdl-stage"
revision=c687e1c57296d468bcad6fd1849f24290b2dae98
patch="$repo_root/scripts/patches/st-sdl-rg280v.patch"
image=plumos-jz47xx-build:bookworm
volume=plumos-jz47xx-rg280v-build
mkdir -p "$out"

if [[ ! -d "$source/.git" ]]; then
    git clone --depth 1 https://github.com/jamesofarrell/st-sdl.git "$source"
fi
if [[ $(git -C "$source" rev-parse HEAD) != "$revision" ]]; then
    git -C "$source" fetch --depth 1 origin "$revision"
    git -C "$source" checkout --detach "$revision"
fi
[[ $(git -C "$source" rev-parse HEAD) == "$revision" ]]
if ! git -C "$source" apply --reverse --check "$patch" >/dev/null 2>&1; then
    git -C "$source" apply "$patch"
fi

cp "$repo_root/assets/rg280v-apps/st-sdl-build.mk" "$source/config_rg350.mk"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace/output/rg280v-apps/st-sdl-source "$image" \
    bash -lc 'make clean && make -j8' > "$out/st-sdl-build.log" 2>&1 || {
        tail -80 "$out/st-sdl-build.log" >&2
        exit 1
    }

rm -rf "$stage"
mkdir -p "$stage"
cp "$source/st" "$source/st.png" "$source/LICENSE" "$source/README" "$stage/"
cp "$repo_root/assets/rg280v-apps/st-sdl-rg280v.sh" \
   "$repo_root/assets/rg280v-apps/st-sdl.rg280v.desktop" "$stage/"
chmod 755 "$stage/st-sdl-rg280v.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        ${cross}strip "$out/st-sdl-stage/st"
        ${cross}readelf -A "$out/st-sdl-stage/st" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
        /workspace/output/rg280v/host/bin/mksquashfs \
            "$out/st-sdl-stage" "$out/st-sdl-rg280v.opk" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -mkfs-time 0 -all-time 0 >/dev/null
    '

export_dir="$out/st-sdl-source-export"
rm -rf "$export_dir"
mkdir -p "$export_dir/st-sdl"
git -C "$source" archive "$revision" | tar -C "$export_dir/st-sdl" -xf -
patch -d "$export_dir/st-sdl" -p1 < "$patch" >/dev/null
cp "$repo_root/assets/rg280v-apps/"{st-sdl-build.mk,st-sdl-rg280v.sh,st-sdl.rg280v.desktop} \
   "$export_dir/st-sdl/"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -v "$repo_root:/workspace" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            -C "$out/st-sdl-source-export" \
            -czf "$out/st-sdl-rg280v-source.tar.gz" st-sdl
    '
shasum -a 256 "$out/st-sdl-rg280v.opk" "$out/st-sdl-rg280v-source.tar.gz"
