#!/bin/sh
set -eu
root=${PLUMOS_ROOT:-/media/data/plumos}
export HOME="${PLUMOS_OPK_HOME:-$root/home/opk/crocods}"
export LD_LIBRARY_PATH="$root/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-kmsdrm}" SDL_AUDIODRIVER="${SDL_AUDIODRIVER:-alsa}"
. "$root/bin/plumos-jz47xx-media-env"
plumos_select_media
export CROCODS_FIRMWARE_DIR="$PLUMOS_BIOS_ROOT/opk/crocods"
mkdir -p "$HOME"
cd "$HOME"
rc=0
/opk/crocods "$@" || rc=$?
printf 'PLUMOS_EMULATOR_EXIT=%s\n' "$rc"
exit "$rc"
