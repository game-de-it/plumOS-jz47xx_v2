#!/usr/bin/env python3
"""Add four externally sourced 350teric skins without replacing user settings."""
import hashlib
import json
import pathlib
import shutil
import subprocess
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT / 'output/rg280v-350teric'
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
HOME = '/media/data/plumos/home/350teric/.esoteric'
SOURCES = {
    'skin-pack': ('https://github.com/m1024x/retrogame-skin-pack.git',
                  'f7686404fbe137c17281c2545c22cfe311e04a4c'),
    'skin-flat': ('https://github.com/peeweek/gmenu2x-skin-flat.git',
                  'e613a6b677ae4c6f74b6135b777005ede2b0a041'),
}
CHOICES = {'OldBoy': ('skin-pack', 'OldBoy'),
           'PSNextDark': ('skin-pack', 'PSNextDark'),
           'Zelda': ('skin-pack', 'Zelda'),
           'Flat': ('skin-flat', 'flat')}


def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True).strip()


WORK.mkdir(parents=True, exist_ok=True)
for folder, (url, revision) in SOURCES.items():
    source = WORK / folder
    if not (source / '.git').exists():
        subprocess.run(['git', 'clone', url, str(source)], check=True)
        subprocess.run(['git', '-C', str(source), 'checkout', '--detach', revision], check=True)
    actual = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != revision:
        raise SystemExit('Unexpected skin source revision: ' + folder)

stage = WORK / 'skin-install'
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir()
allowed = {line.split('name == "', 1)[1].split('"', 1)[0] for line in
           (WORK / 'source/src/skin.cpp').read_text().splitlines() if 'name == "' in line}
manifest = {}
for name, (folder, upstream_name) in CHOICES.items():
    source = WORK / folder
    target = stage / name
    shutil.copytree(source / upstream_name, target)
    original = (target / 'skin.conf').read_text()
    (target / 'skin.conf.upstream').write_text(original)
    settings = {}
    for line in original.splitlines():
        if '=' not in line or line.lstrip().startswith('#'):
            continue
        key, value = (part.strip() for part in line.split('=', 1))
        key = key.lower()
        if key in allowed and (key != 'font' or value.startswith('#')):
            settings[key] = value
    # A full CJK font already ships with 350teric. Keep upstream fonts for reference,
    # while inheriting the common font so Japanese ROM names remain readable.
    if (target / 'font.ttf').exists():
        (target / 'font.ttf').rename(target / 'font-upstream.ttf')
    settings.update(fontsize='12', fontsizetitle='14', fontsizesectiontitle='12',
                    linkrows='6', linkcols='1', sectionbar='1', sectiontitlebarsize='40',
                    menutitlebarheight='40', menuinfobarheight='20', linkdisplaymode='0',
                    showloader='0', showsectionicons='1')
    if name == 'Flat':
        settings.update(font='#ffffffff', fontalt='#ffffffff')
    if name == 'Zelda':
        settings['fontoutline'] = '#000000c8'
    (target / 'skin.conf').write_text('# 350teric RG280V compatibility settings; upstream copy alongside.\n' +
                                      '\n'.join(k + '=' + v for k, v in settings.items()) + '\n')
    for notice in ['README.md', 'LICENSE.md', '3DRPARTY-LICENSE.md']:
        if (source / notice).exists():
            shutil.copyfile(source / notice, target / ('SOURCE-' + notice))
    metadata = dict(repository=SOURCES[folder][0], revision=SOURCES[folder][1],
                    directory=upstream_name, common_font=True, resolution=[320, 240])
    (target / 'plumos-source.json').write_text(json.dumps(metadata, indent=2) + '\n')
    manifest[name] = metadata

if shell('test -f ' + HOME + '/esoteric.conf && echo yes') != 'yes':
    raise SystemExit('Install 350teric first')
if int(shell('df -k /media/data').splitlines()[-1].split()[3]) < 30000:
    raise SystemExit('At least 30 MiB free SD1 space is required')
config_before = shell('sha256sum ' + HOME + '/esoteric.conf').split()[0]
# Existing external skins, including user edits, are left intact on reinstallation.
names = [name for name in CHOICES if shell('test -d ' + HOME + '/skins/' + name +
                                          ' && echo exists || true') != 'exists']
archive = WORK / 'skin-install.tar'
with tarfile.open(archive, 'w') as tar:
    for name in names:
        tar.add(stage / name, arcname=name)
remote = '/media/data/plumos/350teric-skins.tar'
subprocess.run(ADB + ['push', str(archive), remote], check=True)
assert shell('sha256sum ' + remote).split()[0] == hashlib.sha256(archive.read_bytes()).hexdigest()
shell('set -e; tar -xf ' + remote + ' -C ' + HOME + '/skins; rm ' + remote)
assert shell('sha256sum ' + HOME + '/esoteric.conf').split()[0] == config_before
(WORK / 'skins-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Installed:', ', '.join(names) or '(all already installed; retained existing copies)')
print('Current skin and user configuration preserved.')
