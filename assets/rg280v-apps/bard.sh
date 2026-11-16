#!/bin/sh
set -eu
export LD_LIBRARY_PATH="/opk/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cd /opk
if [ ! -f "$HOME/.bard_config" ]; then
    exec /opk/bard -screen_width 320 -screen_height 240 -font /opk/default.otf \
        -font_size 18 -text /opk/Bard_Help.html
fi
exec /opk/bard -screen_width 320 -screen_height 240 -font /opk/default.otf
