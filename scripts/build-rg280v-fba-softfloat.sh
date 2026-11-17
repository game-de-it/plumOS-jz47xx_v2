#!/usr/bin/env bash
# Rebuild the upstream FBA .44 release for the RG280V soft-float ABI.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
work="$root/output/rg280v-apps/rg350-visual-tests"
src="$work/fba-sdl-src"
release="$work/fba-multi-od-beta-fix06.opk"
output="$work/fba44-rg280v-softfloat.opk"
stage="$work/fba-softfloat-stage"
patch="$root/patches/rg280v-fba-menu.patch"

for path in "$src/Makefile.dingux" "$release" \
    "$work/avir-2.5/avir.h" \
    "$work/json_include/single_include/nlohmann/json.hpp" \
    "$work/png++-0.2.9/output/include/png++/png.hpp" \
    "$work/boost_1_73_0/boost/algorithm/string/trim.hpp"; do
    [[ -e "$path" ]] || { echo "Missing build input: $path" >&2; exit 1; }
done
[[ -f "$patch" ]] || { echo "Missing source patch: $patch" >&2; exit 1; }
if ! git -C "$src" apply --unidiff-zero --reverse --check "$patch" 2>/dev/null; then
    git -C "$src" apply --unidiff-zero --check "$patch"
    git -C "$src" apply --unidiff-zero "$patch"
fi

docker run --rm --platform linux/arm64 \
    -v "$root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace/output/rg280v-apps/rg350-visual-tests/fba-sdl-src \
    plumos-jz47xx-build:bookworm bash -euc '
        tools=/workspace/output/rg280v/host/bin
        flags="-mips32r2 -msoft-float"
        make -f Makefile.dingux init TOOLCHAIN_DIR="$tools/" CFLAGS_ARCH="$flags" USE_LIBAO= DEPEND=
        make -f Makefile.dingux obj/dingux/dep/generated/m68kops.h \
            TOOLCHAIN_DIR="$tools/" CFLAGS_ARCH="$flags" USE_LIBAO= DEPEND=
        make -f Makefile.dingux -j8 TOOLCHAIN_DIR="$tools/" CFLAGS_ARCH="$flags" USE_LIBAO= DEPEND= \
            >/workspace/output/rg280v-apps/rg350-visual-tests/fba-build.log 2>&1
        cd /workspace
        stage=output/rg280v-apps/rg350-visual-tests/fba-softfloat-stage
        rm -rf -- "$stage"
        "$tools/unsquashfs" -no-progress -d "$stage" \
            output/rg280v-apps/rg350-visual-tests/fba-multi-od-beta-fix06.opk >/dev/null
        cp output/rg280v-apps/rg350-visual-tests/fba-sdl-src/bin/fbasdl.dge "$stage/fbasdl.dge"
        output=output/rg280v-apps/rg350-visual-tests/fba44-rg280v-softfloat.opk
        python3 -c "from pathlib import Path; Path(\"$output\").unlink(missing_ok=True)"
        "$tools/mksquashfs" "$stage" "$output" -all-root -noappend -no-exports -comp gzip -no-progress >/dev/null
        "$tools/mipsel-gcw0-linux-uclibc-readelf" -A "$stage/fbasdl.dge" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
    '
shasum -a 256 "$output"
