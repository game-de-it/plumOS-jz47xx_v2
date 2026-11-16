#!/bin/sh
set -eu
export SDL_NOMOUSE=1
cd /opk
exec /opk/pdfviewer
