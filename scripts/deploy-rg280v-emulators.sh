#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
adb=(adb -P "$port" -s "$serial")
remote=/media/data/plumos
local_emulators="$repo_root/output/rg280v-emulators"

"$repo_root/scripts/fetch-rg280v-emulators.sh"
"$repo_root/scripts/repack-rg280v-regba.sh"
if [[ ! -f "$local_emulators/lib/libvorbisfile.so.3" ]]; then
    "$repo_root/scripts/build-rg280v-emulator-libs.sh"
fi
"$repo_root/scripts/build-rg280v-fe.sh"

adb -P "$port" connect "$serial" >/dev/null
"${adb[@]}" get-state >/dev/null
"${adb[@]}" shell "mkdir -p $remote/emulators $remote/lib $remote/bin $remote/config/frontend"

copy_checked() {
    local source=$1 destination=$2 mode=$3 expected actual
    expected=$(shasum -a 256 "$source" | awk '{print $1}')
    "${adb[@]}" push "$source" "$destination.new" >/dev/null
    actual=$("${adb[@]}" shell "sha256sum $destination.new" | awk '{print $1}')
    [[ "$actual" == "$expected" ]] || { echo "hash mismatch: $destination" >&2; exit 1; }
    "${adb[@]}" shell "mv $destination.new $destination && chmod $mode $destination"
    echo "$expected  $destination"
}

copy_checked "$repo_root/output/rg280v-fe/plumos-text-ui" "$remote/bin/plumos-text-ui" 0755
copy_checked "$repo_root/assets/frontend/bin/plumos-prepare-opk-input" "$remote/bin/plumos-prepare-opk-input" 0755
copy_checked "$repo_root/assets/frontend/bin/plumos-standalone-launch" "$remote/bin/plumos-standalone-launch" 0755
copy_checked "$repo_root/assets/frontend/regba-global-config.cfg" "$remote/config/regba-global-config.cfg" 0644
copy_checked "$repo_root/board/rg280v/overlay/etc/udev/rules.d/70-plumos-gpio-keys.rules" \
    "$remote/config/70-plumos-gpio-keys.rules" 0644
for name in FCEUX_2019-11-15.opk gambatte-dms-multi-r572u4-20211021.opk \
    PocketSNES_2019-12-12.opk ReGBA_1.9.2_rg280v.opk GenesisPlusGX_2019-12-23.opk; do
    copy_checked "$local_emulators/$name" "$remote/emulators/$name" 0644
done
for source in "$local_emulators"/lib/*; do
    copy_checked "$source" "$remote/lib/$(basename "$source")" 0644
done

temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
if "${adb[@]}" shell "test -f $remote/config/frontend/systems.json"; then
    "${adb[@]}" pull "$remote/config/frontend/systems.json" "$temporary/installed.json" >/dev/null
    python3 "$repo_root/scripts/merge-rg280v-emulator-profiles.py" \
        "$temporary/installed.json" "$repo_root/assets/frontend/systems.json" "$temporary/merged.json"
    "${adb[@]}" shell "cp $remote/config/frontend/systems.json $remote/config/frontend/systems.json.pre-emulators"
else
    cp "$repo_root/assets/frontend/systems.json" "$temporary/merged.json"
fi
copy_checked "$temporary/merged.json" "$remote/config/frontend/systems.json" 0644
