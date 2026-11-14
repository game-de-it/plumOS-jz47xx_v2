#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
"$repo_root/scripts/fetch-rg280v-emulators.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/build \
    -w /workspace plumos-jz47xx-build:bookworm \
    bash /workspace/scripts/repack-rg280v-regba-in-container.sh
