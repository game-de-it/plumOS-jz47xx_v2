#!/usr/bin/env python3
"""Install SimpleMenu with existing FE launch profiles and the standard 0A theme."""
import hashlib
import argparse
import json
import pathlib
import shlex
import shutil
import subprocess
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT / 'output/rg280v-simplemenu'
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/plumos'
HOME = BASE + '/home/simplemenu/.simplemenu'
Q = shlex.quote
argparse.ArgumentParser(description=__doc__).parse_args()


def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True).strip()


systems = json.loads(shell('cat ' + BASE + '/config/frontend/systems.json'))['systems']
if shell("ps | grep '[.]\/simplemenu' || true"):
    raise SystemExit('Exit SimpleMenu before replacing its executable')
free_kib = int(shell('df -k ' + BASE).splitlines()[-1].split()[3])
if free_kib < 20 * 1024:
    raise SystemExit('SimpleMenu installation requires 20 MiB of free SD1 space')
(WORK / 'install-systems.json').write_text(json.dumps(systems, indent=2))
stage = WORK / 'install'
if stage.exists():
    # Some upstream artwork directories carry read-only permissions.
    def remove_readonly(function, path, error):
        if not isinstance(error[1], PermissionError):
            raise error[1]
        pathlib.Path(path).parent.chmod(0o755)
        pathlib.Path(path).chmod(0o700)
        function(path)
    shutil.rmtree(stage, onerror=remove_readonly)
shutil.copytree(WORK / 'runtime', stage / 'simplemenu')
seed = stage / 'simplemenu/seed/.simplemenu'
seed.mkdir(parents=True)
source = WORK / 'source/simplemenu/output/OD'
shutil.copytree(source / 'themes/320x240/0A', seed / 'themes/320x240/0A')

config = (source / 'config/config.ini').read_text()
config = config.replace('[SCREEN]', '[SCREEN]\nscreen_width = 320\nscreen_height = 240')
for old in ['underclocked_speed = 444', 'overclocked_speed = 1092', 'sleep_speed = 444']:
    config = config.replace(old, old.split(' = ')[0] + ' = 996')
(seed / 'config.ini').write_text(config + '\n')
(seed / 'favorites.sav').write_text('')
for name in ['apps', 'games', 'tmp', 'rom_preferences', 'section_groups']:
    (seed / name).mkdir()

names = {'gb': 'GAME BOY', 'gbc': 'GAME BOY COLOR', 'gba': 'GAME BOY ADVANCE',
         'snes': 'SNES', 'sfc': 'SNES', 'megadrive': 'SEGA GENESIS',
         'mastersystem': 'MASTER SYSTEM', 'gamegear': 'GAME GEAR',
         'pcengine': 'PC ENGINE', 'pcenginecd': 'PC ENGINE CD',
         'ngpc': 'NEO GEO POCKET COLOR', 'neogeocd': 'NEO GEO CD',
         'arcade': 'FINALBURN ALPHA', 'pokemini': 'POKEMON MINI',
         'lynx': 'ATARI LYNX', 'cpc': 'AMSTRAD CPC', 'zxspectrum': 'ZX SPECTRUM'}
