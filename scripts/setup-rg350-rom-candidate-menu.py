#!/usr/bin/env python3
"""Expose three-ROM visual comparisons for the >=50 FPS OPK candidates."""
import hashlib,json,pathlib,shlex,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
BASE='/media/data/local/rg350-rom-candidates'
CATALOG=json.loads((ROOT/'output/rg280v-apps/rg350-catalog-audit.json').read_text())
GROUPS=json.loads((ROOT/'output/rg280v-apps/rg350-rom-candidates.json').read_text())
# Catalog 20 PocketSNES and 36 Gambatte 2021 share the active SA binaries.
LABELS={11:'FCEUX 2.2.3',12:'GenesisGX',21:'PokeMini',24:'Race Explorer',33:'CrocoDS',35:'Gambatte 2020',37:'Gambatte r572u3 GB',38:'Gambatte r572u3 GBC',49:'OhBoy'}
def shell(s): return subprocess.check_output(ADB+['shell',s],text=True).strip()
def push(p,d):
 shell('mkdir -p '+shlex.quote(str(pathlib.PurePosixPath(d).parent)))
 subprocess.run(ADB+['push',str(p),d],capture_output=True,check=True)
 assert shell('sha256sum '+shlex.quote(d)).split()[0]==hashlib.sha256(p.read_bytes()).hexdigest()
apps_path='/media/data/plumos/config/frontend/apps.json'
apps=json.loads(shell('cat '+apps_path))
out=ROOT/'output/rg280v-apps/rom-candidate-stage';out.mkdir(parents=True,exist_ok=True)
backup=out/'apps-before-rom-menu.json'
if not backup.exists():backup.write_text(json.dumps(apps,ensure_ascii=False,indent=2))
new=[];cases=[]
for number,label in LABELS.items():
 group=next(g for g in GROUPS if number in g['catalog_numbers'])
 opk=BASE+f'/opk/{number:02d}.opk'
 source=ROOT/'output/rg280v-apps/rg350-catalog'/CATALOG[number-1]['name']
 if number in (12,49): source=ROOT/f'output/rg280v-apps/rg350-audio-fixed-{number}.opk'
 push(source,opk)
 for index,rom in enumerate(group['candidates'],1):
  if not rom['remote']:continue
  ident=f'rg350_romtest_{number:02d}_{index}'
  title=rom['title']
  cases.append(f'    {ident}) opk={shlex.quote(opk)}; rom={shlex.quote(rom["remote"])} ;;')
  new.append(dict(id=ident,display_name=f'TEST {number:02d} {label} {index}: {title}',menu='apps',kind='shell',visible=True,launch_profile=f'shell:{BASE}/run {ident}'))
wrapper='''#!/bin/sh
set -eu
case "${1:-}" in
'''+ '\n'.join(cases)+'''
    *) exit 2 ;;
esac
root=/media/data/plumos
"$root/bin/plumos-prepare-opk-input"
export HOME="$root/home" PLUMOS_ROOT="$root" SDL_VIDEODRIVER=kmsdrm
export LD_LIBRARY_PATH="$root/lib"
mkdir -p /media/data/local/rg350-rom-candidates/log
/usr/bin/opkrun "$opk" "$rom" >"/media/data/local/rg350-rom-candidates/log/$1.log" 2>&1
'''
p=out/'run';p.write_text(wrapper);push(p,BASE+'/run');shell('chmod 755 '+BASE+'/run')
apps['apps']=[a for a in apps['apps'] if not a.get('id','').startswith('rg350_romtest_')]+new
p=out/'apps-rom-menu.json';p.write_text(json.dumps(apps,ensure_ascii=False,indent=2)+'\n')
push(p,apps_path+'.tmp');shell('mv '+apps_path+'.tmp '+apps_path)
assert json.loads(shell('cat '+apps_path))==apps
print('Verified menu entries:',len(new))
