#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
source_dir="$repo_root/work/buildroot"
expected=98ce2f08d1ca54d8916b47f37ee866d1d0a0d4e0

if [[ ! -d "$source_dir/.git" ]]; then
    mkdir -p "$repo_root/work"
    git init "$source_dir" >/dev/null
    git -C "$source_dir" remote add origin https://github.com/OpenDingux/buildroot.git
    git -C "$source_dir" fetch --depth 1 --filter=blob:none origin "$expected"
    git -C "$source_dir" checkout --detach FETCH_HEAD
fi

actual=$(git -C "$source_dir" rev-parse HEAD)
if [[ "$actual" != "$expected" ]]; then
    echo "OpenDingux revision mismatch: $actual (expected $expected)" >&2
    exit 1
fi
if [[ -n "$(git -C "$source_dir" status --porcelain)" ]]; then
    echo "OpenDingux source has local changes" >&2
    exit 1
fi
printf '%s\n' "$source_dir"
