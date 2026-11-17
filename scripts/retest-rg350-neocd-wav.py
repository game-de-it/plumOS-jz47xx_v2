#!/usr/bin/env python3
"""Test the original Neo4All executable against a complete, verified WAV set."""
import hashlib
import json
import pathlib
import shlex
import subprocess
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
NAS = pathlib.Path('<local-path>')
HOME = '/media/data/local/rg350-missing-rom-retest/home-15'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--prepare-only', action='store_true')
args = parser.parse_args()
subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)
status = json.loads((ROOT / 'output/rg280v-apps/neocd-wav-stage-status.json').read_text())
assert len(status['files']) == 35 and ' ro,' in status['mount_after']
source = status['destination']

def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True, errors='replace')

shell('mkdir -p ' + HOME + '/cd ' + HOME + '/.neo4all/roms')
bios = NAS / 'bios/neocd/neocd.bin'
dest = HOME + '/.neo4all/neocd.bin'
subprocess.run(ADB + ['push', str(bios), dest], check=True)
assert shell('sha256sum ' + dest).split()[0] == hashlib.sha256(bios.read_bytes()).hexdigest()
shell('ln -sf ../neocd.bin ' + HOME + '/.neo4all/roms/neocd.bin')
shell('ln -sf ../.neo4all/neocd.bin ' + HOME + '/cd/neocd.bin')
for item in status['files']:
    path = item['name']
    if path == 'Fatal Fury.iso':
        # opkrun resolves symlinks before passing the argument. Keep a regular
        # ISO beside the renamed CUE so the emulator can find its track table.
        target = HOME + '/cd/' + path
        shell('rm -f ' + shlex.quote(target))
        shell('cp ' + shlex.quote(source + '/' + path) + ' ' + shlex.quote(target))
        assert shell('sha256sum ' + shlex.quote(target)).split()[0] == item['sha256']
        continue
    shell('ln -sf ' + shlex.quote(source + '/' + path) + ' ' + shlex.quote(HOME + '/cd/' + path))
# This executable looks for a CUE with the ISO's basename. Do not edit the NAS set.
shell('cp ' + shlex.quote(source + '/Fatal Fury WAV.cue') + ' ' + shlex.quote(HOME + '/cd/Fatal Fury.cue'))
if args.prepare_only:
    raise SystemExit(0)
subprocess.run([
    'python3', str(ROOT / 'scripts/audit-rg350-opks-device.py'),
    '--only', '15', '--opk', '15=' + str(ROOT / 'output/rg280v-apps/missing-rom-opks/15.opk'),
    '--rom', '15=' + HOME + '/cd/Fatal Fury.iso',
    '--seconds', '45', '--screenshot-delay', '38', '--start-presses', '10',
    '--tag', 'rom-retest-wav-20261118-15-1',
], check=True, cwd=ROOT)
