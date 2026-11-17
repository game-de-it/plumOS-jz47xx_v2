#!/usr/bin/env python3
"""Prepare isolated launchers with ROM arguments for the missing-ROM retest."""
import json,pathlib,subprocess,tempfile,re,sys
r=pathlib.Path(__file__).resolve().parents[1];out=r/'output/rg280v-apps/missing-rom-opks';out.mkdir(exist_ok=True)
configs={1:'exec ./3doh "$1"',6:'exec ./dcastaway "$1"',7:'exec ./dosbox -conf "$1"',10:'exec ./run.sh "$1"',15:'exec ./neo4all "$1"',17:'mkdir -p "$home/runtime/Paks"\nln -sf "$1" "$home/runtime/Paks/test.pak"\ncd "$home/runtime"\nexec /opk/OpenBOR',22:'cd "$(dirname "$1")"\nexec /opk/potator-gcw0.dge "$1"',32:'exec ./xmame/xmame69/xmame.SDL.69 -rompath="$(dirname "$1")" "$(basename "$1" .zip)"',30:'exec ./uae4all.dge "$1"',31:'exec ./sdlvice.sh "$1"',39:'exec ./gngeo.dge --biospath="$home/bios" --rompath="$(dirname "$1")" "$(basename "$1" .zip)"',42:'exec ./jzintv -e "$home/bios/exec.bin" -g "$home/bios/grom.bin" "$1"',47:'exec ./mednafen -force_module pcfx "$1"',50:'exec ./openmsx -machine C-BIOS_MSX2 -cart "$1"',56:'case "$1" in *BASS*) game=sky ;; *Monkey*) game=monkey2 ;; *) game=baseball ;; esac\nexport LD_LIBRARY_PATH=/opk:${LD_LIBRARY_PATH:-}\nexec ./scummvm --extrapath=/opk/engine-data --themepath=/opk/themes --config="$home/scummvmrc" --music-driver=adlib --path="$1" --fullscreen "$game"',60:'exec ./uae4all.dge "$1"'}
for n,body in configs.items():
 home=f'/media/data/local/rg350-missing-rom-retest/home-{n:02d}'
 (out/f'{n:02d}.sh').write_text('#!/bin/sh\nset -eu\nhome='+home+'\nmkdir -p "$home"\nexport HOME="$home"\n'+body+'\n')
(out/'numbers.json').write_text(json.dumps(list(configs)))

if '--pack' in sys.argv:
 cat=json.loads((r/'output/rg280v-apps/rg350-catalog/manifest.json').read_text())
 tools=r/'output/rg280v/host/bin'
 for n in configs:
  with tempfile.TemporaryDirectory() as t:
   subprocess.run([str(tools/'unsquashfs'),'-no-progress','-d',t,str(r/'output/rg280v-apps/rg350-catalog'/cat[n-1]['name'])],stdout=subprocess.DEVNULL,check=True)
   stage=pathlib.Path(t);wrapper=stage/'rom-retest.sh';wrapper.write_bytes((out/f'{n:02d}.sh').read_bytes());wrapper.chmod(0o755)
   for desktop in stage.rglob('*.desktop'):
    desktop.write_text(re.sub(r'^Exec=.*$','Exec=/bin/sh ./rom-retest.sh %f',desktop.read_text(),flags=re.M))
   dest=out/f'{n:02d}.opk';dest.unlink(missing_ok=True)
   subprocess.run([str(tools/'mksquashfs'),t,str(dest),'-all-root','-noappend','-no-exports','-comp','gzip','-no-progress'],stdout=subprocess.DEVNULL,check=True)
 print('prepared',len(configs))
