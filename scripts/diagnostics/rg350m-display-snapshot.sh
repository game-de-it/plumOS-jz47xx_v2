#!/bin/sh
# Temporary SD1 diagnostic. Called by rcS on the RG350M validation image.
set -eu

phase=${1:?missing boot phase}
tr '\000' '\n' </sys/firmware/devicetree/base/compatible |
    grep -qx 'ylm,rg350m' || exit 0
awk '$2 == "/media/user" && $3 == "vfat" && $4 ~ /^rw(,|$)/ { found = 1 }
    END { exit !found }' /proc/mounts || exit 0

boot_id=$(cat /proc/sys/kernel/random/boot_id)
directory=/media/user/rg350m-display-diagnostics
mkdir -p "$directory"
report="$directory/$boot_id-$phase.txt"

show() {
    [ -r "$1" ] || return 0
    printf '\n--- %s ---\n' "$1"
    cat "$1" || true
}

{
    printf 'Phase: %s\nBoot ID: %s\n' "$phase" "$boot_id"
    show /proc/uptime
    printf '\nDevice tree model: '
    tr -d '\000' </sys/firmware/devicetree/base/model
    printf '\n'
    show /proc/cmdline
    show /proc/fb
    ls -l /dev/dri /dev/fb* 2>&1 || true

    for device in /sys/class/drm/card* /sys/class/graphics/fb* /sys/class/backlight/*; do
        [ -d "$device" ] || continue
        printf '\n=== %s ===\n' "$device"
        for attribute in status enabled dpms modes name mode virtual_size bits_per_pixel \
            stride blank brightness actual_brightness max_brightness bl_power type; do
            show "$device/$attribute"
        done
    done
    if [ ! -d /sys/kernel/debug/dri ]; then
        mount -t debugfs -o ro debugfs /sys/kernel/debug 2>/dev/null || true
    fi
    for device in /sys/kernel/debug/dri/*; do
        [ -d "$device" ] || continue
        show "$device/name"
        show "$device/state"
        show "$device/clients"
    done

    printf '\n=== USB ===\n'
    for udc in /sys/class/udc/*; do
        show "$udc/state"
        show "$udc/current_speed"
    done
    show /sys/class/net/usb0/operstate
    show /sys/class/net/usb0/carrier
    show /var/log/plumos-usb.log

    printf '\n=== Frontend ===\n'
    if [ -r /var/run/plumos-fe.pid ]; then
        pid=$(cat /var/run/plumos-fe.pid)
        printf 'FE PID: %s\n' "$pid"
        show "/proc/$pid/status"
        readlink "/proc/$pid/exe" || true
    fi
    show /var/log/plumos-local.log
    if [ -r /media/data/plumos/Logs/frontend.log ]; then
        printf '\n--- frontend.log (last 120 lines) ---\n'
        tail -n 120 /media/data/plumos/Logs/frontend.log
    fi

    printf '\n=== Kernel log ===\n'
    dmesg || true
} >"$report.tmp" 2>&1
mv "$report.tmp" "$report"
sync
