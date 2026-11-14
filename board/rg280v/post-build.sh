#!/bin/sh
set -eu

target=$1

# The OpenDingux skeleton is a temporary Buildroot input. Its init services
# are superseded by plumOS rcS, including on incremental builds.
find "$target/etc/init.d" -maxdepth 1 -type f -name 'S[0-9]*' -delete
rm -f "$target/usr/sbin/frontend_start"
