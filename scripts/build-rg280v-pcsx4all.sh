#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
source_dir="$out/pcsx4all-source"
commit=ab17108051d2178465da58ce377225575d680e5e
submodule=7f643c813f1ffea659fb85a47b14d8fbda18cce1
patch="$repo_root/scripts/patches/pcsx4all-rg280v.patch"

mkdir -p "$out"
if [[ ! -d "$source_dir/.git" ]]; then
    git clone --depth 1 https://github.com/jdgleaver/RG350_pcsx4all.git "$source_dir"
    git -C "$source_dir" fetch --depth 1 origin "$commit"
    git -C "$source_dir" checkout --detach "$commit"
fi
[[ $(git -C "$source_dir" rev-parse HEAD) == "$commit" ]] || {
    echo "Unexpected PCSX4ALL source revision" >&2
    exit 1
}
git -C "$source_dir" submodule update --init --depth 1 src/libShake
[[ $(git -C "$source_dir/src/libShake" rev-parse HEAD) == "$submodule" ]] || {
    echo "Unexpected libShake revision" >&2
    exit 1
}
if ! git -C "$source_dir" apply --reverse --check "$patch" >/dev/null 2>&1; then
    git -C "$source_dir" apply "$patch"
fi

docker run --rm -i --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace/output/rg280v-emulators/pcsx4all-source \
    plumos-jz47xx-build:bookworm bash -s >"$out/pcsx4all-build.log" 2>&1 <<'CONTAINER'
set -euo pipefail
export PATH=/workspace/output/rg280v/host/bin:$PATH
cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
sysroot=$(${cross}gcc -print-sysroot)
args=(
    CC="${cross}gcc" CXX="${cross}g++" LD="${cross}g++"
    HUGEEDIT=true HAVE_CHD=1 DEV=1
    'C_ARCH=-mips32r2 -msoft-float -DGCW_ZERO -DRG350 -DDINGUX_BETA -DSHMEM_MIRRORING'
    "LDFLAGS=-L$sysroot/usr/lib -lSDL -lrt -lz -lm"
)
make -f Makefile.rg350_odbeta clean "${args[@]}"
make -f Makefile.rg350_odbeta -j4 "${args[@]}"
"${cross}strip" -o /workspace/output/rg280v-emulators/pcsx4all_rg280v pcsx4all
readelf -A /workspace/output/rg280v-emulators/pcsx4all_rg280v | grep 'Tag_GNU_MIPS_ABI_FP: Soft float'
CONTAINER

test -s "$out/pcsx4all_rg280v"
tar -C "$source_dir" --exclude=.git --exclude=obj --exclude=pcsx4all \
    -czf "$out/pcsx4all_rg280v-source.tar.gz" .
shasum -a 256 "$out/pcsx4all_rg280v"
