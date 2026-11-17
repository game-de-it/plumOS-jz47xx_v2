#!/usr/bin/env python3
"""Container-side packer for source-rebuilt OPKs; no production libraries replaced."""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
n = int(sys.argv[1])
p = json.loads((root / f'output/rg280v-apps/source-repair-profile-{n}.json').read_text())
work = root / 'output/rg280v-apps'
sdk = root / 'output/rg280v/host'
tools = sdk / 'bin'
catalog = json.loads((work / 'rg350-catalog/manifest.json').read_text())
stage = work / f'source-repair-stage-{n}'
# Recreate only this generated stage so removed profile libraries cannot linger.
if stage.exists():
    shutil.rmtree(stage)
subprocess.run([str(tools / 'unsquashfs'), '-f', '-no-progress', '-d', str(stage),
    str(work / 'rg350-catalog' / catalog[n-1]['name'])], stdout=subprocess.DEVNULL, check=True)
for obsolete in p.get('remove', []):
    old = stage / obsolete
    assert old.resolve().is_relative_to(stage.resolve()), obsolete
    if old.is_dir(): shutil.rmtree(old)
    else: old.unlink(missing_ok=True)
binary = work / 'source-repairs' / p['slug'] / p['binary']
shutil.copy2(binary, stage / 'plumos-emulator')
subprocess.run([str(tools / 'mipsel-gcw0-linux-uclibc-strip'), str(stage / 'plumos-emulator')], check=True)
abi = subprocess.check_output([str(tools / 'mipsel-gcw0-linux-uclibc-readelf'), '-A', str(stage / 'plumos-emulator')], text=True)
assert 'Soft float' in abi, abi
lib = stage / 'lib'
lib.mkdir(exist_ok=True)
for source, dest in [('libSDL_image.so', 'libSDL_image-1.2.so.0'), ('libpng16.so.16', 'libpng16.so.16')]:
    shutil.copy2(sdk / 'mipsel-gcw0-linux-uclibc/sysroot/usr/lib' / source, lib / dest)
for name in p.get('libraries', []):
    assert pathlib.PurePath(name).name == name
    shutil.copy2(sdk / 'mipsel-gcw0-linux-uclibc/sysroot/usr/lib' / name, lib / name)
wrapper = stage / 'plumos-repair.sh'
wrapper.write_text('#!/bin/sh\nset -eu\nexport HOME=/media/data/local/rg350-source-repairs/home-' + str(n) +
    '\nmkdir -p "$HOME"\nexport LD_LIBRARY_PATH=/opk/lib:${LD_LIBRARY_PATH:-/media/data/plumos/lib}\n' +
    p.get('prepare', '') + '\nset +e\n(\n' + p.get('exec', 'exec /opk/plumos-emulator "$@"') + '\n)\nrc=$?\necho PLUMOS_EMULATOR_EXIT=$rc\nexit \"$rc\"\n')
wrapper.chmod(0o755)
for desktop in stage.glob('*.desktop'):
    desktop.write_text(re.sub(r'^Exec=.*$', 'Exec=/bin/sh ./plumos-repair.sh %f', desktop.read_text(), flags=re.M))
out = work / 'source-repair-opks'
out.mkdir(exist_ok=True)
dest = out / f'{n:02d}.opk'
dest.unlink(missing_ok=True)
subprocess.run([str(tools / 'mksquashfs'), str(stage), str(dest), '-all-root', '-noappend', '-no-exports', '-comp', 'gzip', '-no-progress'], stdout=subprocess.DEVNULL, check=True)
meta = dict(number=n, source=p['url'], revision=p['revision'], sha256=hashlib.sha256(dest.read_bytes()).hexdigest(), bytes=dest.stat().st_size)
meta['binary_sha256'] = hashlib.sha256((stage / 'plumos-emulator').read_bytes()).hexdigest()
meta['build_command'] = p['build']
meta['dependencies'] = p.get('dependencies', [])
meta['libraries'] = p.get('libraries', [])
if p.get('patch'):
    meta['patch'] = p['patch']
    meta['patch_sha256'] = hashlib.sha256((root / p['patch']).read_bytes()).hexdigest()
(out / f'{n:02d}.json').write_text(json.dumps(meta, indent=2))
print(json.dumps(meta), flush=True)
