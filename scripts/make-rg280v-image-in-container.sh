#!/usr/bin/env bash
set -euo pipefail

source_dir=/workspace/output/rg280v/images
stage=/workspace/output/rg280v/image-stage
destination=/workspace/output/plumos-rg280v-adb-bringup.img
boot_start=8192
boot_sectors=1048576
data_start=$((boot_start + boot_sectors))
data_sectors=2097152
user_start=$((data_start + data_sectors))
user_sectors=1048576
total_sectors=$((user_start + user_sectors))

mkdir -p "$stage"
if [[ $(stat -c '%s' "$source_dir/ubiboot-rg350.bin") -gt 8192 ]]; then
    echo 'UBIBoot exceeds the reserved 16 sectors' >&2
    exit 1
fi
truncate -s 0 "$stage/boot.vfat"
truncate -s $((boot_sectors * 512)) "$stage/boot.vfat"
mkfs.vfat -F 32 -n PLUMOSBOOT "$stage/boot.vfat" >/dev/null
mmd -i "$stage/boot.vfat" ::/dev ::/root

cat "$source_dir/uzImage.bin" "$source_dir/rg280v.dtb" > "$stage/uzImage.bin"
for name in uzImage.bin rootfs.squashfs modules.squashfs mininit-syspart; do
    if [[ "$name" == uzImage.bin ]]; then
        input="$stage/$name"
    else
        input="$source_dir/$name"
    fi
    mcopy -o -i "$stage/boot.vfat" "$input" ::/
done
mdir -i "$stage/boot.vfat" ::/dev ::/root >/dev/null

data_root="$stage/data-root"
mkdir -p "$data_root/local/bin" "$data_root/local/share" "$data_root/local/init.d"
cp /workspace/output/rg280v-status/rg280v-fbshow "$data_root/local/bin/rg280v-fbshow"
cp /workspace/output/rg280v-status/adb-ready.ppm "$data_root/local/share/adb-ready.ppm"
cp /workspace/board/rg280v/adb/S90status "$data_root/local/init.d/S90status"
chmod 0755 "$data_root/local/bin/rg280v-fbshow" "$data_root/local/init.d/S90status"
truncate -s 0 "$stage/data.ext4"
truncate -s $((data_sectors * 512)) "$stage/data.ext4"
mkfs.ext4 -F -q -d "$data_root" -L PLUMOSDATA "$stage/data.ext4"
for path in /local/bin/rg280v-fbshow /local/share/adb-ready.ppm /local/init.d/S90status; do
    debugfs -R "stat $path" "$stage/data.ext4" 2>/dev/null | grep -q 'Inode:' || {
        echo "Missing data file in ext4: $path" >&2
        exit 1
    }
done

truncate -s 0 "$stage/user.vfat"
truncate -s $((user_sectors * 512)) "$stage/user.vfat"
mkfs.vfat -F 32 -n PLUMOS "$stage/user.vfat" >/dev/null
mmd -i "$stage/user.vfat" ::/roms ::/bios ::/apps ::/updates
mdir -i "$stage/user.vfat" ::/roms ::/bios ::/apps ::/updates >/dev/null

truncate -s 0 "$destination"
truncate -s $((total_sectors * 512)) "$destination"
printf 'label: dos\nunit: sectors\n\nstart=%s, size=%s, type=b\nstart=%s, size=%s, type=83\nstart=%s, size=%s, type=b\n' \
    "$boot_start" "$boot_sectors" "$data_start" "$data_sectors" \
    "$user_start" "$user_sectors" | \
    sfdisk --quiet --wipe always "$destination"

dd if="$source_dir/ubiboot-rg350.bin" of="$destination" \
    bs=512 seek=1 count=16 conv=notrunc status=none
dd if="$stage/boot.vfat" of="$destination" \
    bs=512 seek="$boot_start" conv=notrunc status=none
dd if="$stage/data.ext4" of="$destination" \
    bs=512 seek="$data_start" conv=notrunc status=none
dd if="$stage/user.vfat" of="$destination" \
    bs=512 seek="$user_start" conv=notrunc status=none

cmp -s -n $((boot_sectors * 512)) \
    -i 0:$((boot_start * 512)) "$stage/boot.vfat" "$destination"
cmp -s -n $((data_sectors * 512)) \
    -i 0:$((data_start * 512)) "$stage/data.ext4" "$destination"
cmp -s -n $((user_sectors * 512)) \
    -i 0:$((user_start * 512)) "$stage/user.vfat" "$destination"
cmp -s -n "$(stat -c '%s' "$source_dir/ubiboot-rg350.bin")" \
    -i 0:512 "$source_dir/ubiboot-rg350.bin" "$destination"
mdir -i "$destination@@$((boot_start * 512))" ::/dev ::/root >/dev/null
mdir -i "$destination@@$((user_start * 512))" ::/roms ::/bios ::/apps ::/updates >/dev/null

for name in uzImage.bin rootfs.squashfs modules.squashfs mininit-syspart; do
    if [[ "$name" == uzImage.bin ]]; then
        expected="$stage/$name"
    else
        expected="$source_dir/$name"
    fi
    mcopy -i "$stage/boot.vfat" "::/$name" - | cmp - "$expected"
done

(
    cd "$(dirname "$destination")"
    sha256sum "$(basename "$destination")" > "$(basename "$destination").sha256"
)
sfdisk --dump "$destination"
cat "$destination.sha256"
