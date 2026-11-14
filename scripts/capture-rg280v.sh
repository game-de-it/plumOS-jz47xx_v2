#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
serial=10.1.1.2:5555
destination="$repo_root/output/rg280v/diagnostics/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$destination"

adb connect "$serial"
adb -s "$serial" get-state >/dev/null

adb -s "$serial" shell '
    uname -a
    cat /proc/cmdline
    cat /sys/firmware/devicetree/base/model 2>/dev/null
    cat /proc/partitions
    mount
    cat /proc/asound/cards 2>/dev/null
    cat /sys/class/udc/*/uevent 2>/dev/null
    cat /sys/kernel/debug/usb/devices 2>/dev/null
' > "$destination/system.txt"
adb -s "$serial" shell dmesg > "$destination/dmesg.txt"
adb -s "$serial" shell cat /var/log/plumos-usb.log > "$destination/usb-service.txt" 2>/dev/null || true
adb -s "$serial" shell cat /var/log/plumos-adbd.log > "$destination/adbd.txt" 2>/dev/null || true

printf 'Saved diagnostics: %s\n' "$destination"
