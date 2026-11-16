#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
remote=/media/data/plumos
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
adb=(adb -P "$port" -s "$serial")
"${adb[@]}" get-state >/dev/null
"${adb[@]}" shell "mkdir -p $remote/picoarch/cores $remote/bin $remote/config/frontend $remote/licenses"

copy_checked() {
    local source=$1 destination=$2 mode=$3 expected actual attempt
    expected=$(shasum -a 256 "$source" | awk '{print $1}')
    "${adb[@]}" push "$source" "$destination.new" </dev/null >/dev/null
    for attempt in 1 2 3; do
        actual=$("${adb[@]}" shell "sha256sum $destination.new" </dev/null | awk '{print $1}')
        [[ "$actual" == "$expected" ]] && break
        sleep 1
    done
    [[ "$actual" == "$expected" ]] || {
        echo "hash mismatch: $destination expected=$expected actual=$actual" >&2
        exit 1
    }
    "${adb[@]}" shell "mv $destination.new $destination && chmod $mode $destination" </dev/null
    echo "$expected  $destination"
}

deploy_cores() {
    local recipes=$1 id class repo ref subdir makefile args
    while IFS='|' read -r id class repo ref subdir makefile args; do
        [[ -z "$id" || "$id" == \#* ]] && continue
        copy_checked "$out/${id}_libretro.so" \
            "$remote/picoarch/cores/${id}_libretro.so" 0644
    done < "$recipes"
}

if [[ "${PLUMOS_PICOARCH_ONLY_EXTRA:-0}" != 1 ]]; then
    copy_checked "$repo_root/assets/frontend/bin/plumos-picoarch-launch" \
        "$remote/bin/plumos-picoarch-launch" 0755
    copy_checked "$out/picoarch-rg280v" "$remote/picoarch/bin/picoarch" 0755
    deploy_cores "$repo_root/scripts/rg280v-picoarch-cores.tsv"
    copy_checked "$out/mednafen_wswan_libretro.so" \
        "$remote/picoarch/cores/mednafen_wswan_libretro.so" 0644
    copy_checked "$out/picoarch-cores/mednafen_wswan/COPYING" \
        "$remote/licenses/mednafen_wswan-COPYING" 0644
    copy_checked "$out/mednafen_wswan-rg280v-source.tar.gz" \
        "$remote/licenses/mednafen_wswan-rg280v-source.tar.gz" 0644
fi

if [[ "${PLUMOS_PICOARCH_INCLUDE_EXTRA:-0}" == 1 ]]; then
    while IFS='|' read -r id class repo ref subdir makefile args; do
        [[ -z "$id" || "$id" == \#* ]] && continue
        [[ -s "$out/${id}_libretro.so" ]] || continue
        copy_checked "$out/${id}_libretro.so" \
            "$remote/picoarch/cores/${id}_libretro.so" 0644
    done < "$repo_root/scripts/rg280v-picoarch-extra-cores.tsv"
fi

if [[ "${PLUMOS_PICOARCH_ONLY_EXTRA:-0}" == 1 ]]; then
    exit 0
fi

temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_dir"' EXIT
"${adb[@]}" pull "$remote/config/frontend/systems.json" "$temp_dir/installed.json" >/dev/null
python3 "$repo_root/scripts/merge-rg280v-emulator-profiles.py" \
    "$temp_dir/installed.json" "$repo_root/assets/frontend/systems.json" \
    "$temp_dir/merged.json"
copy_checked "$temp_dir/merged.json" "$remote/config/frontend/systems.json" 0644

if [[ "${PLUMOS_PICOARCH_RESTART_FE:-0}" == 1 ]]; then
    "${adb[@]}" shell /media/data/local/init.d/S95frontend restart
fi
