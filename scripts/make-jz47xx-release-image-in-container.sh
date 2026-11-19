#!/usr/bin/env bash
# Build from a factory allowlist in the SDK container. No live card is accessed.
set -euo pipefail
cd /workspace
version=${1:?usage: make-jz47xx-release-image-in-container.sh VERSION}
version=${version#v}
[[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z][0-9A-Za-z.-]*)?$ ]]
out=output/release
name="plumOS-JZ47xx-$version.img"
mkdir -p "$out"
test ! -e "$out/$name"
sdk=output/rg280v
export PATH="$PWD/$sdk/host/bin:$PATH"
boot=output/jz47xx-multimodel/boot
stage=$(mktemp -d "$sdk/jz47xx-release.XXXXXXXX")
trap 'rm -rf -- "$stage"' EXIT
cc="$sdk/host/bin/mipsel-gcw0-linux-uclibc-gcc"

(cd "$boot" && sha256sum -c SHA256SUMS)
bash scripts/build-jz47xx-multimodel-ubiboot-in-container.sh

root="$stage/data"
mkdir -p "$root/local/bin"
python3 scripts/stage-jz47xx-release.py "$root" --stage "$stage"
printf '%s\n' "$version" > "$root/plumos/VERSION"
install -Dm0644 LICENSE "$root/plumos/licenses/plumOS-MIT.txt"
"$cc" -Os -Wall -Wextra -Werror tools/plumos-resize-user-partition.c \
    -o "$root/local/bin/plumos-resize-user-partition"
"$cc" -Os -Wall -Wextra tools/rg280v-fbshow.c -o "$root/local/bin/rg280v-fbshow"
install -Dm0644 output/rg280v-status/boot-logo.ppm "$root/local/share/boot-logo.ppm"

# Lock inherited system accounts and remove development-only daemon/shell
# entry points before repacking the inspected system filesystem.
unsquashfs -no-progress -d "$stage/system" "$boot/rootfs.squashfs"
rm -f "$stage/system/usr/bin/adbd" "$stage/system/usr/sbin/dropbear" \
    "$stage/system/usr/sbin/plumos-usb-ecm" "$stage/system/etc/udhcpd.conf" \
    "$stage/system/usr/share/gmenu2x/.gitignore"
sed -i '/^tty1::respawn:\/bin\/sh$/d' "$stage/system/etc/inittab"
for shadow in "$stage/system/etc/shadow" "$stage/system/media/data/local/etc/shadow"; do
    if [ -f "$shadow" ] && [ ! -L "$shadow" ]; then
        sed -i -E 's/^([^:]+):[^:]*:/\1:!:/' "$shadow"
    fi
done
install -Dm0600 "$stage/system/media/data/local/etc/shadow" "$root/local/etc/shadow"
# Remove the development USB setup and its late diagnostic worker.
python3 - "$stage/system/etc/init.d/rcS" <<'PY'
import sys
from pathlib import Path
rcs = Path(sys.argv[1])
source = rcs.read_text()
start = source.index('if [ -x /usr/sbin/plumos-usb-ecm ]; then\n')
end = source.index('if [ -n "$data_device" ] && [ -f /media/data/plumos/provision/seed-v1 ]', start)
tail = source.index('\n(\n    sleep 10\n    log "USB_LATE_OPERSTATE=')
rcs.write_text(source[:start] + source[end:tail])
PY
find "$stage/system" -type f -name '*.png' -print0 > "$stage/system-pngs"
python3 - "$stage/system-pngs" <<'PY'
import runpy
import sys
from pathlib import Path
sanitize_png = runpy.run_path("scripts/stage-jz47xx-release.py")["sanitize_png"]
for entry in Path(sys.argv[1]).read_bytes().split(b"\0"):
    if entry:
        sanitize_png(Path(entry.decode()))
PY
python3 scripts/stage-jz47xx-release.py "$stage/system"
python3 scripts/stage-jz47xx-release.py "$root"
mksquashfs "$stage/system" "$stage/rootfs.squashfs" \
    -noappend -no-xattrs -comp zstd -processors 2 -no-progress
unsquashfs -no-progress -d "$stage/modules" "$boot/modules.squashfs" >/dev/null
python3 scripts/stage-jz47xx-release.py "$stage/modules"

boot_start=8192
boot_size=262144
data_start=270336
data_size=3145728
user_start=3416064
user_size=131072
truncate -s $((boot_size * 512)) "$stage/boot.vfat"
mkfs.vfat -F32 -n PLUMOSBOOT "$stage/boot.vfat" >/dev/null
mmd -i "$stage/boot.vfat" ::/dev ::/root
for model in rg280v rg300x rg350 rg350m; do
    mcopy -i "$stage/boot.vfat" "$boot/uzImage-$model.bin" "::/${model^^}.BIN"
done
printf 'multimodel\n' > "$stage/model.txt"
mcopy -i "$stage/boot.vfat" "$stage/model.txt" "$stage/rootfs.squashfs" \
    "$boot/modules.squashfs" "$boot/mininit-syspart" ::/
truncate -s $((data_size * 512)) "$stage/data.ext4"
mkfs.ext4 -Fq -d "$root" -L PLUMOSDATA "$stage/data.ext4"
e2fsck -fn "$stage/data.ext4"
fsck.fat -n "$stage/boot.vfat"

image="$stage/$name"
truncate -s $(((user_start + user_size) * 512)) "$image"
printf 'label: dos\nunit: sectors\n\nstart=%s,size=%s,type=b\nstart=%s,size=%s,type=83\nstart=%s,size=%s,type=b\n' \
    "$boot_start" "$boot_size" "$data_start" "$data_size" "$user_start" "$user_size" |
    sfdisk --quiet --wipe never "$image"
dd if="$boot/ubiboot-multimodel.bin" of="$image" bs=512 seek=1 conv=notrunc status=none
dd if="$stage/boot.vfat" of="$image" bs=4M seek=$((boot_start / 8192)) conv=sparse,notrunc status=none
dd if="$stage/data.ext4" of="$image" bs=4M seek=$((data_start / 8192)) conv=sparse,notrunc status=none

fat="$image@@$((boot_start * 512))"
dd if="$image" iflag=skip_bytes,count_bytes skip=512 \
    count="$(stat -c %s "$boot/ubiboot-multimodel.bin")" status=none |
    cmp - "$boot/ubiboot-multimodel.bin"
for model in rg280v rg300x rg350 rg350m; do
    mcopy -i "$fat" "::/${model^^}.BIN" - | cmp - "$boot/uzImage-$model.bin"
done
for actual in "$stage/rootfs.squashfs" "$boot/modules.squashfs" "$boot/mininit-syspart"; do
    mcopy -i "$fat" "::/${actual##*/}" - | cmp - "$actual"
done
! mdir -i "$fat" ::/BOOTMOD.CFG >/dev/null 2>&1
dd if="$image" bs=4M skip=$((data_start / 8192)) count=$((data_size / 8192)) status=none |
    cmp - "$stage/data.ext4"
dd if="$image" bs=4M skip=$((user_start / 8192)) count=$((user_size / 8192)) status=none |
    cmp -n $((user_size * 512)) - /dev/zero
sfdisk --verify "$image"
sfdisk --dump "$image"
cp --sparse=always "$image" "$out/$name"
(cd "$out" && sha256sum "$name" > "$name.sha256")
