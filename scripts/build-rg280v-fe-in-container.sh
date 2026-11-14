#!/usr/bin/env bash
set -euo pipefail

cc=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc
strip=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-strip
sysroot=$($cc -print-sysroot)
out=/workspace/output/rg280v-fe
mkdir -p "$out"

"$cc" -std=gnu99 -Os -pipe -Wall -Wextra -D_GNU_SOURCE \
    -DPLUMOS_ENABLE_FBDEV_RENDERER=1 \
    -DPLUMOS_FBDEV_ENABLE_PNG=1 \
    -DPLUMOS_FBDEV_ENABLE_FREETYPE=1 \
    -DPLUMOS_FBDEV_ENABLE_DRM=1 \
    -I"$sysroot/usr/include/freetype2" \
    -I"$sysroot/usr/include/libdrm" \
    /workspace/src/frontend/plumos_controller_ui.c \
    -o "$out/plumos-controller-ui" -lpng -lfreetype -lz -ldrm
"$cc" -std=gnu99 -Os -pipe -Wall -Wextra -D_GNU_SOURCE \
    /workspace/src/frontend/plumos_library_scan.c \
    -o "$out/plumos-library-scan"
"$cc" -std=gnu99 -Os -pipe -Wall -Wextra -D_GNU_SOURCE \
    /workspace/src/frontend/plumos_text_ui.c \
    -o "$out/plumos-text-ui"
"$strip" "$out/plumos-controller-ui" "$out/plumos-library-scan" \
    "$out/plumos-text-ui"
file "$out/plumos-controller-ui" "$out/plumos-library-scan" \
    "$out/plumos-text-ui"
