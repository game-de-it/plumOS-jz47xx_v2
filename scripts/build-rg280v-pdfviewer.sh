#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-apps"
source_dir="$out/pdfviewer-source"
original="$out/pdfviewer-source-original.tar.gz"
stage="$out/pdfviewer-stage"
export_dir="$out/pdfviewer-source-export"
patch_file="$repo_root/scripts/patches/pdfviewer-rg280v.patch"
image=plumos-jz47xx-build:bookworm
volume=plumos-jz47xx-rg280v-build
mkdir -p "$out"

if [[ ! -f "$original" ]]; then
    curl -L --fail --silent --show-error \
        'https://drive.google.com/uc?export=download&id=0BwYi4RGX-HSaUVpaajlDRG9BSGc' \
        -o "$original"
fi
printf '%s  %s\n' \
    d42918c4fe1378384b296a9cce38cd34a534698e29bc70ae1ca5725e36220e83 \
    "$original" | shasum -a 256 -c - >/dev/null
mkdir -p "$source_dir"
if [[ ! -f "$source_dir/pdfviewer.cpp" ]]; then
    tar -xzf "$original" -C "$source_dir"
fi
if ! patch -d "$source_dir" -p1 --dry-run -R < "$patch_file" >/dev/null 2>&1; then
    patch -d "$source_dir" -p1 < "$patch_file" >/dev/null
fi
cp "$repo_root/scripts/rg280v-pdfviewer-build.py" "$source_dir/build-rg280v.py"

docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace/output/rg280v-apps/pdfviewer-source "$image" \
    python3 build-rg280v.py > "$out/pdfviewer-build.log" 2>&1 || {
        tail -80 "$out/pdfviewer-build.log" >&2
        exit 1
    }

rm -rf "$stage"
mkdir -p "$stage"
cp "$source_dir/build-rg280v/pdfviewer" "$stage/pdfviewer"
cp -R "$source_dir/basfonts" "$stage/"
cp "$source_dir/raiz/copying.txt" "$stage/COPYING-xpdf.txt"
cp "$source_dir/basfonts/readme" "$stage/COPYING-fonts.txt"
cp "$repo_root/assets/rg280v-apps/pdfviewer-rg280v.sh" \
   "$repo_root/assets/rg280v-apps/pdfviewer.rg280v.desktop" "$stage/"
cp "$source_dir/icons/icongcw.png" "$stage/pdfviewer.png"
chmod 755 "$stage/pdfviewer-rg280v.sh"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -e HOME=/tmp \
    -v "$repo_root:/workspace" -v "$volume:/workspace/output/rg280v" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
        ${cross}strip "$out/pdfviewer-stage/pdfviewer"
        ${cross}readelf -A "$out/pdfviewer-stage/pdfviewer" | grep "Tag_GNU_MIPS_ABI_FP: Soft float"
        /workspace/output/rg280v/host/bin/mksquashfs \
            "$out/pdfviewer-stage" "$out/pdfviewer-rg280v.opk" \
            -all-root -noappend -no-exports -no-xattrs -no-progress \
            -mkfs-time 0 -all-time 0 >/dev/null
    '

rm -rf "$export_dir"
mkdir -p "$export_dir/pdfviewer"
tar -xzf "$original" -C "$export_dir/pdfviewer"
patch -d "$export_dir/pdfviewer" -p1 < "$patch_file" >/dev/null
rm -rf "$export_dir/pdfviewer/built" "$export_dir/pdfviewer/obj" \
    "$export_dir/pdfviewer/pdfviewer.opk"
cp "$repo_root/scripts/rg280v-pdfviewer-build.py" "$export_dir/pdfviewer/build-rg280v.py"
cp "$repo_root/assets/rg280v-apps/"{pdfviewer-rg280v.sh,pdfviewer.rg280v.desktop} \
   "$export_dir/pdfviewer/"
docker run --rm --platform linux/arm64 \
    --user "$(id -u):$(id -g)" -v "$repo_root:/workspace" \
    -w /workspace "$image" bash -lc '
        set -e
        out=/workspace/output/rg280v-apps
        tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
            -C "$out/pdfviewer-source-export" \
            -czf "$out/pdfviewer-rg280v-source.tar.gz" pdfviewer
    '
shasum -a 256 "$out/pdfviewer-rg280v.opk" "$out/pdfviewer-rg280v-source.tar.gz"
