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
[[ -x "$build/target/etc/init.d/rcS" ]]
[[ -x "$build/target/usr/sbin/plumos-usb-ecm" ]]
[[ -x "$build/target/usr/sbin/plumos-first-boot" ]]
[[ -d "$build/target/media/user" ]]
[[ -x "$build/target/sbin/mkfs.fat" ]]
[[ ! -e "$build/target/etc/init.d/S94plumos-dev-usb" ]]
[[ ! -e "$build/target/usr/sbin/frontend_start" ]]
grep -q 'tty1::respawn:/bin/sh' "$build/target/etc/inittab"
grep -q '/sbin/ip addr add 10.1.1.2/30' "$build/target/etc/init.d/rcS"
grep -q 'USER_MOUNTED' "$build/target/etc/init.d/rcS"
grep -q 'plumos-first-boot' "$build/target/etc/init.d/rcS"
grep -q 'user_label" = PLUMOS' "$build/target/etc/init.d/rcS"
[[ $(wc -c < "$images/ubiboot-rg350.bin") -le 8192 ]]

"$build/host/bin/unsquashfs" -ll "$images/modules.squashfs" > "$build/modules-list.txt"
grep -q 'snd-usb-audio.ko' "$build/modules-list.txt"

printf 'RG280V build artifacts verified\n'
