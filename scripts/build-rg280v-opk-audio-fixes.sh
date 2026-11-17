#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
for name in ohboy genesis-gx; do
 src="$root/output/rg280v-apps/$name-src"
 case "$name" in
  ohboy) expected=4720bcf5fbb4d80d85d6f623847d29cefea2cd94 ;;
  genesis-gx) expected=2499cd3e3d1d8b7d0130d8b2825adb4cc608b2c0 ;;
 esac
 [ "$(git -C "$src" rev-parse HEAD)" = "$expected" ] || { echo "Unexpected source revision: $name" >&2; exit 1; }
 patch="$root/patches/rg280v-$name-audio.patch"
 if [ "$name" = ohboy ]; then patch="$root/patches/rg280v-ohboy-audio-menu.patch"; fi
 if ! git -C "$src" apply --unidiff-zero --reverse --check "$patch" 2>/dev/null; then
  git -C "$src" apply --unidiff-zero --check "$patch"
  git -C "$src" apply --unidiff-zero "$patch"
 fi
done
docker run --rm --platform linux/arm64 -v "$root:/workspace" \
 -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
 -w /workspace plumos-jz47xx-build:bookworm bash -euc '
 t=/workspace/output/rg280v/host/bin
 inc=/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL
 work=output/rg280v-apps
 cd "$work/ohboy-src"
 make -f Makefile.gcwzero -j8 CC="$t/mipsel-gcw0-linux-uclibc-gcc" STRIP="$t/mipsel-gcw0-linux-uclibc-strip" \
 CFLAGS="-O3 -mips32r2 -msoft-float -fcommon -I$inc -D_GNU_SOURCE=1 -D_REENTRANT -DDINGOO_BUILD -DDINGOO_OPENDINGUX -DGCWZERO -DDISABLE_ROMBROWSER" \
 LIBS="-lSDL -lSDL_image -lz -lm" >/workspace/output/rg280v-apps/ohboy-build.log 2>&1
 cd ../genesis-gx-src/gcw0
 make -j8 CC="$t/mipsel-gcw0-linux-uclibc-gcc" \
 CFLAGS="-O3 -mips32r2 -msoft-float -fcommon -I$inc -D_GNU_SOURCE=1 -D_REENTRANT -std=gnu99" \
 LIBS="-lSDL -lSDL_ttf -lSDL_image -lz -lm -lvorbisfile -lasound" \
 INCLUDES="-I../core -I../core/z80 -I../core/m68k -I../core/sound -I../core/sound/minimp3 -I../core/input_hw -I../core/cart_hw -I../core/cart_hw/svp -I../core/cd_hw -I../core/ntsc -I../gcw0" \
 >/workspace/output/rg280v-apps/genesis-gx-build.log 2>&1
 cd /workspace
 for spec in "49 ohboy-src/ohboy.gcw0 ohboy.gcw0" "12 genesis-gx-src/gcw0/gen_gcw0 gen_gcw0"; do
  set -- $spec
  stage="$work/audio-fix-stage-$1"
  rm -rf "$stage"
  src="$work/rg350-catalog/ohboy.opk"
  if [ "$1" = 12 ]; then src="$work/rg350-catalog/GenesisPlusGX_2019-12-23.opk"; fi
  "$t/unsquashfs" -f -no-progress -d "$stage" "$src" >/dev/null
  cp "$work/$2" "$stage/$3"
  "$t/mipsel-gcw0-linux-uclibc-readelf" -A "$stage/$3" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
  output="$work/rg350-audio-fixed-$1.opk"
  rm -f "$output"
  "$t/mksquashfs" "$stage" "$output" -all-root -noappend -no-exports -comp gzip -no-progress >/dev/null
  sha256sum "$output"
 done
 '
