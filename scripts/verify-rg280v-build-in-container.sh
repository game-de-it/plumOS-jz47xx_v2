#!/usr/bin/env bash
set -euo pipefail

build=/workspace/output/rg280v
images="$build/images"

for name in uzImage.bin rg280v.dtb rootfs.squashfs modules.squashfs mininit-syspart ubiboot-rg350.bin; do
    [[ -s "$images/$name" ]] || { echo "Missing $name" >&2; exit 1; }
done

grep -q 'CONFIG_SND_USB_AUDIO=m' "$build/build/linux-custom/.config"
grep -a -q 'ylm,rg280v' "$images/rg280v.dtb"
[[ -x "$build/target/usr/bin/adbd" ]]
[[ -x "$build/target/etc/init.d/S94plumos-dev-usb" ]]
[[ $(wc -c < "$images/ubiboot-rg350.bin") -le 8192 ]]

"$build/host/bin/unsquashfs" -ll "$images/modules.squashfs" > "$build/modules-list.txt"
grep -q 'snd-usb-audio.ko' "$build/modules-list.txt"

printf 'RG280V build artifacts verified\n'
