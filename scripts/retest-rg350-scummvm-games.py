#!/usr/bin/env python3
"""Use ScummVM engine data and scene-skip controls; START opens its pause menu."""
import hashlib
import pathlib
import shlex
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAS = pathlib.Path('<local-path>')
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/local/rg350-missing-rom-retest/scumm-corrected'
subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)

def shell(text):
    return subprocess.check_output(ADB + ['shell', text], text=True, errors='replace')

for i, name in enumerate(["Monkey Island 2 LeChuck's Revenge (Floppy DOS VGA)", 'BASS-Floppy-1.3'], 1):
    dest = BASE + '/' + name
    shell('mkdir -p ' + shlex.quote(dest))
    try:
        for src in (NAS / name).iterdir():
            if not src.is_file():
                continue
            target = dest + '/' + src.name
            subprocess.run(ADB + ['push', str(src), target], capture_output=True, check=True)
            assert shell('sha256sum ' + shlex.quote(target)).split()[0] == hashlib.sha256(src.read_bytes()).hexdigest()
        subprocess.run([
            'python3', str(ROOT / 'scripts/audit-rg350-opks-device.py'),
            '--only', '56', '--opk', '56=' + str(ROOT / 'output/rg280v-apps/missing-rom-opks/56.opk'),
            '--rom', '56=' + dest, '--seconds', '30', '--screenshot-delay', '26',
            '--key-event', '8:1:150', '--key-event', '14:1:150', '--key-event', '20:29:150',
            '--extra-lib-dir', '/media/data/local/rg350-missing-rom-retest/lib',
            '--tag', f'rom-retest-play-20261118-56-{i}',
        ], cwd=ROOT, check=True)
    finally:
        shell('rm -rf ' + shlex.quote(dest))
