#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
destination="$repo_root/output/rg280v-emulators"
source_revision=2ed8306dfb48472b4a5257dbd27bc461949dca4f
source_base="https://raw.githubusercontent.com/RafaVico/RG350_APPREPOSITORY/$source_revision/Emulators"
mkdir -p "$destination"

fetch_checked() {
    local name=$1 expected=$2 url=${3:-$source_base/$1} actual
    if [[ -f "$destination/$name" ]]; then
        actual=$(shasum -a 256 "$destination/$name" | awk '{print $1}')
        [[ "$actual" == "$expected" ]] && { echo "verified $name"; return; }
    fi
    curl -fL --retry 2 --output "$destination/$name.download" "$url"
    actual=$(shasum -a 256 "$destination/$name.download" | awk '{print $1}')
    [[ "$actual" == "$expected" ]] || { echo "hash mismatch: $name" >&2; rm -f "$destination/$name.download"; exit 1; }
    mv "$destination/$name.download" "$destination/$name"
    echo "verified $name"
}

fetch_checked FCEUX_2019-11-15.opk bf5d600a9dc194cacdb30a87719e4b09eb88cc72abaadf2bb2583e400c76c027
fetch_checked gambatte-dms-multi-r572u4-20211021.opk 320495b9b14ff238afeb6feeebd11f990e3cd807fc65d673380b281b486f538d
fetch_checked PocketSNES_2019-12-12.opk 1987de5708af7074abee335a36ee1b4cb4fb0c79d5a46b521f51e7c9720ff1ae
fetch_checked ReGBA_2019-12-26.opk c2a48ed46d1ec37e9dd9baed2c18c62c04005fbd83a10e2ba6390845420dd52d
fetch_checked GenesisPlusGX_2019-12-23.opk 38919450a9a379642549ce99ac6805d6d84e17e84ba338a426f731bc655d5e65
gba_bios_source=https://raw.githubusercontent.com/Cult-of-GBA/BIOS/a30e9a96df083628b650724b7d4d7112b4070b98
fetch_checked mit-gba-bios.bin 61af6e8c2db6cf24aa6924e8133f6a50833158fca33ff08ea5e11e1a06e132f2 "$gba_bios_source/bios.bin"
fetch_checked MIT-GBA-BIOS-LICENSE 761675b95595be4c2e452876a9c414479da22089f7ccf5a6613ca40a1c80675d "$gba_bios_source/LICENSE"
