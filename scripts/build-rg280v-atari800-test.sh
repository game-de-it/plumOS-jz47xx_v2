#!/usr/bin/env bash
# Rebuild the isolated Atari800 4.1.0 visual-test OPK for RG280V.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
work="$root/output/rg280v-apps/rg350-visual-tests"
src="$work/atari800-src"
stage="$work/atari-source-stage"
patch="$root/patches/rg280v-atari800-input-video.patch"
output="$work/atari800-rg280v-input.opk"

for path in "$src/src/Makefile" "$src/src/sdl/input.c" "$stage/default.gcw0.desktop" "$patch"; do
    [[ -f "$path" ]] || { echo "Missing build input: $path" >&2; exit 1; }
done
if ! git -C "$src" apply --unidiff-zero --reverse --check "$patch" 2>/dev/null; then
    git -C "$src" apply --unidiff-zero --check "$patch"
    git -C "$src" apply --unidiff-zero "$patch"
fi

docker run --rm --platform linux/arm64 \
    -v "$root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace/output/rg280v-apps/rg350-visual-tests/atari800-src/src \
    plumos-jz47xx-build:bookworm bash -euc '
        tools=/workspace/output/rg280v/host/bin
        export PATH="$tools:$PATH"
        make -j4 CFLAGS="-O2 -mips32r2 -msoft-float -DPLUMOS_RG280V -ansi -pedantic -Waggregate-return -Wmissing-declarations -Wmissing-prototypes -Wstrict-prototypes -Winline -Wredundant-decls" \
            >/workspace/output/rg280v-apps/rg350-visual-tests/atari-build.log 2>&1
        "$tools/mipsel-gcw0-linux-uclibc-readelf" -A atari800 | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
        cd /workspace
        stage=output/rg280v-apps/rg350-visual-tests/atari-source-stage
        cp output/rg280v-apps/rg350-visual-tests/atari800-src/src/atari800 "$stage/atari800"
        python3 -c "from pathlib import Path; Path(\"output/rg280v-apps/rg350-visual-tests/atari800-rg280v-input.opk\").unlink(missing_ok=True)"
        "$tools/mksquashfs" "$stage" output/rg280v-apps/rg350-visual-tests/atari800-rg280v-input.opk \
            -all-root -noappend -no-exports -comp gzip -no-progress >/dev/null
    '
shasum -a 256 "$output"
