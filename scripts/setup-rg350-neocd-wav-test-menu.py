#!/usr/bin/env python3
"""Expose the isolated Neo4All BGM/WAV comparison in Apps."""
import hashlib
import json
import pathlib
import shlex
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/local/rg350-missing-rom-retest'
OUT = ROOT / 'output/rg280v-apps/neo4all-wav-test-menu'
OUT.mkdir(exist_ok=True)
subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)

def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True, errors='replace')

def push(src, dest):
    subprocess.run(ADB + ['push', str(src), dest], capture_output=True, check=True)
    assert shell('sha256sum ' + shlex.quote(dest)).split()[0] == hashlib.sha256(src.read_bytes()).hexdigest()

opk = ROOT / 'output/rg280v-apps/neo4all-rg280v-bgm-test.opk'
push(opk, BASE + '/neo4all-bgm.opk')
wrapper = OUT / 'run-neo4all-wav'
wrapper.write_text('''#!/bin/sh
set -eu
root=/media/data/plumos
"$root/bin/plumos-prepare-opk-input"
export PLUMOS_ROOT="$root" HOME=/media/data/local/rg350-missing-rom-retest/home-15
export SDL_VIDEODRIVER=kmsdrm LD_LIBRARY_PATH="$root/lib"
exec /usr/bin/opkrun /media/data/local/rg350-missing-rom-retest/neo4all-bgm.opk "/media/data/local/rg350-missing-rom-retest/home-15/cd/Fatal Fury.iso"
''')
push(wrapper, BASE + '/run-neo4all-wav')
shell('chmod 755 ' + BASE + '/run-neo4all-wav')
path = '/media/data/plumos/config/frontend/apps.json'
apps = json.loads(shell('cat ' + path))
backup = OUT / 'apps-before.json'
if not backup.exists():
    backup.write_text(json.dumps(apps, ensure_ascii=False, indent=2))
ident = 'rg350_missing_neo4all_wav'
apps['apps'] = [a for a in apps['apps'] if a.get('id') != ident]
apps['apps'].append(dict(id=ident, display_name='TEST 15 Neo4All BGM: Fatal Fury WAV',
    menu='apps', kind='shell', visible=True, launch_profile='shell:' + BASE + '/run-neo4all-wav'))
result = OUT / 'apps-with-neo4all.json'
result.write_text(json.dumps(apps, ensure_ascii=False, indent=2) + '\n')
push(result, path + '.tmp')
shell('mv ' + path + '.tmp ' + path)
assert json.loads(shell('cat ' + path)) == apps
print('Added isolated Neo4All WAV comparison')
