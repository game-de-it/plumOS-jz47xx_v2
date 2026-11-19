#!/usr/bin/env bash
# Run with the JZ47xx SDK mounted at /workspace/output/rg280v.
set -euo pipefail
cd /workspace
source_image=output/jz47xx-multimodel/boot/rootfs.squashfs
output=output/rg350m-validation
tools=output/rg280v/host/bin
stage=$(mktemp -d)
trap 'rm -rf -- "$stage"' EXIT

mkdir -p "$output"
"$tools/unsquashfs" -no-progress -d "$stage/root" "$source_image" >/dev/null
install -m 0755 scripts/diagnostics/rg350m-display-snapshot.sh \
    "$stage/root/usr/sbin/rg350m-display-snapshot"

python3 - "$stage/root/etc/init.d/rcS" <<'PY'
import sys
from pathlib import Path

script = Path(sys.argv[1])
content = script.read_text()
before_services = '    mkdir -p /media/data/local/init.d\n    for service'
if content.count(before_services) != 1 or content.count('\nlog READY\n') != 1:
    raise SystemExit('Unexpected rcS layout in reference rootfs')
content = content.replace(
    before_services,
    '    /usr/sbin/rg350m-display-snapshot before-frontend || true\n' + before_services,
)
content = content.replace(
    '\nlog READY\n',
    '''\nlog READY

(
    /usr/sbin/rg350m-display-snapshot ready || true
    sleep 5
    /usr/sbin/rg350m-display-snapshot after-5s || true
    sleep 15
    /usr/sbin/rg350m-display-snapshot after-20s || true
) &
''',
)
script.write_text(content)
PY

sh -n "$stage/root/etc/init.d/rcS"
sh -n "$stage/root/usr/sbin/rg350m-display-snapshot"
"$tools/mksquashfs" "$stage/root" "$stage/rootfs.squashfs" \
    -noappend -no-progress -comp zstd -b 131072 >/dev/null
"$tools/unsquashfs" -cat "$stage/rootfs.squashfs" etc/init.d/rcS |
    cmp - "$stage/root/etc/init.d/rcS"
"$tools/unsquashfs" -cat "$stage/rootfs.squashfs" usr/sbin/rg350m-display-snapshot |
    cmp - scripts/diagnostics/rg350m-display-snapshot.sh
cp "$stage/rootfs.squashfs" "$output/rootfs-display-diagnostic.squashfs"
sha256sum "$source_image" "$output/rootfs-display-diagnostic.squashfs"
