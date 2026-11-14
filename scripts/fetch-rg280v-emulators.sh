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
fetch_checked ReGBA_1.9.2_rg350.opk 1e7e0a3c67aae88c0d10752572156db7d1501b4c5eb6999a882be6ae2bf23e93 \
    https://github.com/jdgleaver/ReGBA/releases/download/1.9.2/regba_rg350.opk
fetch_checked ReGBA_1.9.2-GPL-2.0.txt ab15fd526bd8dd18a9e77ebc139656bf4d33e97fc7238cd11bf60e2b9b8666c6 \
    https://raw.githubusercontent.com/jdgleaver/ReGBA/4396f9eca3320b7e2955e2815cfe6332542b91be/doc/gpl-2.0_en.txt
fetch_checked GenesisPlusGX_2019-12-23.opk 38919450a9a379642549ce99ac6805d6d84e17e84ba338a426f731bc655d5e65
