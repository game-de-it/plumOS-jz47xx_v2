#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
remote=/media/data/plumos
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
adb=(adb -P "$port" -s "$serial")
"${adb[@]}" get-state >/dev/null
test -s "$out/pcsx4all_rg280v"

copy_checked() {
    local source=$1 destination=$2 mode=$3 expected actual
    expected=$(shasum -a 256 "$source" | awk '{print $1}')
    "${adb[@]}" push "$source" "$destination.new" </dev/null >/dev/null
    actual=$("${adb[@]}" shell "sha256sum $destination.new" </dev/null | awk '{print $1}')
    [[ "$actual" == "$expected" ]] || {
        echo "hash mismatch: $destination" >&2
        exit 1
    }
    "${adb[@]}" shell "mv $destination.new $destination && chmod $mode $destination" </dev/null
    echo "$expected  $destination"
}

"${adb[@]}" shell "mkdir -p $remote/bin $remote/home/.pcsx4all $remote/config/frontend"
copy_checked "$out/pcsx4all_rg280v" "$remote/bin/pcsx4all" 0755
copy_checked "$repo_root/assets/frontend/bin/plumos-standalone-launch" \
    "$remote/bin/plumos-standalone-launch" 0755
"${adb[@]}" shell "if [ ! -e $remote/home/.pcsx4all/bios ]; then ln -s $remote/bios $remote/home/.pcsx4all/bios; fi"

"${adb[@]}" pull "$remote/config/frontend/systems.json" "$out/pcsx4all-systems-before.json" >/dev/null
python3 "$repo_root/scripts/merge-rg280v-pcsx4all-profile.py" \
    "$out/pcsx4all-systems-before.json" "$repo_root/assets/frontend/systems.json" \
    "$out/pcsx4all-systems-updated.json"
copy_checked "$out/pcsx4all-systems-updated.json" "$remote/config/frontend/systems.json" 0644

config="$remote/home/.pcsx4all/pcsx4all_ng.cfg"
if "${adb[@]}" shell "test -f $config" >/dev/null 2>&1; then
    "${adb[@]}" pull "$config" "$out/pcsx4all-config-before.cfg" >/dev/null
    python3 - "$out/pcsx4all-config-before.cfg" "$out/pcsx4all-config-updated.cfg" <<'PY'
from pathlib import Path
import re
import sys

source, target = map(Path, sys.argv[1:])
text = source.read_text()
if re.search(r"(?m)^MenuToggleCombo [0-9]+$", text):
    text = re.sub(r"(?m)^MenuToggleCombo [0-9]+$", "MenuToggleCombo 1", text)
else:
    text += "\nMenuToggleCombo 1\n"
if re.search(r"(?m)^Analog_Mode [0-9]+$", text):
    text = re.sub(r"(?m)^Analog_Mode [0-9]+$", "Analog_Mode 0", text)
else:
    text = text.rstrip("\n") + "\nAnalog_Mode 0\n"
target.write_text(text)
PY
    copy_checked "$out/pcsx4all-config-updated.cfg" "$config" 0644
fi

if [[ ${PLUMOS_PCSX4ALL_RESTART_FE:-1} == 1 ]]; then
    "${adb[@]}" shell "/media/data/local/init.d/S95frontend stop; /media/data/local/init.d/S95frontend start; sleep 6; ps | grep '[p]lumos-controller-ui'"
fi
