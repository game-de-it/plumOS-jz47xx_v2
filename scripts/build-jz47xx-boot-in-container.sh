#!/usr/bin/env bash
# Run in the existing SDK container. Produces files only, never writes a card.
set -euo pipefail
sdk=/workspace/output/rg280v
kernel="$sdk/build/linux-custom"
out=/workspace/output/jz47xx-multimodel/boot
reference=/workspace/output/jz47xx-multimodel/reference-boot
mkdir -p "$out"
patch_file=/workspace/patches/jz47xx-rg350m-i2c-gpio.patch
if ! git -C "$kernel" apply --reverse --check "$patch_file" 2>/dev/null; then
    git -C "$kernel" apply "$patch_file"
fi
make -C "$kernel" ARCH=mips CROSS_COMPILE="$sdk/host/bin/mipsel-gcw0-linux-uclibc-" \
    -j "${JOBS:-8}" ingenic/rg280v.dtb ingenic/rg300x.dtb ingenic/rg350.dtb ingenic/rg350m.dtb
cp "$sdk/images/uzImage.bin" "$out/kernel.bin"
cp "$sdk/images/ubiboot-rg350.bin" "$out/ubiboot-rg350.bin"
test "$(stat -c %s "$out/ubiboot-rg350.bin")" -le 8192
for model in rg280v rg300x rg350 rg350m; do
    cp "$kernel/arch/mips/boot/dts/ingenic/$model.dtb" "$out/$model.dtb"
    "$sdk/host/bin/fdtget" "$out/$model.dtb" / compatible | grep -qw "ylm,$model"
    cat "$out/kernel.bin" "$out/$model.dtb" >"$out/uzImage-$model.bin"
done
# Use the already validated rootfs/modules as a pair, rather than silently
# picking up SDK modules changed by subsequent frontend package builds.
for name in rootfs.squashfs modules.squashfs mininit-syspart; do
    cp "$reference/$name" "$out/$name"
done
(cd "$out" && sha256sum kernel.bin ubiboot-rg350.bin *.dtb uzImage-*.bin \
    rootfs.squashfs modules.squashfs mininit-syspart >SHA256SUMS)
