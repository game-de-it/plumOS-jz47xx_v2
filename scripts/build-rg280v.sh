#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
volume=plumos-jz47xx-rg280v-build
if ! docker run --rm --platform linux/arm64 \
    -v "$volume:/workspace/output/rg280v" \
    plumos-jz47xx-build:bookworm \
    test -f /workspace/output/rg280v/.config 2>/dev/null; then
    "$repo_root/scripts/configure-rg280v.sh"
fi

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v "$volume:/workspace/output/rg280v" -w /workspace \
    plumos-jz47xx-build:bookworm \
    make -C /workspace/work/buildroot O=/workspace/output/rg280v \
        BR2_DL_DIR=/workspace/work/dl -j "${JOBS:-8}"
