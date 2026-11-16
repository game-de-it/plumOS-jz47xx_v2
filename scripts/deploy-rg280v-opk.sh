#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -f "$1" || "$1" != *.opk ]]; then
    echo 'Usage: deploy-rg280v-opk.sh path/to/app.opk' >&2
    exit 2
fi

name=$(basename "$1")
if [[ ! "$name" =~ ^[A-Za-z0-9][A-Za-z0-9_.-]*\.opk$ || "$name" == *..* || ${#name} -gt 96 ]]; then
    echo "Invalid OPK filename: $name" >&2
    exit 2
fi
expected=$(shasum -a 256 "$1" | awk '{print $1}')
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
adb -P "$port" connect "$serial" >/dev/null
adb -P "$port" -s "$serial" get-state >/dev/null
adb -P "$port" -s "$serial" shell mkdir -p /media/data/apps
adb -P "$port" -s "$serial" push "$1" "/media/data/apps/$name.new" >/dev/null
actual=$(adb -P "$port" -s "$serial" shell "sha256sum /media/data/apps/$name.new" | awk '{print $1}')
[[ "$actual" == "$expected" ]] || { echo "OPK transfer hash mismatch: $name" >&2; exit 1; }
adb -P "$port" -s "$serial" shell "mv /media/data/apps/$name.new /media/data/apps/$name"
printf 'Deployed %s to /media/data/apps (SHA-256 %s)\n' "$name" "$expected"
