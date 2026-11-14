#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -f "$1" || "$1" != *.opk ]]; then
    echo 'Usage: deploy-rg280v-opk.sh path/to/app.opk' >&2
    exit 2
fi

port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
adb -P "$port" connect "$serial" >/dev/null
adb -P "$port" -s "$serial" get-state >/dev/null
adb -P "$port" -s "$serial" shell mkdir -p /media/data/apps
adb -P "$port" -s "$serial" push "$1" "/media/data/apps/$(basename "$1")"
printf 'Deployed %s to /media/data/apps\n' "$(basename "$1")"
