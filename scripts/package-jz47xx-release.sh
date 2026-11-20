#!/usr/bin/env bash
# Package the exact IMG identified in the hardware validation record.
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
    echo "Usage: $0 VERIFIED_IMG VERIFIED_SHA256 [OUTPUT_DIR]" >&2
    exit 2
fi
image=$1
expected_sha=$2
output=${3:-output/release}
name=${image##*/}
if [[ ! -f "$image" || ! $name =~ ^plumOS-JZ47xx-([0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z][0-9A-Za-z.-]*)?)\.img$ ||
      ! $expected_sha =~ ^[a-f0-9]{64}$ ]]; then
    echo "Expected a plumOS-JZ47xx versioned IMG and a lowercase SHA-256." >&2
    exit 2
fi
version=${name#plumOS-JZ47xx-}
version=${version%.img}
archive="plumOS-JZ47xx-v$version-sd-image.7z"
image_dir=$(cd "$(dirname -- "$image")" && pwd)

if command -v sha256sum >/dev/null 2>&1; then
    sha_command=(sha256sum)
else
    sha_command=(shasum -a 256)
fi
if command -v 7zz >/dev/null 2>&1; then
    seven_zip=7zz
else
    seven_zip=7z
fi

digest=$("${sha_command[@]}" <"$image")
if [[ ${digest%% *} != "$expected_sha" ]]; then
    echo "IMG SHA-256 does not match the hardware validation record." >&2
    exit 1
fi

mkdir -p "$output"
output=$(cd "$output" && pwd)
for file in "$archive" SHA256SUMS; do
    if [[ -e "$output/$file" || -L "$output/$file" ]]; then
        echo "Output already exists: $output/$file" >&2
        exit 1
    fi
done
stage=$(mktemp -d "$output/.packaging.XXXXXXXX")
cleanup() {
    for file in "$stage/$archive" "$stage/SHA256SUMS"; do
        if [[ -f "$file" ]]; then unlink "$file"; fi
    done
    rmdir "$stage"
}
trap cleanup EXIT
(
    cd "$image_dir"
    "$seven_zip" a -mx=3 "$stage/$archive" "./$name" >/dev/null
)
digest=$("$seven_zip" x -so "$stage/$archive" "$name" | "${sha_command[@]}")
if [[ ${digest%% *} != "$expected_sha" ]]; then
    echo "The archived IMG does not match the hardware validation record." >&2
    exit 1
fi
(
    cd "$stage"
    "${sha_command[@]}" "$archive"
    printf '%s  %s\n' "$expected_sha" "$name"
) >"$stage/SHA256SUMS"
mv "$stage/$archive" "$stage/SHA256SUMS" "$output/"
printf '%s\n' "$output/$archive" "$output/SHA256SUMS"
