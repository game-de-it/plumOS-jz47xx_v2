#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
source_dir="$out/input-test-source"
commit=98301bd91047865ebcb6b366882c0592b7f69a16

mkdir -p "$out"
if [[ ! -d "$source_dir/.git" ]]; then
    git clone --depth 1 https://github.com/tonyjih/RG350_input-test.git "$source_dir"
fi
if [[ $(git -C "$source_dir" rev-parse HEAD) != "$commit" ]]; then
    git -C "$source_dir" fetch --depth 1 origin "$commit"
    git -C "$source_dir" checkout --detach "$commit"
fi
[[ $(git -C "$source_dir" rev-parse HEAD) == "$commit" ]] || exit 1
patch="$repo_root/scripts/patches/input-test-rg280v.patch"
if ! git -C "$source_dir" apply --reverse --check "$patch" >/dev/null 2>&1; then
    git -C "$source_dir" apply "$patch"
fi

docker run --rm -i --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm bash -s <<'CONTAINER'
set -euo pipefail
cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
sysroot=$(${cross}gcc -print-sysroot)
out=/workspace/output/rg280v-apps
src=$out/input-test-source
stage=$out/input-test-stage
rm -rf "$stage"
mkdir -p "$stage"
"${cross}gcc" -std=gnu99 -O2 -mips32r2 -msoft-float -DSDL_1 \
    -I/workspace/scripts/stubs/rg280v-no-shake -I"$sysroot/usr/include/SDL" \
    "$src/sdl.c" -o "$stage/input-test-sdl-1.2" \
    -L"$sysroot/usr/lib" -lSDL_ttf -lSDL -lm
"${cross}strip" "$stage/input-test-sdl-1.2"
cp "$src/data/input-test-sdl1.png" "$stage/"
cp "$src/data/jstester-1.2.gcw0.desktop" "$stage/default.gcw0.desktop"
sed -i 's/X-OD-NeedsGSensor=true/X-OD-NeedsGSensor=false/' "$stage/default.gcw0.desktop"
"/workspace/output/rg280v/host/bin/mksquashfs" "$stage" "$out/input-test-rg280v.opk" \
    -all-root -noappend -no-exports -no-xattrs -no-progress \
    -mkfs-time 0 -all-time 0 >/dev/null
readelf -A "$stage/input-test-sdl-1.2" | grep 'Tag_GNU_MIPS_ABI_FP: Soft float'
CONTAINER

source_export="$out/input-test-source-export"
rm -rf "$source_export"
mkdir -p "$source_export"
tar -C "$source_dir" --exclude=.git -cf - . | tar -C "$source_export" -xf -
cp "$repo_root/scripts/stubs/rg280v-no-shake/shake.h" "$source_export/"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" \
    -v "$repo_root:/workspace" -w /workspace \
    plumos-jz47xx-build:bookworm \
    tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
    -C /workspace/output/rg280v-apps/input-test-source-export \
    -czf /workspace/output/rg280v-apps/input-test-rg280v-source.tar.gz .
shasum -a 256 "$out/input-test-rg280v.opk" "$out/input-test-rg280v-source.tar.gz"
