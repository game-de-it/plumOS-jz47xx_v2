#!/bin/sh
set -eu
export LD_LIBRARY_PATH="/opk/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cd /opk

if [ -n "${FFPLAY_TEST_FILE:-}" ]; then
    media=$FFPLAY_TEST_FILE
elif [ "$#" -gt 0 ] && [ -f "$1" ]; then
    media=$1
else
    media=$(/opk/ffplay-picker) || exit 0
fi

mkdir -p "$HOME/.config/ffplay/file_settings"
exec /opk/ffplay -x 320 -y 480 -fs -autoexit "$media"
