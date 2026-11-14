#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
"$repo_root/scripts/fetch-rg280v-emulators.sh"

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" \
    -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
    -w /workspace plumos-jz47xx-build:bookworm \
    bash -c '
        set -euo pipefail
        out=/workspace/output/rg280v-emulators
        tools=/workspace/output/rg280v/host/bin
        stage=$out/gambatte-rg280v-stage
        mkdir -p "$stage"
        find "$stage" -mindepth 1 -delete
        "$tools/unsquashfs" -f -d "$stage" "$out/gambatte-dms-multi-r572u4-20211021.opk" >/dev/null
        python3 - "$stage/default.gcw0.desktop" <<"PY"
import sys
path = sys.argv[1]
with open(path, encoding="utf-8") as stream:
    source = stream.read()
before = "Exec=gambatte-dms.gcw0 %f"
assert source.count(before) == 1, "unexpected Gambatte launcher"
with open(path, "w", encoding="utf-8") as stream:
    stream.write(source.replace(before, "Exec=gambatte-dms.gcw0 --resampler 0 %f"))
PY
        "$tools/mksquashfs" "$stage" "$out/gambatte-dms-rg280v.opk.new" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -all-time 0 -mkfs-time 0 >/dev/null
        mv "$out/gambatte-dms-rg280v.opk.new" "$out/gambatte-dms-rg280v.opk"
        find "$stage" -mindepth 1 -delete
        rmdir "$stage"
    '
shasum -a 256 "$out/gambatte-dms-rg280v.opk"
