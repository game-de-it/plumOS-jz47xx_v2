#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
destination="$repo_root/output/rg280v-emulators"
archive="$destination/libpng-1.4.22.tar.gz"
expected=64b0632f7c528a7afd58c351be416fba3c9348a50a31b465d937e718febe81a7
mkdir -p "$destination"

if [[ ! -f "$archive" ]]; then
    curl -fL --retry 2 --output "$archive.download" \
        https://rsync.osuosl.org/pub/libpng/src/archive/gz/libpng14/libpng-1.4.22.tar.gz
    mv "$archive.download" "$archive"
fi
actual=$(shasum -a 256 "$archive" | awk '{print $1}')
[[ "$actual" == "$expected" ]] || { echo 'libpng source hash mismatch' >&2; exit 1; }

"$repo_root/scripts/configure-rg280v.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm \
    bash /workspace/scripts/build-rg280v-emulator-libs-in-container.sh
