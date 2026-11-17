#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
docker run --rm --platform linux/arm64 \
  -v "$root:/workspace" \
  -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
  -w /workspace plumos-jz47xx-build:bookworm bash -euc '
    t=/workspace/output/rg280v/host
    for variant in source-repair sdl2; do
      define=
      if [ "$variant" = sdl2 ]; then define=-DHEALTH_SDL2; fi
    "$t/bin/mipsel-gcw0-linux-uclibc-gcc" -O2 $define -fPIC -shared -mips32r2 -msoft-float \
      -I"$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL" \
      scripts/probe-rg280v-standalone-health.c \
      -o output/rg280v-apps/libstandalone-health-$variant.so -ldl -lrt -lasound
    done
  '
