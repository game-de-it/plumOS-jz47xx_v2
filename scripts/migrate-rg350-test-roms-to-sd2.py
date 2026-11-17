#!/usr/bin/env python3
"""Move owned OPK test ROMs to SD2 after hash verification; retain path aliases."""
import json
import pathlib
import shlex
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
DEST = '/media/data/sd2/.plumos-rg350-tests-20261118/relocated'
BASE = '/media/data/local/rg350-rom-candidates'
EXTRA = '/media/data/local/rg350-missing-rom-retest'
subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)

def sh(command):
    for attempt in range(3):
        result = subprocess.run(ADB + ['shell', command], capture_output=True, text=True, errors='replace')
        if result.returncode == 0:
            return result.stdout.strip()
        if attempt == 2:
            raise RuntimeError(command + '\n' + result.stderr + result.stdout)
        subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], capture_output=True)
        time.sleep(1)

def quote(path):
    return shlex.quote(path)

def exists(path):
    return sh('test -e ' + quote(path) + ' && echo yes || true') == 'yes'

def hashes(path):
    output = sh('find ' + quote(path) + ' -type f -exec sha256sum {} \;')
    values = {}
    for line in output.splitlines():
        digest, name = line.split(None, 1)
        name = name.strip()
        assert name.startswith(path + '/')
        values[name[len(path)+1:]] = digest
    return values

mount = next(x for x in sh('cat /proc/mounts').splitlines() if x.split()[1] == '/media/data/sd2')
assert mount.split()[0] == '/dev/mmcblk1p1' and 'ro' in mount.split()[3].split(','), mount
assert int(sh('df -k /media/data/sd2').splitlines()[-1].split()[3]) > 256 * 1024
assert not sh('ps | grep -E "opkrun|plumos-emulator" | grep -v grep'), 'An emulator is still running'
marker = DEST + '/.owned-rg350-rom-migration'
if exists(DEST):
    assert exists(marker), 'Refusing to reuse an unowned destination'

families = [g['family'] for g in json.loads((ROOT / 'output/rg280v-apps/rg350-rom-candidates.json').read_text())]
trees = [(BASE + '/' + family, DEST + '/rom-candidates/' + family) for family in families]
trees += [('/media/data/local/rg350-visual-tests/rom', DEST + '/visual-roms')]
trees += [(EXTRA + '/' + name, DEST + '/extra-roms/' + name) for name in ['gw', 'c64', 'large', 'scumm-corrected', 'dos']]
bios = ['home-01/.3doh/bios.bin', 'home-06/.DCaSTaway/bios/rom',
        'home-30/.uae4all/kick.rom', 'home-60/.uae4all/kick.rom',
        'home-42/bios/exec.bin', 'home-42/bios/grom.bin', 'home-15/.neo4all/neocd.bin']
trees += [(EXTRA + '/home-39/bios', DEST + '/bios/neogeo')]
before_df = sh('df -k /media/data')
records = []
sh('/media/data/local/init.d/S95frontend stop')
try:
    sh('mount -o remount,rw /media/data/sd2')
    sh('mkdir -p ' + quote(DEST) + '; touch ' + quote(marker))
    pending = []
    for source, target in trees:
        if not exists(source):
            continue
        link = sh('test -L ' + quote(source) + ' && readlink ' + quote(source) + ' || true')
        if link:
            assert link == target, (source, link)
            continue
        assert not sh('find ' + quote(source) + ' -type l'), source
        original = hashes(source)
        sh('mkdir -p ' + quote(target) + '; cp -R ' + quote(source + '/.') + ' ' + quote(target + '/'))
        copied = hashes(target)
        assert copied == original, source
        pending.append((source, target, original))
        print('Verified', source, len(original), 'files', flush=True)
    for relative in bios:
        source = EXTRA + '/' + relative
        if not exists(source) or sh('test -L ' + quote(source) + ' && echo yes || true'):
            continue
        target = DEST + '/bios/' + relative
        sh('mkdir -p ' + quote(str(pathlib.PurePosixPath(target).parent)) + '; cp ' + quote(source) + ' ' + quote(target))
        digest = sh('sha256sum ' + quote(source)).split()[0]
        assert sh('sha256sum ' + quote(target)).split()[0] == digest
        pending.append((source, target, digest))
    # The ISO must be a real file beside its same-basename CUE, since opkrun
    # resolves ROM symlinks. Reuse the already verified full WAV set on SD2.
    cd = EXTRA + '/home-15/cd'
    wav = '/media/data/sd2/.plumos-rg350-tests-20261118/Fatal Fury WAV'
    if not sh('test -L ' + quote(cd) + ' && echo yes || true'):
        assert sh('sha256sum ' + quote(cd + '/Fatal Fury.iso')).split()[0] == sh('sha256sum ' + quote(wav + '/Fatal Fury.iso')).split()[0]
        sh('cp ' + quote(cd + '/Fatal Fury.cue') + ' ' + quote(wav + '/Fatal Fury.cue'))
        assert sh('sha256sum ' + quote(cd + '/Fatal Fury.cue')).split()[0] == sh('sha256sum ' + quote(wav + '/Fatal Fury.cue')).split()[0]
        pending.append((cd, wav, 'ISO and matching CUE verified'))
    sh('sync')
    # All target data is verified before removing any original test data.
    for source, target, evidence in pending:
        assert source.startswith((BASE + '/', EXTRA + '/', '/media/data/local/rg350-visual-tests/rom'))
        sh('rm -rf ' + quote(source) + '; ln -s ' + quote(target) + ' ' + quote(source))
        assert sh('readlink ' + quote(source)) == target
        assert exists(source)
        records.append(dict(source=source, target=target, sha256=evidence))
    sh('sync')
finally:
    sh('mount -o remount,ro /media/data/sd2')
    final_mount = next(x for x in sh('cat /proc/mounts').splitlines() if x.split()[1] == '/media/data/sd2')
    assert 'ro' in final_mount.split()[3].split(',')
    sh('/media/data/local/init.d/S95frontend start')
out = ROOT / 'output/rg280v-apps/rom-sd2-migration-20261118.json'
out.write_text(json.dumps(dict(mount_before=mount, mount_after=final_mount,
    sd1_before=before_df, sd1_after=sh('df -k /media/data'), moved=records), ensure_ascii=False, indent=2))
print('ROMs moved; SD2 restored read-only; frontend restarted', flush=True)

manifest = ROOT / 'output/rg280v-apps/rg350-rom-candidates.json'
groups = json.loads(manifest.read_text())
for group in groups:
    for item in group['candidates']:
        if item.get('remote') and item['remote'].startswith(BASE + '/'):
            item['remote'] = DEST + '/rom-candidates/' + item['remote'][len(BASE)+1:]
manifest.write_text(json.dumps(groups, ensure_ascii=False, indent=2) + '\n')
