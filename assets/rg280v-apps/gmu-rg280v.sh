#!/bin/sh
set -eu
export LD_LIBRARY_PATH="/opk/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export SDL_NOMOUSE=1
cd /opk
mkdir -p "$HOME/.config/gmu"
if [ -e "$HOME/.config/gmu/gmu.conf" ] && \
   ! grep -q '^Gmu.DefaultFileBrowserPath=' "$HOME/.config/gmu/gmu.conf"; then
    cp "$HOME/.config/gmu/gmu.conf" "$HOME/.config/gmu/gmu.conf.broken"
    rm "$HOME/.config/gmu/gmu.conf"
fi
if [ ! -e "$HOME/.config/gmu/gmu.conf" ]; then
    cp /opk/gmu.rg280v.conf "$HOME/.config/gmu/gmu.conf"
fi
status=0
/opk/gmu.bin -d /opk -c gmu.conf \
    >"$HOME/.config/gmu/last.log" 2>&1 || status=$?
sleep 0.3
exit "$status"
