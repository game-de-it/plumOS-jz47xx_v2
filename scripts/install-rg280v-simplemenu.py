#!/usr/bin/env python3
"""Install SimpleMenu with existing FE launch profiles and locally fetched themes."""
import hashlib
import argparse
import configparser
import json
import pathlib
import shlex
import shutil
import subprocess
import tarfile
import time
from simplemenu_section_layout import migrate_state

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT / 'output/rg280v-simplemenu'
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/plumos'
HOME = BASE + '/home/simplemenu/.simplemenu'
Q = shlex.quote
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--refresh-sections', action='store_true',
                    help='Update installed section order while preserving the selected system by name')
args = parser.parse_args()


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
for theme in ['SimpleQuest', 'SimpleQuest2']:
    # Private device installation only: the author's theme is not redistributed.
    shutil.copytree(WORK / 'themes' / theme, seed / 'themes/320x240' / theme)

config = (source / 'config/config.ini').read_text()
config = config.replace('[SCREEN]', '[SCREEN]\nscreen_width = 320\nscreen_height = 240')
for old in ['underclocked_speed = 444', 'overclocked_speed = 1092', 'sleep_speed = 444']:
    config = config.replace(old, old.split(' = ')[0] + ' = 996')
(seed / 'config.ini').write_text(config + '\n')
(seed / 'favorites.sav').write_text('')
for name in ['apps', 'games', 'tmp', 'rom_preferences', 'section_groups']:
    (seed / name).mkdir()

layout_document = json.loads((ROOT / 'assets/rg280v-simplemenu/system-order.json').read_text())
names = layout_document['section_names']
handhelds = {'gb', 'gbc', 'gba', 'ngpc', 'wonderswan', 'pokemini', 'lynx', 'gamegear'}
computers = {'msx', 'amiga', 'atari800', 'cpc', 'zxspectrum'}
groups = {g: [] for g in ['arcades', 'consoles', 'handhelds', 'home computers']}
layout = layout_document['groups']
section_ids = {}
launchers = stage / 'simplemenu/launchers'
launchers.mkdir()
for system in systems:
    if not system.get('enabled') or not system.get('launch_profiles'):
        continue
    ident = system['id']
    group = next((g for g, ids in layout.items() if ident in ids), None)
    if group is None:
        group = ('handhelds' if ident in handhelds else 'home computers' if ident in computers
                 else 'arcades' if ident == 'arcade' else 'consoles')
    section = names.get(ident, system['display_name'].upper())
    section_ids[section] = ident
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
    rank = {ident: i for i, ident in enumerate(layout[group])}
    sections.sort(key=lambda item: rank.get(section_ids[item[0]], 1000))
    (seed / 'section_groups' / (group + '.ini')).write_text(
        '[CONSOLES]\nconsoleList = ' + ','.join(n for n, _ in sections) + '\n\n' +
        '\n\n'.join(text for _, text in sections) + '\n')
    shutil.copyfile(source / 'section_groups' / (group + '.png'),
                    seed / 'section_groups' / (group + '.png'))
# Initial selection: SimpleQuest, consoles/NES; subsequent user state is preserved.
(seed / 'last_state.sav').write_text('10;\n1;\n0;\n1;\n1;\n1;\n0;\n1;\n0;\n3;\n')
if args.refresh_sections:
    old_groups = {}
    for group in groups:
        old_config = configparser.ConfigParser(interpolation=None)
        old_config.read_string(shell('cat ' + Q(HOME + '/section_groups/' + group + '.ini')))
        old_groups[group] = [n.strip() for n in old_config['CONSOLES']['consoleList'].split(',')]
    old_state = shell('cat ' + Q(HOME + '/last_state.sav'))
    new_groups = {g: [name for name, _ in rows] for g, rows in groups.items()}
    migrated = migrate_state(old_state, old_groups, new_groups)
    (WORK / 'state-before-layout.sav').write_text(old_state + '\n')
    (WORK / 'state-after-layout.sav').write_text(migrated)
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
if args.refresh_sections:
    backup = BASE + '/backup/simplemenu-layout-' + time.strftime('%Y%m%d-%H%M%S')
    shell('mkdir -p ' + Q(backup) + '; cp -a ' + Q(HOME + '/section_groups') + ' ' + Q(backup) +
          '; cp -p ' + Q(HOME + '/last_state.sav') + ' ' + Q(backup))
    subprocess.run(ADB + ['push', str(WORK / 'state-after-layout.sav'), HOME + '/last_state.sav.new'], check=True)
    shell('set -e; cp ' + Q(BASE + '/simplemenu/seed/.simplemenu/section_groups') + '/*.ini ' +
          Q(HOME + '/section_groups/') + '; mv ' + Q(HOME + '/last_state.sav.new') + ' ' + Q(HOME + '/last_state.sav'))
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
