#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-status"
"$repo_root/scripts/build-rg280v-status.sh"

adb connect 10.1.1.2:5555
adb -s 10.1.1.2:5555 shell \
    'mkdir -p /media/data/local/bin /media/data/local/share'
adb -s 10.1.1.2:5555 push "$out/rg280v-fbshow" /media/data/local/bin/rg280v-fbshow
adb -s 10.1.1.2:5555 push "$out/boot-logo.ppm" /media/data/local/share/boot-logo.ppm
adb -s 10.1.1.2:5555 shell \
    'chmod 0755 /media/data/local/bin/rg280v-fbshow; rm -f /media/data/local/init.d/S90status /media/data/local/share/adb-ready.ppm'
