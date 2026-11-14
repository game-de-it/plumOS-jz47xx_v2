#!/usr/bin/env bash
set -euo pipefail

out=/workspace/output/rg280v-emulators
work="$out/regba-open-bios-work"
rm -rf "$work"
mkdir -p "$work"
/build/host/bin/unsquashfs -d "$work" "$out/ReGBA_2019-12-26.opk" >/dev/null
original_md5=$(md5sum "$work/gba_bios.bin" | awk '{print $1}')
[[ "$original_md5" == a860e8c0b6d573d191e4ec7db1b1e4f6 ]] || {
    echo 'unexpected BIOS in ReGBA OPK' >&2
    exit 1
}
cp "$out/mit-gba-bios.bin" "$work/gba_bios.bin"
cp "$out/MIT-GBA-BIOS-LICENSE" "$work/BIOS-LICENSE.txt"
rm -f "$out/ReGBA_2019-12-26-open-bios.opk"
/build/host/bin/mksquashfs "$work" "$out/ReGBA_2019-12-26-open-bios.opk" \
    -comp gzip -noappend -all-root -mkfs-time 0 -all-time 0 >/dev/null
expected=d2549262475851a7eb0a9a7dece2dfbc4d6251d16990e142fa02e5d2e6e98aaa
actual=$(sha256sum "$out/ReGBA_2019-12-26-open-bios.opk" | awk '{print $1}')
[[ "$actual" == "$expected" ]] || { echo 'repacked ReGBA hash mismatch' >&2; exit 1; }
echo "$actual  $out/ReGBA_2019-12-26-open-bios.opk"
