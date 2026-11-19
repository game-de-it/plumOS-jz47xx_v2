#!/bin/bash
# Package an app-private etnaviv fix; do not install to target/staging or flash OS.
set -euo pipefail
cd "$(dirname "$0")/.."
docker run --rm --platform linux/arm64 -i -v "$PWD:/workspace" \
 -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v -w /workspace \
 plumos-jz47xx-build:bookworm bash -s <<'BUILD'
set -eu
export PATH=/workspace/output/rg280v/host/bin:$PATH
w=/workspace/output/rg280v-emulationstation
mesa=/workspace/output/rg280v/build/mesa3d-23.2.1
file=src/gallium/drivers/etnaviv/etnaviv_rs.c
lib=src/gallium/targets/dri/libgallium_dri.so
mkdir -p "$w/runtime/dri"
cp "$mesa/$file" "$w/etnaviv_rs.c.before-private-build"
restore_sdk() {
 cp "$w/etnaviv_rs.c.before-private-build" "$mesa/$file"
 ninja -C "$mesa/build" "$lib"
}
trap restore_sdk EXIT
patch --dry-run -d "$mesa" -p1 < /workspace/patches/rg280v-emulationstation-mesa-tile-blit.patch
patch -d "$mesa" -p1 < /workspace/patches/rg280v-emulationstation-mesa-tile-blit.patch
ninja -C "$mesa/build" "$lib"
cp -L "$mesa/build/$lib" "$w/runtime/dri/libgallium_dri.so"
/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-strip --strip-unneeded "$w/runtime/dri/libgallium_dri.so"
for driver in etnaviv ingenic-drm; do ln -sfn libgallium_dri.so "$w/runtime/dri/${driver}_dri.so"; done
cp "$mesa/docs/license.rst" "$w/runtime/Mesa-LICENSE.rst"
printf 'Packaged private Mesa driver; restoring the SDK source and library.\n'
BUILD
