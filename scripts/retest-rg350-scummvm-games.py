#!/usr/bin/env python3
"""Use ScummVM engine data and scene-skip controls; START opens its pause menu."""
import hashlib
import pathlib
import shlex
import subprocess
from rg350_test_rom_storage import ROM_ROOT, stage_file, host_rom_root

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAS = (host_rom_root() / 'scummvm')
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = ROM_ROOT + '/extra-roms/scumm-corrected'
subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)

def shell(text):
    return subprocess.check_output(ADB + ['shell', text], text=True, errors='replace')

for i, name in enumerate(["Monkey Island 2 LeChuck's Revenge (Floppy DOS VGA)", 'BASS-Floppy-1.3'], 1):
    dest = BASE + '/' + name
    try:
        for src in (NAS / name).iterdir():
            if not src.is_file():
                continue
            target = dest + '/' + src.name
            stage_file(src, target)
        subprocess.run([
            'python3', str(ROOT / 'scripts/audit-rg350-opks-device.py'),
            '--only', '56', '--opk', '56=' + str(ROOT / 'output/rg280v-apps/missing-rom-opks/56.opk'),
            '--rom', '56=' + dest, '--seconds', '30', '--screenshot-delay', '26',
            '--key-event', '8:1:150', '--key-event', '14:1:150', '--key-event', '20:29:150',
            '--extra-lib-dir', '/media/data/local/rg350-missing-rom-retest/lib',
            '--tag', f'rom-retest-play-20261118-56-{i}',
        ], cwd=ROOT, check=True)
    finally:
        pass  # Keep verified ROM data on SD2 for repeat tests.
