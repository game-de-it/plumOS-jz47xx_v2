#!/usr/bin/env python3
"""Expose only explicitly reviewed, checksum-matched source builds in Apps."""
import hashlib
import json
import pathlib
import shlex
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/local/rg350-source-repairs'
OUT = ROOT / 'output/rg280v-apps/source-repair-apps'
OUT.mkdir(exist_ok=True)
Q = shlex.quote

def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True, errors='replace').strip()

def push(source, target):
    subprocess.run(ADB + ['push', str(source), target], check=True, capture_output=True)
    assert shell('sha256sum ' + Q(target)).split()[0] == hashlib.sha256(source.read_bytes()).hexdigest()

subprocess.run(['adb', '-P', '5041', 'connect', '10.1.1.2:5555'], check=True)
candidates = json.loads((ROOT / 'assets/rg280v-apps/source-repair-visual-candidates.json').read_text())
assert len({c['id'] for c in candidates}) == len(candidates)
assert all(c['review'] == 'machine-pass-physical-pending' for c in candidates)
path = '/media/data/plumos/config/frontend/apps.json'
apps = json.loads(shell('cat ' + path))
backup = OUT / 'apps-before.json'
if not backup.exists():
    backup.write_text(json.dumps(apps, ensure_ascii=False, indent=2) + '\n')
assert not shell("ps | busybox grep '/opk/plumos-emulator' | busybox grep -v grep"), 'Emulator is running'
shell('mkdir -p ' + BASE + '/opk ' + BASE + '/log')
installed = {}
entries = []
for c in candidates:
    n = c['number']
    opk = ROOT / f'output/rg280v-apps/source-repair-opks/{n:02d}.opk'
    assert hashlib.sha256(opk.read_bytes()).hexdigest() == c['sha256'], c['id']
    # A real PAL 50 Hz field clock straddles 50.00 in finite measurement windows.
    # Permit only 0.05 FPS measurement jitter for an explicitly verified PAL clock.
    fps = c['gameplay_fps_min']
    assert fps >= 50 or (c.get('native_fps') == 50 and fps >= 49.95)
    assert c['screen_reviewed'] and c['audio_signal_checked']
    assert c['clean_exit'] and c['fe_restored']
    rom = c['rom']
    assert rom.startswith('/media/data/sd2/'), rom
    assert shell('test -f ' + Q(rom) + ' && echo yes') == 'yes', rom
    if n not in installed:
        push(opk, BASE + f'/opk/{n:02d}.opk')
        installed[n] = True
    wrapper = OUT / c['id']
    wrapper.write_text('''#!/bin/sh
set -eu
root=/media/data/plumos
"$root/bin/plumos-prepare-opk-input"
export PLUMOS_ROOT="$root" HOME="$root/home"
export SDL_VIDEODRIVER=kmsdrm LD_LIBRARY_PATH="$root/lib"
exec /usr/bin/opkrun ''' + Q(BASE + f'/opk/{n:02d}.opk') + ' ' + Q(rom) +
        ' >' + Q(BASE + '/log/' + c['id'] + '.log') + ' 2>&1\n')
    dest = BASE + '/' + c['id']
    push(wrapper, dest)
    shell('chmod 755 ' + Q(dest))
    entries.append(dict(id=c['id'], display_name=c['display_name'], menu='apps',
                        kind='shell', visible=True, launch_profile='shell:' + dest))
apps['apps'] = entries + [a for a in apps['apps'] if not a.get('id', '').startswith('rg350_source_repair_')]
result = OUT / 'apps-after.json'
result.write_text(json.dumps(apps, ensure_ascii=False, indent=2) + '\n')
push(result, path + '.tmp')
shell('mv ' + path + '.tmp ' + path)
assert json.loads(shell('cat ' + path)) == apps
shell('/media/data/local/init.d/S95frontend restart')
print(f'Added {len(entries)} physical-review entries from {len(installed)} rebuilt packages')
