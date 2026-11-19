#!/usr/bin/env bash
# Private device-validation image, assembled from the accepted live runtime.
# It may contain private user configuration/BIOS: never use as a release image.
set -euo pipefail
model=${1:?usage: make-jz47xx-test-image-in-container.sh MODEL}
case "$model" in rg300x|rg350|rg280v|rg350m) ;; *) exit 2 ;; esac
base=/workspace/output/jz47xx-multimodel
boot="$base/boot"
# Linux filesystem: preserve case-sensitive theme names, modes and symlinks.
stage=/workspace/output/rg280v/jz47xx-test-image-stage
root="$stage/data-root"
destination="$base/plumos-jz47xx-test.img"
mkdir -p "$root" "$stage/empty"
test -f "$base/runtime.tar"
test ! -e "$destination" || {
    echo "Existing image: move or explicitly remove it before rebuilding: $destination" >&2
    exit 1
}
(cd "$boot" && sha256sum -c SHA256SUMS)
tar xf "$base/runtime.tar" -C "$root" \
    --exclude=plumos/backup --exclude=plumos/backups --exclude=plumos/Logs
mkdir -p "$root/plumos/Logs"
test -x "$root/plumos/bin/plumos-controller-ui"
# The snapshot is already provisioned. Never run partitioning on this clone.
test -f "$root/plumos/provision/complete"
if [ -f "$root/plumos/provision/seed-v1" ]; then
    unlink "$root/plumos/provision/seed-v1"
fi
cp /workspace/output/rg280v-fe/plumos-controller-ui \
    /workspace/output/rg280v-fe/plumos-rg280v-power-menu "$root/plumos/bin/"
cp /workspace/assets/frontend/bin/plumos-fe-launch \
    /workspace/assets/frontend/bin/plumos-jz47xx-device-env "$root/plumos/bin/"
cp /workspace/assets/frontend/S94hotkeys "$root/local/init.d/"
# This helper scales the existing artwork to the detected framebuffer.
/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-gcc \
    -Os -Wall -Wextra /workspace/tools/rg280v-fbshow.c -o "$root/local/bin/rg280v-fbshow"
chmod 0755 "$root/plumos/bin/plumos-fe-launch" "$root/plumos/bin/plumos-jz47xx-device-env"

boot_start=8192
boot_sectors=262144
data_start=$((boot_start + boot_sectors))
data_sectors=3145728
user_start=$((data_start + data_sectors))
user_sectors=131072
truncate -s $((boot_sectors * 512)) "$stage/boot.vfat"
mkfs.vfat -F32 -n PLUMOSBOOT "$stage/boot.vfat" >/dev/null
mmd -i "$stage/boot.vfat" ::/dev ::/root ::/models
mcopy -i "$stage/boot.vfat" "$boot/uzImage-$model.bin" ::/uzImage.bin
for other in rg300x rg350 rg280v rg350m; do
    mcopy -i "$stage/boot.vfat" "$boot/uzImage-$other.bin" "::/models/$other.bin"
done
for other in rg300x rg350 rg280v rg350m; do
    printf '%s  %s.bin\n' "$(sha256sum "$boot/uzImage-$other.bin" | cut -d ' ' -f1)" "$other"
done >"$stage/SHA256SUMS"
mcopy -i "$stage/boot.vfat" "$stage/SHA256SUMS" ::/models/SHA256SUMS
printf '%s\n' "$model" >"$stage/model.txt"
mcopy -i "$stage/boot.vfat" "$stage/model.txt" ::/model.txt
for name in rootfs.squashfs modules.squashfs mininit-syspart; do
    mcopy -i "$stage/boot.vfat" "$boot/$name" ::/
done
truncate -s $((data_sectors * 512)) "$stage/data.ext4"
mkfs.ext4 -F -q -L PLUMOSDATA -d "$root" "$stage/data.ext4"
truncate -s $((user_sectors * 512)) "$stage/user.vfat"
mkfs.vfat -F32 -n PLUMOS "$stage/user.vfat" >/dev/null
touch "$stage/empty/.plumos-ready"
mcopy -i "$stage/user.vfat" "$stage/empty/.plumos-ready" ::/
truncate -s $(((user_start + user_sectors) * 512)) "$destination"
printf 'label: dos\nunit: sectors\n\nstart=%s,size=%s,type=b\nstart=%s,size=%s,type=83\nstart=%s,size=%s,type=b\n' \
    "$boot_start" "$boot_sectors" "$data_start" "$data_sectors" "$user_start" "$user_sectors" |
    sfdisk --quiet --wipe always "$destination"
dd if="$boot/ubiboot-rg350.bin" of="$destination" bs=512 seek=1 conv=notrunc status=none
for part in "boot.vfat:$boot_start" "data.ext4:$data_start" "user.vfat:$user_start"; do
    dd if="$stage/${part%:*}" of="$destination" bs=4M seek="$(( ${part#*:} / 8192 ))" conv=notrunc status=none
done
mcopy -i "$destination@@$((boot_start * 512))" ::/uzImage.bin - | cmp - "$boot/uzImage-$model.bin"
e2fsck -fn "$stage/data.ext4"
(cd "$base" && sha256sum "$(basename "$destination")" >"$(basename "$destination").sha256")
sfdisk --dump "$destination"
