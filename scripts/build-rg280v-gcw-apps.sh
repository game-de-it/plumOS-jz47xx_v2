#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
volume=plumos-jz47xx-rg280v-build
image=plumos-jz47xx-build:bookworm
mkdir -p "$out"

fetch_source() {
    local name=$1 url=$2 revision=$3 patch=$4 source="$out/$1-source"
    if [[ ! -d "$source/.git" ]]; then
        git clone --depth 1 "$url" "$source"
    fi
    if [[ $(git -C "$source" rev-parse HEAD) != "$revision" ]]; then
        git -C "$source" fetch --depth 1 origin "$revision"
        git -C "$source" checkout --detach "$revision"
    fi
    [[ $(git -C "$source" rev-parse HEAD) == "$revision" ]] || exit 1
    if ! git -C "$source" apply --reverse --check "$patch" >/dev/null 2>&1; then
        git -C "$source" apply "$patch"
    fi
}

"$repo_root/scripts/configure-rg280v.sh"
if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" make -C /workspace/work/buildroot \
    O=/workspace/output/rg280v \
    BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace \
    sdl2 sdl2_image sdl2_ttf > "$out/sdl2-build.log" 2>&1; then
    tail -60 "$out/sdl2-build.log" >&2
    exit 1
fi

fetch_source calculator https://github.com/Jakz/open-dingux-calculator.git \
    582173c1d89e80ea699115860b754347c9757e90 \
    "$repo_root/scripts/patches/calculator-rg280v.patch"
fetch_source commander https://github.com/od-contrib/commander.git \
    a6ef30eb3bd6ef80a031744aae0f5b9cd974c182 \
    "$repo_root/scripts/patches/commander-rg280v.patch"
cp "$repo_root/scripts/patches/commander-rg280v-defs.cmake" \
    "$out/commander-source/CMake/rg280v_defs.cmake"

if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -e 'CXXFLAGS=-msoft-float -DPLUMOS_RG280V' -e LDFLAGS=-msoft-float \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace/output/rg280v-apps/calculator-source/projects/opendingux \
    "$image" bash -lc '
        set -e
        make CROSS=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc- clean
        make CROSS=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
    ' > "$out/calculator-build.log" 2>&1; then
    tail -60 "$out/calculator-build.log" >&2
    exit 1
fi

if ! docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        cmake=/workspace/output/rg280v/host/bin/cmake
        source=/workspace/output/rg280v-apps/commander-source
        build=/workspace/output/rg280v-apps/commander-sdl2-build
        "$cmake" -S "$source" -B "$build" -DCMAKE_BUILD_TYPE=Release \
            -DTARGET_PLATFORM=rg280v -DWITH_SYSTEM_SDL_TTF=ON \
            -DCMAKE_TOOLCHAIN_FILE=/workspace/output/rg280v/host/share/buildroot/toolchainfile.cmake \
            -DCMAKE_C_FLAGS=-msoft-float -DCMAKE_CXX_FLAGS=-msoft-float
        "$cmake" --build "$build" -j8
    ' > "$out/commander-build.log" 2>&1; then
    tail -60 "$out/commander-build.log" >&2
    exit 1
fi

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -s <<'CONTAINER'
set -euo pipefail
out=/workspace/output/rg280v-apps
cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
sysroot=$(${cross}gcc -print-sysroot)
mkdir -p "$out/runtime-lib" "$out/calculator-stage/data" "$out/commander-stage/res"

for name in libSDL2-2.0.so.0 libSDL2_image-2.0.so.0 libSDL2_ttf-2.0.so.0; do
    cp -L "$sysroot/usr/lib/$name" "$out/runtime-lib/$name"
done
cp /workspace/output/rg280v/build/sdl2-2.28.5/LICENSE.txt "$out/runtime-lib/SDL2-LICENSE.txt"
cp /workspace/output/rg280v/build/sdl2_image-2.6.3/LICENSE.txt "$out/runtime-lib/SDL2_image-LICENSE.txt"
cp /workspace/output/rg280v/build/sdl2_ttf-2.20.2/LICENSE.txt "$out/runtime-lib/SDL2_ttf-LICENSE.txt"

cp "$out/calculator-source/projects/opendingux/odcalc" "$out/calculator-stage/"
${cross}strip "$out/calculator-stage/odcalc"
cp "$out/calculator-source/data/"* "$out/calculator-stage/data/"
cp "$out/calculator-source/projects/opendingux/default.gcw0.desktop" "$out/calculator-stage/"
cp "$out/calculator-source/projects/opendingux/icon.png" "$out/calculator-stage/"

cp "$out/commander-sdl2-build/commander" "$out/commander-stage/"
${cross}strip "$out/commander-stage/commander"
cp "$out/commander-source/res/"*.png "$out/commander-source/res/"*.ttf "$out/commander-stage/res/"
cp "$out/commander-source/opkg/default.gcw0.desktop" "$out/commander-stage/"
cp "$out/commander-source/opkg/commander.png" "$out/commander-stage/"

for name in calculator commander; do
    /workspace/output/rg280v/host/bin/mksquashfs "$out/$name-stage" \
        "$out/$name-rg280v.opk" -all-root -noappend -no-exports -no-xattrs \
        -no-progress -mkfs-time 0 -all-time 0 >/dev/null
    ${cross}readelf -A "$out/$name-stage/$([[ $name == calculator ]] && echo odcalc || echo commander)" \
        | grep 'Tag_GNU_MIPS_ABI_FP: Soft float'
done
CONTAINER

source_export="$out/source-export"
rm -rf "$source_export"
mkdir -p "$source_export/calculator" "$source_export/commander"
tar -C "$out/calculator-source" --exclude=.git --exclude='*.o' \
    --exclude=odcalc --exclude=projects/opendingux/data -cf - . \
    | tar -C "$source_export/calculator" -xf -
tar -C "$out/commander-source" --exclude=.git -cf - . \
    | tar -C "$source_export/commander" -xf -
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -v "$repo_root:/workspace" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        for name in calculator commander; do
            tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
                -C "$out/source-export" -czf "$out/$name-rg280v-source.tar.gz" "$name"
        done
    '
shasum -a 256 "$out/calculator-rg280v.opk" "$out/commander-rg280v.opk" \
    "$out/calculator-rg280v-source.tar.gz" "$out/commander-rg280v-source.tar.gz"
