#!/usr/bin/env python3
"""Install the project-owned Amber skin and its matching 350teric renderer."""
import hashlib
import pathlib
import shutil
import subprocess
import tarfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT / 'output/rg280v-350teric'
BASE = '/media/data/plumos'
HOME = BASE + '/home/350teric/.esoteric'
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']


def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True).strip()


if shell('pidof esoteric || true'):
    raise SystemExit('Exit 350teric before installing its renderer')
if shell('test -f ' + HOME + '/esoteric.conf && echo yes') != 'yes':
    raise SystemExit('Install the standard 350teric runtime first')
if int(shell('df -k ' + BASE).splitlines()[-1].split()[3]) < 10000:
    raise SystemExit('Installation requires 10 MiB of free SD1 space')
stage = WORK / 'amber-install'
if stage.exists():
    shutil.rmtree(stage)
(stage / '350teric').mkdir(parents=True)
shutil.copyfile(WORK / 'runtime/esoteric', stage / '350teric/esoteric.new')
(stage / '350teric/esoteric.new').chmod(0o755)
shutil.copytree(ROOT / 'assets/rg280v-350teric/skins/Amber', stage / 'Amber')
archive = WORK / 'amber-install.tar'
with tarfile.open(archive, 'w') as tar:
    for path in stage.iterdir():
        tar.add(path, arcname=path.name)
remote = BASE + '/350teric-amber.tar'
subprocess.run(ADB + ['push', str(archive), remote], check=True)
assert shell('sha256sum ' + remote).split()[0] == hashlib.sha256(archive.read_bytes()).hexdigest()
backup = BASE + '/backup/350teric-amber-' + time.strftime('%Y%m%d-%H%M%S')
shell('set -e; mkdir -p ' + backup + '; cp -p ' + BASE + '/350teric/esoteric ' + backup + '/; '
      'cp -p ' + HOME + '/esoteric.conf ' + backup + '/; '
      'if test -d ' + HOME + '/skins/Amber; then cp -a ' + HOME + '/skins/Amber ' + backup + '/; fi; '
      'mkdir -p ' + BASE + '/350teric/amber-stage; tar -xf ' + remote + ' -C ' + BASE + '/350teric/amber-stage; '
      'cp -a ' + BASE + '/350teric/amber-stage/Amber ' + HOME + '/skins/; '
      'mv ' + BASE + '/350teric/amber-stage/350teric/esoteric.new ' + BASE + '/350teric/esoteric; '
      'rm -rf ' + BASE + '/350teric/amber-stage; rm ' + remote)
expected = hashlib.sha256((WORK / 'runtime/esoteric').read_bytes()).hexdigest()
assert shell('sha256sum ' + BASE + '/350teric/esoteric').split()[0] == expected
print('Installed Amber and renderer:', expected)
print('Current skin setting retained. Backup:', backup)
