#!/usr/bin/env python3
"""Package accepted OPK binaries with production, arbitrary-ROM launchers."""
import hashlib
import json
import pathlib
import re
import subprocess
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORK = ROOT / 'output/rg280v-opk-integration'
SOURCES = json.loads((ROOT / 'assets/rg280v-apps/standalone-opk-routes.json').read_text())
BINARY = {'atari800':'atari800','fba44':'fbasdl.dge','temper':'temper',
 'fceux223':'fceux','genesisgx':'gen_gcw0','pokemini':'pokemini',
 'race':'race-gcw0.dge','crocods':'crocods','gambatte2020':'gambatte-dms.opendingux',
 'ohboy':'ohboy.gcw0','stella':'stella','neo4all':'neo4all.dge'}
for name in ('handy','oswan','smsplusgg','smsplusms','unrealspeccy','gngeo','uae4all'):
    BINARY[name] = 'plumos-emulator'
TOOLS = ROOT / 'output/rg280v/host/bin'
OUT = WORK / 'packages'
OUT.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only', nargs='+')
args = parser.parse_args()
records = json.loads((WORK/'package-manifest.json').read_text()) if args.only else []

for route in SOURCES:
    slug, source = route["id"], route["source"]
    if args.only and slug not in args.only: continue
    records = [r for r in records if r["id"] != slug]
    stage = WORK / 'stages' / slug
    source = ROOT / source
    assert hashlib.sha256(source.read_bytes()).hexdigest() == route['source_sha256'], slug
    if stage.exists():
        import shutil
        shutil.rmtree(stage)
    stage.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(TOOLS/'unsquashfs'),'-f','-no-progress','-d',str(stage),str(source)],
                   check=True, stdout=subprocess.DEVNULL)
    binary = stage / BINARY[slug]
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    # Stages are extracted once from the exact accepted packages. Never rebuild ELF.
    body = 'exec /opk/' + BINARY[slug] + ' "$@"'
    prepare = ''
    if slug == 'unrealspeccy':
        prepare = 'mkdir -p "$HOME/states"\n'
    elif slug == 'pokemini':
        prepare = 'mkdir -p "$HOME/saves"\n'
        body = 'exec /opk/pokemini -eeprom "$HOME/saves/$(basename "$1").eep" -eepromshare -state "$HOME/saves/$(basename "$1").sta" "$1"'
    elif slug == 'gambatte2020':
        body = 'exec /opk/gambatte-dms.opendingux --resampler 0 "$@"'
    elif slug == 'stella':
        prepare = """case "$(cat /sys/class/graphics/fb0/virtual_size 2>/dev/null)" in
    640,*) set -- -maxres 320x240 "$@" ;;
esac
"""
    elif slug == 'gngeo':
        prepare = 'mkdir -p "$HOME/roms"\nln -sfn "$root/bios/standalone/gngeo/neogeo.zip" "$HOME/roms/neogeo.zip"\nln -sfn "$1" "$HOME/roms/$(basename "$1")"\n'
        body = 'exec /opk/plumos-emulator --biospath="$root/bios/standalone/gngeo" --rompath="$HOME/roms" "$1"'
    elif slug == 'uae4all':
        prepare = 'mkdir -p "$HOME/.uae4all"\nln -sfn "$root/bios/standalone/uae4all/kick.rom" "$HOME/.uae4all/kick.rom"\n'
    elif slug == 'neo4all':
        prepare = 'mkdir -p "$HOME/.neo4all"\nln -sfn "$root/bios/standalone/neo4all/neocd.bin" "$HOME/.neo4all/neocd.bin"\n'
    wrapper = stage / 'plumos-production.sh'
    wrapper.write_text('''#!/bin/sh
set -eu
root=${PLUMOS_ROOT:-/media/data/plumos}
export HOME="${PLUMOS_OPK_HOME:-$root/home/opk/''' + slug + '''}"
mkdir -p "$HOME"
export LD_LIBRARY_PATH="/opk/lib:$root/lib/opk-compat:$root/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
''' + prepare + '''set +e
(
''' + body + '''
)
rc=$?
echo PLUMOS_EMULATOR_EXIT=$rc
exit "$rc"
''')
    wrapper.chmod(0o755)
    # opkrun's desktop ordering must not select RetroFW/Lepus/no-ROM variants.
    for desktop in stage.glob('*.desktop'):
        desktop.write_text(re.sub(r'^Exec=.*$', 'Exec=/bin/sh ./plumos-production.sh %f',
                                 desktop.read_text(), flags=re.M))
    dest = OUT / (slug + '.opk')
    dest.unlink(missing_ok=True)
    subprocess.run([str(TOOLS/'mksquashfs'),str(stage),str(dest),'-all-root','-noappend',
                    '-no-exports','-comp','gzip','-no-progress'],check=True,stdout=subprocess.DEVNULL)
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == digest
    records.append(dict(id=slug, source=str(source.relative_to(ROOT)),
                        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        binary=BINARY[slug], binary_sha256=digest,
                        sha256=hashlib.sha256(dest.read_bytes()).hexdigest(), bytes=dest.stat().st_size))
(WORK/'package-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print('Packaged',len(records),'accepted binaries; ELF bytes unchanged')
