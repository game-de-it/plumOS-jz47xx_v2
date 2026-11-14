#!/usr/bin/env bash
set -euo pipefail

source_dir=/workspace/output/rg280v/images
stage=/workspace/output/rg280v/image-stage
destination=/workspace/output/plumos-rg280v-firstboot-seed.img
boot_start=8192
boot_sectors=1048576
data_start=$((boot_start + boot_sectors))
data_sectors=2097152
total_sectors=$((data_start + data_sectors))

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
rm -rf "$data_root"
mkdir -p "$data_root/local/bin" "$data_root/local/share" "$data_root/local/init.d" \
    "$data_root/plumos/provision" "$data_root/plumos/bin" \
    "$data_root/plumos/fonts" "$data_root/plumos/licenses" \
    "$data_root/plumos/themes/default/logos/systems" \
    "$data_root/plumos/themes/default/images" "$data_root/plumos/config/frontend" \
    "$data_root/plumos/config/system" "$data_root/plumos/state/frontend" \
    "$data_root/plumos/Logs" "$data_root/plumos/emulators" \
    "$data_root/plumos/lib" "$data_root/plumos/home"
printf 'RG280V first-boot seed v1\n' > "$data_root/plumos/provision/seed-v1"
cp /workspace/output/rg280v-status/rg280v-fbshow "$data_root/local/bin/rg280v-fbshow"
cp /workspace/output/rg280v-status/adb-ready.ppm "$data_root/local/share/adb-ready.ppm"
cp /workspace/output/rg280v-status/first-boot.ppm "$data_root/local/share/first-boot.ppm"
cp /workspace/output/rg280v-status/first-boot-error.ppm "$data_root/local/share/first-boot-error.ppm"
cp /workspace/board/rg280v/adb/S90status "$data_root/local/init.d/S90status"
cp /workspace/assets/frontend/S95frontend "$data_root/local/init.d/S95frontend"
cp /workspace/output/rg280v-fe/plumos-controller-ui /workspace/output/rg280v-fe/plumos-library-scan \
    /workspace/output/rg280v-fe/plumos-text-ui "$data_root/plumos/bin/"
cp /workspace/assets/frontend/bin/* "$data_root/plumos/bin/"
cp /workspace/board/rg280v/overlay/etc/udev/rules.d/70-plumos-gpio-keys.rules \
    "$data_root/plumos/config/70-plumos-gpio-keys.rules"
cp /workspace/assets/frontend/default.otf /workspace/assets/frontend/cjk-fallback.ttc "$data_root/plumos/fonts/"
cp /workspace/assets/frontend/licenses/* "$data_root/plumos/licenses/"
cp /workspace/output/rg280v-emulators/libpng14-build/libpng-1.4.22/LICENSE \
    "$data_root/plumos/licenses/libpng14-LICENSE"
cp /workspace/output/rg280v-emulators/lib/* "$data_root/plumos/lib/"
for name in fceux_gcw0-2.6.6-2023-08-30.opk gambatte-dms-multi-r572u4-20211021.opk \
    PocketSNES_2019-12-12.opk ReGBA_1.9.2_rg280v.opk GenesisPlusGX_2019-12-23.opk; do
    cp "/workspace/output/rg280v-emulators/$name" "$data_root/plumos/emulators/$name"
done
cp /workspace/assets/frontend/theme.json "$data_root/plumos/themes/default/"
cp /workspace/assets/frontend/logos/systems/*.png "$data_root/plumos/themes/default/logos/systems/"
cp /workspace/assets/frontend/images/*.png "$data_root/plumos/themes/default/images/"
cp /workspace/assets/frontend/systems.json /workspace/assets/frontend/menus.json \
    /workspace/assets/frontend/apps.json /workspace/assets/frontend/settings.json \
    "$data_root/plumos/config/frontend/"
cp /workspace/assets/frontend/system-settings.json "$data_root/plumos/config/system/settings.json"
cp /workspace/assets/frontend/regba-global-config.cfg "$data_root/plumos/config/"
cp /workspace/assets/frontend/VERSION "$data_root/plumos/VERSION"
chmod 0755 "$data_root/local/bin/rg280v-fbshow" "$data_root/local/init.d/S90status" \
    "$data_root/local/init.d/S95frontend" "$data_root/plumos/bin/"*
truncate -s 0 "$stage/data.ext4"
truncate -s $((data_sectors * 512)) "$stage/data.ext4"
mkfs.ext4 -F -q -d "$data_root" -L PLUMOSDATA "$stage/data.ext4"
for path in /local/bin/rg280v-fbshow /local/share/adb-ready.ppm \
            /local/share/first-boot.ppm /local/share/first-boot-error.ppm \
            /local/init.d/S90status /local/init.d/S95frontend \
            /plumos/bin/plumos-controller-ui /plumos/bin/plumos-library-scan \
            /plumos/bin/plumos-text-ui /plumos/bin/plumos-standalone-launch \
            /plumos/bin/plumos-prepare-opk-input \
            /plumos/bin/plumos-fceux-prepare \
            /plumos/config/70-plumos-gpio-keys.rules \
            /plumos/emulators/fceux_gcw0-2.6.6-2023-08-30.opk \
            /plumos/emulators/gambatte-dms-multi-r572u4-20211021.opk \
            /plumos/emulators/PocketSNES_2019-12-12.opk \
            /plumos/emulators/ReGBA_1.9.2_rg280v.opk \
            /plumos/lib/libregba-doublebuf.so \
            /plumos/lib/libfceux-menu.so \
            /plumos/lib/libgambatte-menu.so \
            /plumos/emulators/GenesisPlusGX_2019-12-23.opk \
            /plumos/config/frontend/menus.json /plumos/config/frontend/systems.json \
            /plumos/provision/seed-v1; do
    debugfs -R "stat $path" "$stage/data.ext4" 2>/dev/null | grep -q 'Inode:' || {
        echo "Missing data file in ext4: $path" >&2
        exit 1
    }
done

truncate -s 0 "$destination"
truncate -s $((total_sectors * 512)) "$destination"
printf 'label: dos\nunit: sectors\n\nstart=%s, size=%s, type=b\nstart=%s, size=%s, type=83\n' \
    "$boot_start" "$boot_sectors" "$data_start" "$data_sectors" | \
    sfdisk --quiet --wipe always "$destination"

dd if="$source_dir/ubiboot-rg350.bin" of="$destination" \
    bs=512 seek=1 count=16 conv=notrunc status=none
dd if="$stage/boot.vfat" of="$destination" \
    bs=512 seek="$boot_start" conv=notrunc status=none
dd if="$stage/data.ext4" of="$destination" \
    bs=512 seek="$data_start" conv=notrunc status=none

cmp -s -n $((boot_sectors * 512)) \
    -i 0:$((boot_start * 512)) "$stage/boot.vfat" "$destination"
cmp -s -n $((data_sectors * 512)) \
    -i 0:$((data_start * 512)) "$stage/data.ext4" "$destination"
cmp -s -n "$(stat -c '%s' "$source_dir/ubiboot-rg350.bin")" \
    -i 0:512 "$source_dir/ubiboot-rg350.bin" "$destination"
mdir -i "$destination@@$((boot_start * 512))" ::/dev ::/root >/dev/null

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
