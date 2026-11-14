#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -f "$1" || "$1" != *.opk ]]; then
    echo 'Usage: deploy-rg280v-opk.sh path/to/app.opk' >&2
    exit 2
fi

serial=10.1.1.2:5555
adb connect "$serial" >/dev/null
adb -s "$serial" get-state >/dev/null
adb -s "$serial" shell mkdir -p /media/data/apps
adb -s "$serial" push "$1" "/media/data/apps/$(basename "$1")"
printf 'Deployed %s to /media/data/apps\n' "$(basename "$1")"