handhelds = {'gb', 'gbc', 'gba', 'ngpc', 'wonderswan', 'pokemini', 'lynx', 'gamegear'}
computers = {'msx', 'amiga', 'atari800', 'cpc', 'zxspectrum'}
groups = {g: [] for g in ['arcades', 'consoles', 'handhelds', 'home computers']}
launchers = stage / 'simplemenu/launchers'
launchers.mkdir()
for system in systems:
    if not system.get('enabled') or not system.get('launch_profiles'):
        continue
    ident = system['id']
    group = ('handhelds' if ident in handhelds else 'home computers' if ident in computers
             else 'arcades' if ident in {'arcade', 'neogeo'} else 'consoles')
    section = names.get(ident, system['display_name'].upper())
    profiles = [('Default', None)] + [(p.replace(':', '_'), p) for p in system['launch_profiles']]
    assert len(profiles) <= 10, ident
    execs = []
    for label, profile in profiles:
        filename = ident + '__' + label
        script = launchers / filename
        command = [BASE + '/bin/plumos-text-ui', 'launch', ident]
        profile_arg = ' --profile ' + Q(profile) if profile else ''
        script.write_text('''#!/bin/sh
set -eu
root=${PLUMOS_ROOT:-/media/data/plumos}
sdcard=${PLUMOS_SDCARD_ROOT:-/media/data/sd2}
rom=$(readlink -f "$1")
case "$rom" in "$sdcard/roms/"*) relative=${rom#"$sdcard/roms/"} ;; *) exit 2 ;; esac
export PLUMOS_ROOT="$root" PLUMOS_SDCARD_ROOT="$sdcard"
''' + 'exec ' + ' '.join(map(Q, command)) + ' "$relative" --no-scan --execute' + profile_arg + '\n')
        script.chmod(0o755)
        execs.append(BASE + '/simplemenu/launchers/' + filename)
    # Scan real SD2 ROM directories, so new files appear without rebuilding a list.
    dirs = ['/media/data/sd2/roms/' + a['name'].strip('/') + '/' for a in system['directory_aliases']]
    exts = ['.' + e.lstrip('.') for e in system['extensions']]
    groups[group].append((section, '\n'.join(['[' + section + ']', 'execs = ' + ','.join(execs),
        'romDirs = ' + ','.join(dict.fromkeys(dirs)), 'romExts = ' + ','.join(exts)])))

for group, sections in groups.items():
    (seed / 'section_groups' / (group + '.ini')).write_text(
        '[CONSOLES]\nconsoleList = ' + ','.join(n for n, _ in sections) + '\n\n' +
        '\n\n'.join(text for _, text in sections) + '\n')
    shutil.copyfile(source / 'section_groups' / (group + '.png'),
                    seed / 'section_groups' / (group + '.png'))
# Initial selection: standard 0A, consoles/NES; existing user state/themes are preserved.
(seed / 'last_state.sav').write_text('10;\n1;\n0;\n1;\n1;\n0;\n0;\n1;\n0;\n3;\n')
(stage / 'bin').mkdir()
for name in ['plumos-simplemenu', 'plumos-simplemenu-invoker']:
    shutil.copyfile(ROOT / 'assets/frontend/bin' / name, stage / 'bin' / name)
    (stage / 'bin' / name).chmod(0o755)
archive = WORK / 'install.tar'
with tarfile.open(archive, 'w') as tar:
    for path in sorted(stage.iterdir()):
        tar.add(path, arcname=path.name)
subprocess.run(ADB + ['push', str(archive), BASE + '/simplemenu-install.tar'], check=True)
assert shell('sha256sum ' + BASE + '/simplemenu-install.tar').split()[0] == hashlib.sha256(archive.read_bytes()).hexdigest()
shell('set -e; tar -xf ' + BASE + '/simplemenu-install.tar -C ' + BASE + '; rm ' + BASE + '/simplemenu-install.tar')
shell('mkdir -p ' + BASE + '/home/simplemenu; if ! test -d ' + HOME + '; then cp -a ' +
      BASE + '/simplemenu/seed/.simplemenu ' + BASE + '/home/simplemenu/; fi')
apps = json.loads(shell('cat ' + BASE + '/config/frontend/apps.json'))
apps['apps'] = [a for a in apps['apps'] if not a['id'].startswith('rg350_') and a['id'] != 'simplemenu']
apps['apps'].append(dict(id='simplemenu', display_name='SimpleMenu', menu='apps',
                         kind='shell', visible=True, launch_profile='shell:' + BASE + '/bin/plumos-simplemenu'))
path = WORK / 'apps-simplemenu.json'
path.write_text(json.dumps(apps, ensure_ascii=False, indent=2) + '\n')
subprocess.run(ADB + ['push', str(path), BASE + '/config/frontend/apps.json.new'], check=True)
assert json.loads(shell('cat ' + BASE + '/config/frontend/apps.json.new')) == apps
shell('mv ' + BASE + '/config/frontend/apps.json.new ' + BASE + '/config/frontend/apps.json')
print('Installed SimpleMenu:', sum(len(v) for v in groups.values()), 'systems;', len(apps['apps']), 'configured apps')
