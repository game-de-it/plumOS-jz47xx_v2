#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
port=${ADB_SERVER_PORT:-5037}
serial=${PLUMOS_RG280V_ADB_SERIAL:-10.1.1.2:5555}
out=${1:-$repo_root/output/rg280v-fe/screenshot.png}
raw=${out%.png}.raw
mkdir -p "$(dirname "$out")"

for attempt in 1 2 3; do
    adb -P "$port" -s "$serial" shell \
        'dd if=/dev/fb0 of=/media/data/plumos/state/frontend/fb.raw bs=614400 count=1 2>/dev/null'
    adb -P "$port" -s "$serial" pull \
        /media/data/plumos/state/frontend/fb.raw "$raw" >/dev/null
    [[ $(stat -f %z "$raw") == 614400 ]] && break
done
python3 - "$raw" "$out" <<'PY'
import sys
from PIL import Image

raw, output = sys.argv[1:]
data = open(raw, 'rb').read()
if len(data) != 320 * 480 * 4:
    raise SystemExit(f'unexpected framebuffer length: {len(data)}')
image = Image.frombytes('RGBA', (320, 480), data, 'raw', 'BGRA')
image.convert('RGB').resize((320, 240)).save(output)
print(output)
PY
