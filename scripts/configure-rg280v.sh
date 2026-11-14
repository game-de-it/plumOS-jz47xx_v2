#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
"$repo_root/scripts/fetch-upstream.sh" >/dev/null
output_dir="$repo_root/output/rg280v"
mkdir -p "$output_dir"
volume=plumos-jz47xx-rg280v-build
docker volume create "$volume" >/dev/null

image=plumos-jz47xx-build:bookworm
if ! docker image inspect "$image" >/dev/null 2>&1; then
    docker build -t "$image" -f "$repo_root/docker/Dockerfile" "$repo_root/docker"
fi

docker run --rm --platform linux/arm64 \
    --user root \
    -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v "$volume:/workspace/output/rg280v" -w /workspace "$image" \
    chown "$(id -u):$(id -g)" /workspace/output/rg280v

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v "$volume:/workspace/output/rg280v" -w /workspace "$image" \
    make -C /workspace/work/buildroot O=/workspace/output/rg280v \
        BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace \
        BR2_DEFCONFIG=/workspace/configs/plumos_rg280v_defconfig defconfig

printf 'Configured Docker volume %s\n' "$volume"
