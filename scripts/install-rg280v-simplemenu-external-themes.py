#!/usr/bin/env python3
"""Fetch pinned external themes and install original assets on a private device."""
import hashlib
import json
import pathlib
import shlex
import subprocess
import tarfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/rg280v-simplemenu/external-themes'
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
HOME = '/media/data/plumos/home/simplemenu/.simplemenu'
THEMES = HOME + '/themes/320x240'
CATALOG = [
    ('SimUI', 'https://github.com/dkodr/SimUI.git',
     '13d35f79f9b6c75f034c51838496aa922b272045', 'SimUI', '320x240/SimUI'),
    ('ArtBook', 'https://github.com/anthonycaccese/sm-theme-art-book.git',
     'f64636382fbcc5c5bb9b9e79fbf116e43cbcc79b', 'art-book', '320x240/ArtBook'),
]


def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True).strip()


def installed_names():
    return sorted(shell('for d in ' + THEMES + '/*; do if test -d "$d"; '
                        'then echo "${d##*/}"; fi; done').splitlines(), key=str.lower)


if shell("ps | awk '$5==\"./simplemenu\" {print $1}'"):
    raise SystemExit('Exit SimpleMenu before adding themes')
if int(shell('df -k /media/data').splitlines()[-1].split()[3]) < 20 * 1024:
    raise SystemExit('Need 20 MiB free SD1 space')
OUT.mkdir(parents=True, exist_ok=True)
names_before = installed_names()
state = shell('cat ' + HOME + '/last_state.sav') + '\n'
lines = state.splitlines()
if len(lines) < 10 or lines[0] != '10;':
    raise SystemExit('Unsupported saved-state header')
selected = names_before[int(lines[5].rstrip(';'))]
archive = OUT / 'external-themes.tar'
manifest = []
with tarfile.open(archive, 'w') as tar:
    for name, url, revision, folder, subdir in CATALOG:
        repo = OUT / folder
        if not repo.exists():
            subprocess.run(['git', 'clone', '--depth', '1', url, str(repo)], check=True)
        actual = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != revision or subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain']):
            raise SystemExit('Theme source differs from pinned original: ' + name)
        source = repo / subdir
        tar.add(source, arcname=name)
        files = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(source.rglob('*')) if p.is_file()}
        manifest.append(dict(name=name, url=url, revision=revision, files=files))
backup = '/media/data/plumos/backup/simplemenu-themes-' + time.strftime('%Y%m%d-%H%M%S')
shell('mkdir -p ' + backup + '; cp -p ' + HOME + '/last_state.sav ' + backup + '/')
for name, *_ in CATALOG:
    shell('if test -d ' + THEMES + '/' + name + '; then cp -a ' + THEMES + '/' + name + ' ' + backup + '/; fi')
remote_archive = '/media/data/plumos/simplemenu-external-themes.tar'
subprocess.run(ADB + ['push', str(archive), remote_archive], check=True)
assert shell('sha256sum ' + remote_archive).split()[0] == hashlib.sha256(archive.read_bytes()).hexdigest()
shell('set -e; tar -xf ' + remote_archive + ' -C ' + THEMES + '; rm ' + remote_archive)
for entry in manifest:
    for relative, expected in entry['files'].items():
        remote = THEMES + '/' + entry['name'] + '/' + relative
        assert shell('sha256sum ' + shlex.quote(remote)).split()[0] == expected, remote
lines[5] = str(installed_names().index(selected)) + ';'
state_file = OUT / 'last-state-preserved.sav'
state_file.write_text('\n'.join(lines) + '\n')
subprocess.run(ADB + ['push', str(state_file), HOME + '/last_state.sav.new'], check=True)
assert shell('sha256sum ' + HOME + '/last_state.sav.new').split()[0] == hashlib.sha256(state_file.read_bytes()).hexdigest()
shell('mv ' + HOME + '/last_state.sav.new ' + HOME + '/last_state.sav')
(OUT / 'installed-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Installed original themes; previous selected theme preserved:', selected)
