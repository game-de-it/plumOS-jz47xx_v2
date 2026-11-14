#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
"$repo_root/scripts/build-rg280v-status.sh"
"$repo_root/scripts/verify-rg280v-build.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace \
    plumos-jz47xx-build:bookworm \
    bash /workspace/scripts/make-rg280v-image-in-container.sh
