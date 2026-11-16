#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
out="$repo_root/output/rg280v-emulators"
sources="$out/picoarch-cores"
recipes=${PLUMOS_PICOARCH_RECIPES:-$repo_root/scripts/rg280v-picoarch-cores.tsv}
core_filter=${PLUMOS_PICOARCH_CORE_FILTER:-}
mkdir -p "$sources" "$out/picoarch-cores-logs"

build_one() {
    local id=$1 repo=$2 ref=$3 subdir=$4 makefile=$5 args=$6
    local checkout="$sources/$id" log="$out/picoarch-cores-logs/$id.log"
    local source_dir="$checkout${subdir:+/$subdir}"
    if [[ "${PLUMOS_PICOARCH_SKIP_BUILT:-0}" == 1 && -s "$out/${id}_libretro.so" ]]; then
        echo "KEEP $id (already built)"
        return
    fi
    if [[ "$id" == mednafen_pce_fast && -s "$out/mednafen_pce_fast_libretro.so" ]]; then
        echo "KEEP $id (existing tested RG280V build)"
        return
    fi
    if [[ ! -d "$checkout/.git" ]]; then
        mkdir -p "$checkout"
        git -C "$checkout" init -q
        git -C "$checkout" remote add origin "$repo"
    fi
    if [[ "$(git -C "$checkout" rev-parse HEAD 2>/dev/null || true)" != "$ref" ]]; then
        git -C "$checkout" fetch -q --depth 1 origin "$ref"
        git -C "$checkout" checkout -q --detach FETCH_HEAD
    fi
    git -C "$checkout" submodule update --init --depth 1 --quiet
    if [[ "$id" == quicknes ]]; then
        python3 "$repo_root/scripts/patch-rg280v-quicknes.py" "$checkout"
    fi
    if [[ "$id" == chimerasnes ]]; then
        python3 "$repo_root/scripts/patch-rg280v-chimerasnes.py" "$checkout"
    fi
    if [[ "$id" == mednafen_supafaust ]]; then
        python3 "$repo_root/scripts/patch-rg280v-supafaust.py" "$checkout"
    fi
    if [[ "$id" == pcsx_rearmed ]]; then
        python3 "$repo_root/scripts/patch-rg280v-pcsx-rearmed.py" "$checkout"
    fi
    case "$id" in
        opera|mednafen_pcfx)
            rthreads="$source_dir/libretro-common/rthreads/rthreads.c" ;;
        np2kai)
            rthreads="$checkout/sdl/libretro/libretro-common/rthreads/rthreads.c" ;;
        *) rthreads= ;;
    esac
    if [[ -n "$rthreads" ]]; then
        python3 - "$rthreads" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()
before = '#if defined(VITA) || defined(BSD) || defined(ORBIS)'
after = before + ' || defined(__linux__)'
if before in source and after not in source:
    path.write_text(source.replace(before, after, 1))
PY
    fi
    echo "BUILD $id"
    if [[ "$makefile" == CMakeLists.txt ]]; then
        if ! docker run --rm --platform linux/arm64 \
            --user "$(id -u):$(id -g)" -e HOME=/tmp \
            -v "$repo_root:/workspace" \
            -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
            -w "/workspace/output/rg280v-emulators/picoarch-cores/$id${subdir:+/$subdir}" \
            plumos-jz47xx-build:bookworm bash -c '
                set -e
                export PATH=/workspace/output/rg280v/host/bin:$PATH
                cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
                sysroot=/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot
                target=${1#*target=}
                target=${target%% *}
                [[ "$1" == *target=* ]] || { echo "CMake target missing: $1" >&2; exit 1; }
                extra=()
                if [[ "$target" == mgba_libretro ]]; then
                    extra=(-DBUILD_LIBRETRO=ON -DDISABLE_FRONTENDS=ON -DBUILD_QT=OFF
                           -DBUILD_SDL=OFF -DBUILD_PYTHON=OFF -DBUILD_TEST=OFF
                           -DBUILD_PERF=OFF -DBUILD_SUITE=OFF -DBUILD_CINEMA=OFF
                           -DUSE_FFMPEG=OFF -DUSE_LIBZIP=OFF -DUSE_MINIZIP=OFF
                           -DUSE_PNG=OFF -DUSE_SQLITE3=OFF -DUSE_LUA=OFF)
                elif [[ "$target" == easyrpg_libretro ]]; then
                    extra=(-DPLAYER_TARGET_PLATFORM=libretro
                           -DPLAYER_AUDIO_BACKEND=libretro)
                fi
                cmake -S . -B build-rg280v -DCMAKE_SYSTEM_NAME=Linux \
                    -DCMAKE_C_COMPILER="${cross}gcc" -DCMAKE_CXX_COMPILER="${cross}g++" \
                    -DCMAKE_FIND_ROOT_PATH="$sysroot" -DCMAKE_BUILD_TYPE=Release \
                    "${extra[@]}"
                cmake --build build-rg280v --target "$target" -j4
            ' bash "$args" >"$log" 2>&1; then
            echo "FAIL $id: $log"
            return 1
        fi
    elif ! docker run --rm --platform linux/arm64 \
        --user "$(id -u):$(id -g)" -e HOME=/tmp \
        -v "$repo_root:/workspace" \
        -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v \
        -w "/workspace/output/rg280v-emulators/picoarch-cores/$id${subdir:+/$subdir}" \
        plumos-jz47xx-build:bookworm bash -c '
            set -e
            export PATH=/workspace/output/rg280v/host/bin:$PATH
            cross=/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-
            ar_args=(AR="${cross}ar")
            [[ "$3" == lutro ]] && ar_args=()
            [[ "$3" == scummvm ]] && ar_args=(AR="${cross}ar cru")
            make -f "$1" -j4 CC="${cross}gcc" CXX="${cross}g++" "${ar_args[@]}" \
                RANLIB="${cross}ranlib" STRIP="${cross}strip" $2
        ' bash "$makefile" "$args" "$id" >"$log" 2>&1; then
        echo "FAIL $id: $log"
        return 1
    fi
    local built
    built=$(find "$checkout" -type f -name "${id}_libretro.so" -print -quit)
    if [[ -z "$built" ]]; then
        built=$(find "$source_dir" -type f -name '*_libretro.so' -print -quit)
    fi
    if [[ -z "$built" ]]; then
        echo "FAIL $id: no libretro .so in $source_dir"
        return 1
    fi
    cp "$built" "$out/${id}_libretro.so"
    if [[ "$id" == mednafen_wswan ]]; then
        git -C "$checkout" archive --format=tar.gz \
            --output="$out/mednafen_wswan-rg280v-source.tar.gz" HEAD
    fi
    file "$out/${id}_libretro.so"
    shasum -a 256 "$out/${id}_libretro.so"
}

failed=()
matched=0
while IFS='|' read -r id class repo ref subdir makefile args; do
    [[ -z "$id" || "$id" == \#* ]] && continue
    [[ -z "$core_filter" || "$id" == "$core_filter" ]] || continue
    matched=1
    if ! build_one "$id" "$repo" "$ref" "$subdir" "$makefile" "$args"; then
        failed+=("$id")
    fi
done < "$recipes"
if [[ -n "$core_filter" && "$matched" == 0 ]]; then
    echo "Core not found in recipes: $core_filter" >&2
    exit 1
fi
if (( ${#failed[@]} )); then
    printf 'Failed cores: %s\n' "${failed[*]}" >&2
    exit 1
fi
