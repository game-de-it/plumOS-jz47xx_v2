#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
base="$out/pcsx4all-source"
[[ -d "$base/src/libShake/include" ]] || {
    echo "Build the regular PCSX4ALL first to obtain libShake" >&2
    exit 1
}

build_variant() {
    local variant=$1 url commit source_dir patch
    case "$variant" in
        ninoh)
            url=https://github.com/Ninoh-FOX/PCSX4ALL.git
            commit=09681c2b697e69b18b48541e224e7369373f5a2e
            ;;
        soarqin)
            url=https://github.com/soarqin/RG350_pcsx4all.git
            commit=bff0e8b371238078939a15ca161b342c287fbef0
            ;;
        gameblabla)
            url=https://github.com/gameblabla/pcsx4all.git
            commit=21084ac2f11cd719fc6c1ce745538f3aae54a043
            ;;
        *) echo "Unknown variant: $variant" >&2; exit 2 ;;
    esac
    source_dir="$out/pcsx4all-$variant"
    patch="$repo_root/scripts/patches/pcsx4all-$variant-rg280v-test.patch"
    if [[ ! -d "$source_dir/.git" ]]; then
        git clone "$url" "$source_dir"
        git -C "$source_dir" checkout --detach "$commit"
    fi
    [[ $(git -C "$source_dir" rev-parse HEAD) == "$(git -C "$source_dir" rev-parse "$commit")" ]] || {
        echo "Unexpected $variant revision; expected $commit" >&2
        exit 1
    }
    rsync -a "$base/src/libShake/" "$source_dir/src/libShake/"
    if ! git -C "$source_dir" apply --reverse --check "$patch" >/dev/null 2>&1; then
        git -C "$source_dir" apply "$patch"
    fi

    if [[ "$variant" == gameblabla ]]; then
        python3 - "$source_dir" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
makefile = (source / "Makefile.gcw0").read_text()
anchor = "CXXFLAGS := $(CFLAGS)"
assert makefile.count(anchor) == 1
makefile = makefile.replace(anchor, """CFLAGS += -Isrc/libShake/include
OBJDIRS += obj/libShake obj/libShake/src obj/libShake/src/common obj/libShake/src/linux
OBJS += obj/libShake/src/common/error.o obj/libShake/src/common/helpers.o \\
    obj/libShake/src/common/presets.o obj/libShake/src/linux/shake.o

CXXFLAGS := $(CFLAGS)""")
(source / "Makefile.rg280v-variant").write_text(makefile)
PY
    else
        cp "$base/Makefile.rg350_odbeta" "$source_dir/Makefile.rg280v-variant"
    fi

    docker run --rm -i --platform linux/arm64 \
        --user "$(id -u):$(id -g)" -e HOME=/tmp -e PCSX_VARIANT="$variant" \
        -v "$repo_root:/workspace" \
        -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
        -w "/workspace/output/rg280v-emulators/pcsx4all-$variant" \
        plumos-jz47xx-build:bookworm bash -s >"$out/pcsx4all-$variant-build.log" 2>&1 <<'CONTAINER'
set -euo pipefail
export PATH=/workspace/output/rg280v/host/bin:$PATH
cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
sysroot=$(${cross}gcc -print-sysroot)
common=(CC="${cross}gcc" CXX="${cross}g++" LD="${cross}g++"
    'C_ARCH=-mips32r2 -msoft-float -DGCW_ZERO -DRG350 -DDINGUX_BETA -DSHMEM_MIRRORING')
if [[ "$PCSX_VARIANT" == gameblabla ]]; then
    args=("${common[@]}" 'LDFLAGS=-lSDL -lrt -lz -lm')
else
    args=("${common[@]}" HUGEEDIT=true HAVE_CHD=0 DEV=1
        "LDFLAGS=-L$sysroot/usr/lib -lSDL -lrt -lz -lm")
fi
make -f Makefile.rg280v-variant clean "${args[@]}"
make -f Makefile.rg280v-variant -j4 "${args[@]}"
"${cross}strip" -o "/workspace/output/rg280v-emulators/pcsx4all-$PCSX_VARIANT-rg280v" pcsx4all
readelf -A "/workspace/output/rg280v-emulators/pcsx4all-$PCSX_VARIANT-rg280v" \
    | grep 'Tag_GNU_MIPS_ABI_FP: Soft float'
CONTAINER
    shasum -a 256 "$out/pcsx4all-$variant-rg280v"
}

if (( $# )); then
    for variant in "$@"; do build_variant "$variant"; done
else
    for variant in ninoh soarqin gameblabla; do build_variant "$variant"; done
fi
