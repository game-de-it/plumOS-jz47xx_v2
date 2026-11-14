#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
adb=(adb -P "$port" -s "$serial")
remote=/media/data/plumos

"${adb[@]}" get-state >/dev/null
"${adb[@]}" shell "mkdir -p $remote/bin $remote/fonts $remote/themes/default/logos/systems $remote/themes/default/images $remote/config/frontend $remote/config/system $remote/state/frontend $remote/Logs $remote/licenses"

copy_checked() {
    local source=$1 destination=$2 mode=$3 expected actual
    expected=$(shasum -a 256 "$source" | awk '{print $1}')
    "${adb[@]}" push "$source" "$destination.new" >/dev/null
    actual=$("${adb[@]}" shell "sha256sum $destination.new" | awk '{print $1}')
    [[ "$actual" == "$expected" ]] || { echo "hash mismatch: $destination" >&2; exit 1; }
    "${adb[@]}" shell "mv $destination.new $destination && chmod $mode $destination"
    echo "$expected  $destination"
}

copy_if_missing() {
    local source=$1 destination=$2 state
    if [[ "${PLUMOS_FE_UPDATE_CONFIG:-0}" == 1 ]]; then
        copy_checked "$source" "$destination" 0644
        return
    fi
    state=$("${adb[@]}" shell "if test -e $destination; then echo present; else echo absent; fi" | tr -d '\r')
    if [[ "$state" == present ]]; then
        echo "preserved existing $destination"
    elif [[ "$state" == absent ]]; then
        copy_checked "$source" "$destination" 0644
    else
        echo "could not inspect $destination: $state" >&2
        exit 1
    fi
}

copy_checked "$repo_root/output/rg280v-fe/plumos-controller-ui" "$remote/bin/plumos-controller-ui" 0755
copy_checked "$repo_root/output/rg280v-fe/plumos-library-scan" "$remote/bin/plumos-library-scan" 0755
for name in plumos-fe-launch plumos-volume-control plumos-display-control plumos-safe-shutdown; do
    copy_checked "$repo_root/assets/frontend/bin/$name" "$remote/bin/$name" 0755
done
copy_checked "$repo_root/assets/frontend/default.otf" "$remote/fonts/default.otf" 0644
copy_checked "$repo_root/assets/frontend/cjk-fallback.ttc" "$remote/fonts/cjk-fallback.ttc" 0644
copy_checked "$repo_root/assets/frontend/licenses/NotoSansJP-OFL.txt" "$remote/licenses/NotoSansJP-OFL.txt" 0644
copy_checked "$repo_root/assets/frontend/licenses/WQYMicroHei-Apache-2.0.txt" "$remote/licenses/WQYMicroHei-Apache-2.0.txt" 0644
copy_checked "$repo_root/assets/frontend/theme.json" "$remote/themes/default/theme.json" 0644
for source in "$repo_root"/assets/frontend/logos/systems/*.png; do
    copy_checked "$source" "$remote/themes/default/logos/systems/$(basename "$source")" 0644
done
copy_checked "$repo_root/assets/frontend/images/rom_gallery_background.png" \
    "$remote/themes/default/images/rom_gallery_background.png" 0644
copy_checked "$repo_root/assets/frontend/VERSION" "$remote/VERSION" 0644
copy_if_missing "$repo_root/assets/frontend/systems.json" "$remote/config/frontend/systems.json"
copy_if_missing "$repo_root/assets/frontend/menus.json" "$remote/config/frontend/menus.json"
copy_if_missing "$repo_root/assets/frontend/apps.json" "$remote/config/frontend/apps.json"
copy_if_missing "$repo_root/assets/frontend/settings.json" "$remote/config/frontend/settings.json"
copy_if_missing "$repo_root/assets/frontend/system-settings.json" "$remote/config/system/settings.json"
if [[ "${PLUMOS_FE_INSTALL_SERVICE:-0}" == 1 ]]; then
    copy_checked "$repo_root/board/rg280v/adb/S90status" \
        /media/data/local/init.d/S90status 0755
    copy_checked "$repo_root/assets/frontend/S95frontend" \
        /media/data/local/init.d/S95frontend 0755
fi
