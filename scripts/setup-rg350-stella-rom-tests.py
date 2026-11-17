#!/usr/bin/env python3
"""Add three measured Stella comparisons without changing existing emulator routes."""
import hashlib
import json
import pathlib
import shlex
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/local/rg350-rom-candidates'
OUT = ROOT / 'output/rg280v-apps/stella-rom-test-menu'
OUT.mkdir(exist_ok=True)
subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)

def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True, errors='replace')

def push(source, target):
    subprocess.run(ADB + ['push', str(source), target], capture_output=True, check=True)
    assert shell('sha256sum ' + shlex.quote(target)).split()[0] == hashlib.sha256(source.read_bytes()).hexdigest()

shell('mkdir -p ' + BASE + '/opk ' + BASE + '/log')
opk = ROOT / 'output/rg280v-apps/rg350-catalog/Stella_2015-10-06.opk'
push(opk, BASE + '/opk/28.opk')
wrapper = OUT / 'run-stella'
wrapper.write_text('''#!/bin/sh
set -eu
case "${1:-}" in
    4|5|6) rom=/media/data/local/rg350-rom-candidates/atari2600/0$1.bin ;;
    *) exit 2 ;;
esac
root=/media/data/plumos
"$root/bin/plumos-prepare-opk-input"
export HOME="$root/home" PLUMOS_ROOT="$root" SDL_VIDEODRIVER=kmsdrm
export LD_LIBRARY_PATH="$root/lib"
exec /usr/bin/opkrun /media/data/local/rg350-rom-candidates/opk/28.opk "$rom" >"/media/data/local/rg350-rom-candidates/log/stella-$1.log" 2>&1
''')
push(wrapper, BASE + '/run-stella')
shell('chmod 755 ' + BASE + '/run-stella')
path = '/media/data/plumos/config/frontend/apps.json'
apps = json.loads(shell('cat ' + path))
backup = OUT / 'apps-before.json'
if not backup.exists():
    backup.write_text(json.dumps(apps, ensure_ascii=False, indent=2))
prefix = 'rg350_missing_stella_'
apps['apps'] = [a for a in apps['apps'] if not a.get('id', '').startswith(prefix)]
for i, title in enumerate(['Asteroids', 'Centipede', 'Breakout'], 4):
    apps['apps'].append(dict(id=prefix + str(i), display_name=f'TEST 28 Stella {i-3}: {title}',
        menu='apps', kind='shell', visible=True, launch_profile=f'shell:{BASE}/run-stella {i}'))
result = OUT / 'apps-with-stella.json'
result.write_text(json.dumps(apps, ensure_ascii=False, indent=2) + '\n')
push(result, path + '.tmp')
shell('mv ' + path + '.tmp ' + path)
assert json.loads(shell('cat ' + path)) == apps
print('Added three isolated Stella test entries')
