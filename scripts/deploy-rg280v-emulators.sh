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
"$repo_root/scripts/repack-rg280v-gambatte.sh"
"$repo_root/scripts/build-rg280v-picodrive.sh"
"$repo_root/scripts/build-rg280v-picoarch.sh"
PLUMOS_PICOARCH_RECIPES="$repo_root/scripts/rg280v-picoarch-extra-cores.tsv" \
    PLUMOS_PICOARCH_CORE_FILTER=mednafen_wswan \
    "$repo_root/scripts/build-rg280v-picoarch-cores.sh"
"$repo_root/scripts/build-rg280v-fceux-menu.sh"
"$repo_root/scripts/build-rg280v-gambatte-menu.sh"
if [[ ! -f "$local_emulators/lib/libSDL_image-1.2.so.0" ||
      ! -f "$local_emulators/lib/libSDL_mixer-1.2.so.0" ||
      ! -f "$local_emulators/lib/libpng14.so.14" ]]; then
    "$repo_root/scripts/build-rg280v-emulator-libs.sh"
fi
"$repo_root/scripts/build-rg280v-fe.sh"

adb -P "$port" connect "$serial" >/dev/null
"${adb[@]}" get-state >/dev/null
"${adb[@]}" shell "mkdir -p $remote/emulators $remote/lib $remote/bin $remote/config/frontend $remote/picoarch/bin $remote/picoarch/cores $remote/licenses"

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
copy_checked "$repo_root/assets/frontend/bin/plumos-fceux-prepare" "$remote/bin/plumos-fceux-prepare" 0755
copy_checked "$repo_root/assets/frontend/bin/plumos-standalone-launch" "$remote/bin/plumos-standalone-launch" 0755
copy_checked "$repo_root/assets/frontend/bin/plumos-picoarch-launch" "$remote/bin/plumos-picoarch-launch" 0755
copy_checked "$local_emulators/picoarch-rg280v" "$remote/picoarch/bin/picoarch" 0755
copy_checked "$local_emulators/mednafen_pce_fast_libretro.so" \
    "$remote/picoarch/cores/mednafen_pce_fast_libretro.so" 0644
copy_checked "$local_emulators/mednafen_wswan_libretro.so" \
    "$remote/picoarch/cores/mednafen_wswan_libretro.so" 0644
copy_checked "$local_emulators/picoarch-cores/mednafen_wswan/COPYING" \
    "$remote/licenses/mednafen_wswan-COPYING" 0644
copy_checked "$local_emulators/mednafen_wswan-rg280v-source.tar.gz" \
    "$remote/licenses/mednafen_wswan-rg280v-source.tar.gz" 0644
copy_checked "$local_emulators/picoarch-rg280v-source.tar.gz" \
    "$remote/licenses/picoarch-rg280v-source.tar.gz" 0644
copy_checked "$local_emulators/mednafen_pce_fast-rg280v-source.tar.gz" \
    "$remote/licenses/mednafen_pce_fast-rg280v-source.tar.gz" 0644
copy_checked "$local_emulators/picoarch-source/LICENSE" \
    "$remote/licenses/picoarch-LICENSE" 0644
copy_checked "$local_emulators/beetle-pce-fast-source/COPYING" \
    "$remote/licenses/mednafen_pce_fast-COPYING" 0644
copy_checked "$repo_root/assets/frontend/regba-global-config.cfg" "$remote/config/regba-global-config.cfg" 0644
copy_checked "$repo_root/board/rg280v/overlay/etc/udev/rules.d/70-plumos-gpio-keys.rules" \
    "$remote/config/70-plumos-gpio-keys.rules" 0644
for name in fceux_gcw0-2.6.6-2023-08-30.opk gambatte-dms-rg280v.opk \
    PocketSNES_2019-12-12.opk ReGBA_1.9.2_rg280v.opk PicoDrive_rg280v.opk; do
    copy_checked "$local_emulators/$name" "$remote/emulators/$name" 0644
done
for name in libSDL_image-1.2.so.0 libSDL_mixer-1.2.so.0 libpng14.so.14 \
    libregba-doublebuf.so libfceux-menu.so libgambatte-menu.so; do
    copy_checked "$local_emulators/lib/$name" "$remote/lib/$name" 0644
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
