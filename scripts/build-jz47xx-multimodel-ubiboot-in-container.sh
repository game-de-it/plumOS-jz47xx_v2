#!/usr/bin/env bash
# Build the SD1 selector separately from the stock single-model bootloader.
set -euo pipefail
sdk=/workspace/output/rg280v
out=/workspace/output/jz47xx-multimodel/boot
source_archive=/workspace/work/dl/ubiboot/ubiboot-dc54030.tar.gz
source_sha=444eca2671e0b9a890706e3fce88305526a67c75cf8fb29adcc7d56684129205
printf '%s  %s\n' "$source_sha" "$source_archive" | sha256sum -c -

# The selector runs before a DTB is loaded. Refuse to build with a model
# whose DTB does not agree with the common active-low port E wiring.
fdtget="$sdk/host/bin/fdtget"
for model in rg280v rg300x rg350 rg350m; do
    dtb="$out/$model.dtb"
    port_e=$($fdtget -t u "$dtb" /pinctrl@10010000/gpio@4 phandle)
    for spec in 0:21:103 1:25:108 2:23:105 3:24:106; do
        IFS=: read -r button pin code <<<"$spec"
        node="/gpio-keys/button-$button"
        test "$($fdtget -t u "$dtb" "$node" linux,code)" = "$code"
        test "$($fdtget -t u "$dtb" "$node" gpios)" = "$port_e $pin 1"
    done
done

stage=$(mktemp -d "$sdk/jz47xx-multimodel-ubiboot.XXXXXXXX")
trap 'rm -rf -- "$stage"' EXIT
tar -xf "$source_archive" --strip-components=1 -C "$stage"
git -C "$stage" apply /workspace/patches/jz47xx-ubiboot-multimodel.patch
artifact=output/gcw0/ubiboot-rg350.bin
make -C "$stage" CONFIG=gcw0 CROSS_COMPILE="$sdk/host/bin/mipsel-gcw0-linux-uclibc-" \
    CFLAGS_all='-mips32r2 -DPLUMOS_MULTIMODEL' "$artifact"
test -s "$stage/$artifact"
test "$(stat -c %s "$stage/$artifact")" -le 8192
install -m 0644 "$stage/$artifact" "$out/ubiboot-multimodel.bin"
