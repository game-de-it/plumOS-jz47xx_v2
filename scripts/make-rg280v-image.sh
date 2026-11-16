#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
"$repo_root/scripts/fetch-rg280v-emulators.sh"
"$repo_root/scripts/repack-rg280v-regba.sh"
"$repo_root/scripts/repack-rg280v-gambatte.sh"
"$repo_root/scripts/build-rg280v-picodrive.sh"
"$repo_root/scripts/build-rg280v-pcsx4all.sh"
"$repo_root/scripts/build-rg280v-picoarch.sh"
PLUMOS_PICOARCH_RECIPES="$repo_root/scripts/rg280v-picoarch-extra-cores.tsv" \
    PLUMOS_PICOARCH_CORE_FILTER=mednafen_wswan \
    "$repo_root/scripts/build-rg280v-picoarch-cores.sh"
"$repo_root/scripts/build-rg280v-fceux-menu.sh"
"$repo_root/scripts/build-rg280v-gambatte-menu.sh"
"$repo_root/scripts/build-rg280v-emulator-libs.sh"
"$repo_root/scripts/build-rg280v-status.sh"
"$repo_root/scripts/build-rg280v-fe.sh"
"$repo_root/scripts/verify-rg280v-build.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace \
    plumos-jz47xx-build:bookworm \
    bash /workspace/scripts/make-rg280v-image-in-container.sh
