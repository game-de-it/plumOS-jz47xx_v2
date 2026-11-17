#!/usr/bin/env python3
"""Test the original Neo4All executable against a complete, verified WAV set."""
import hashlib
import json
import pathlib
import shlex
import subprocess
import argparse
from rg350_test_rom_storage import ROM_ROOT, stage_file

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

shell('mkdir -p ' + HOME + '/.neo4all/roms')
bios = NAS / 'bios/neocd/neocd.bin'
dest = ROM_ROOT + '/bios/home-15/.neo4all/neocd.bin'
stage_file(bios, dest)
shell('ln -sf ' + shlex.quote(dest) + ' ' + HOME + '/.neo4all/neocd.bin')
shell('ln -sf ../neocd.bin ' + HOME + '/.neo4all/roms/neocd.bin')
# ISO and audio are regular files on SD2; opkrun can resolve the ISO safely.
stage_file(NAS / '_etc/neogeocd/Fatal Fury WAV/Fatal Fury WAV.cue', source + '/Fatal Fury.cue')
assert shell('test -f ' + shlex.quote(source + '/Fatal Fury.iso') + ' && echo yes').strip() == 'yes'
if args.prepare_only:
    raise SystemExit(0)
subprocess.run([
    'python3', str(ROOT / 'scripts/audit-rg350-opks-device.py'),
    '--only', '15', '--opk', '15=' + str(ROOT / 'output/rg280v-apps/missing-rom-opks/15.opk'),
    '--rom', '15=' + source + '/Fatal Fury.iso',
    '--seconds', '45', '--screenshot-delay', '38', '--start-presses', '10',
    '--tag', 'rom-retest-wav-20261118-15-1',
], check=True, cwd=ROOT)
