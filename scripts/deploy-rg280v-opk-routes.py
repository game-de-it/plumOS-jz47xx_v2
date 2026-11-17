#!/usr/bin/env python3
"""Install accepted OPK routes, preserve settings, and stage verified SD2 samples."""
import hashlib
import json
import pathlib
import shlex
import subprocess
import time
import sys
sys.dont_write_bytecode = True
import importlib.util
spec=importlib.util.spec_from_file_location('opk_systems',pathlib.Path(__file__).with_name('register-rg280v-opk-systems.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
merge=module.merge

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'output/rg280v-opk-integration'
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
BASE='/media/data/plumos'
SD='/media/data/sd2'
Q=shlex.quote

def shell(command):
    return subprocess.check_output(ADB+['shell',command],text=True,errors='replace').strip()
def digest(path):
    return shell('sha256sum '+Q(path)).split()[0]
def push(source,dest,mode='0644'):
    expected=hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest()
    shell('mkdir -p '+Q(str(pathlib.PurePosixPath(dest).parent)))
    subprocess.run(ADB+['push',str(source),dest+'.new'],check=True,capture_output=True)
    assert digest(dest+'.new')==expected,dest
    shell('mv '+Q(dest+'.new')+' '+Q(dest)+' && chmod '+mode+' '+Q(dest))
    return expected

def sd_copy(source,target):
    expected=digest(source)
    if shell('test -f '+Q(target)+' && echo yes')=='yes':
        assert digest(target)==expected,('existing file differs; preserved',target)
    else:
        shell('mkdir -p '+Q(str(pathlib.PurePosixPath(target).parent)))
        shell('cp '+Q(source)+' '+Q(target+'.new')+' && mv '+Q(target+'.new')+' '+Q(target))
        assert digest(target)==expected,target
    return dict(source=source,target=target,sha256=expected)

subprocess.run(['adb','-P','5041','connect','10.1.1.2:5555'],check=True)
records=json.loads((OUT/'package-manifest.json').read_text())
assert len(records)==19
assert not shell("ps | busybox grep '/opk/' | busybox grep -v grep"),'An OPK is running'
free=int(shell('df -k '+BASE).splitlines()[-1].split()[3])*1024
assert free > sum(x['bytes'] for x in records)+16*1024**2,free
stamp=time.strftime('%Y%m%d-%H%M%S')
backup=BASE+'/backup/opk-integration-'+stamp
shell('mkdir -p '+Q(backup))
shell('cp -p /media/data/local/init.d/S95frontend '+Q(backup+'/S95frontend'))
for relative in ['config/frontend/systems.json','state/frontend/core-overrides.json',
                 'state/frontend/library-index.json','bin/plumos-controller-ui','bin/plumos-text-ui',
                 'bin/plumos-standalone-launch']:
    shell('if test -f '+Q(BASE+'/'+relative)+'; then cp -p '+Q(BASE+'/'+relative)+' '+Q(backup+'/'+relative.replace('/','_'))+'; fi')
before=json.loads(shell('cat '+BASE+'/config/frontend/systems.json'))
(OUT/('before-systems-'+stamp+'.json')).write_text(json.dumps(before,indent=2))
merged=merge(before)
config=OUT/'device-systems.json';config.write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n')

# Use the original private compatibility libraries, never replace global SDL/ALSA.
compat=OUT/'compat';compat.mkdir(exist_ok=True)
for name in ['libao.so.4','libcrypto.so.1.0.0','libncurses.so.5','libncursesw.so','libreadline.so.6']:
    subprocess.run(ADB+['pull','/media/data/local/rg350-visual-tests/lib/'+name,str(compat/name)],check=True,capture_output=True)
    push(compat/name,BASE+'/lib/opk-compat/'+name)
for record in sorted(records,key=lambda r:-r['bytes']):
    package=OUT/'packages'/(record['id']+'.opk')
    assert hashlib.sha256(package.read_bytes()).hexdigest()==record['sha256']
    push(package,BASE+'/emulators/opk/'+package.name)
    print('Installed',record['id'],flush=True)

migrate={'atari800':['.atari800.cfg'],'fba44':['.fba'],'temper':['.temper'],
 'fceux223':['.fceux'],'genesisgx':['.genplus'],'pokemini':['.pokemini.cfg'],
 'race':['.race-od'],'crocods':['.crocods'],'gambatte2020':['.gambatte'],
 'ohboy':['.ohboy'],'stella':['.stella']}
private={'handy':13,'oswan':18,'smsplusgg':57,'smsplusms':58,'unrealspeccy':61,'gngeo':39,'uae4all':30}
for record in records:
    slug=record['id'];dest=BASE+'/home/opk/'+slug
    if shell('test -d '+Q(dest)+' && echo yes')=='yes':continue
    shell('mkdir -p '+Q(dest))
    if slug in private:
        source='/media/data/local/rg350-source-repairs/home-'+str(private[slug])
        shell('cp -a '+Q(source+'/.')+' '+Q(dest+'/'))
    elif slug=='fceux223':
        # 2.6.6 ROM profiles can crash 2.2.3 during video initialization.
        shell('mkdir -p '+Q(dest+'/.fceux'))
        for part in ['fcs','sav','cheats','gameinfo','movie','movies','snaps']:
            source=BASE+'/home/.fceux/'+part
            shell('if test -d '+Q(source)+'; then cp -a '+Q(source)+' '+Q(dest+'/.fceux/')+'; fi')
    elif slug=='neo4all':
        shell('cp -a /media/data/local/rg350-missing-rom-retest/home-15/. '+Q(dest+'/'))
    else:
        for entry in migrate[slug]:
            source=BASE+'/home/'+entry
            shell('if test -e '+Q(source)+'; then cp -a '+Q(source)+' '+Q(dest+'/')+'; fi')

# Game and BIOS payloads remain on SD2. Refuse to overwrite different user data.
mount=next(line for line in shell('cat /proc/mounts').splitlines() if line.split()[1]==SD)
assert mount.split()[0]=='/dev/mmcblk1p1',mount
was_ro='ro' in mount.split()[3].split(',')
verified=[]
try:
    if was_ro:shell('mount -o remount,rw '+SD)
    old=SD+'/.plumos-rg350-tests-20261118/relocated'
    groups=json.loads((ROOT/'output/rg280v-apps/rg350-rom-candidates.json').read_text())
    for family in ['cpc','pokemini','lynx','ngpc']:
        group=next(g for g in groups if g['family']==family)
        for rom in group['candidates']:
            name=rom['title'].replace('/','-')+pathlib.PurePosixPath(rom['remote']).suffix
            verified.append(sd_copy(rom['remote'],SD+'/roms/'+family+'/'+name))
    for name in ['CavernsOfMars.car','Miner2049er.car','FoodFight.rom']:
        verified.append(sd_copy(old+'/visual-roms/atari/'+name,SD+'/roms/atari800/'+name))
    for i,name in [(4,'Asteroids'),(5,'Centipede'),(6,'Breakout')]:
        verified.append(sd_copy(old+f'/rom-candidates/atari2600/0{i}.bin',SD+'/roms/atari2600/'+name+'.bin'))
    verified.append(sd_copy(old+'/rom-candidates/zx/01.tap',SD+'/roms/zxspectrum/10th Frame.tap'))
    verified.append(sd_copy(old+'/rom-candidates/amiga/02.adf',SD+'/roms/amiga/Baby Jo.adf'))
    for game in ['aof','aof2','aof3']:
        verified.append(sd_copy(old+'/extra-roms/neogeo/'+game+'.zip',SD+'/roms/neogeo/'+game+'.zip'))
    verified.append(sd_copy(old+'/visual-roms/fba/kungfum.zip',SD+'/roms/arcade/kungfum.zip'))
    for slug,name,source in [('gngeo','neogeo.zip',old+'/extra-roms/neogeo/neogeo.zip'),
                             ('uae4all','kick.rom',old+'/bios/home-30/.uae4all/kick.rom'),
                             ('neo4all','neocd.bin',old+'/bios/home-15/.neo4all/neocd.bin')]:
        dest=SD+'/bios/opk/'+slug+'/'+name
        verified.append(sd_copy(source,dest))
        shell('mkdir -p '+Q(BASE+'/bios/standalone/'+slug)+' && ln -sfn '+Q(dest)+' '+Q(BASE+'/bios/standalone/'+slug+'/'+name))
    # Keep track files out of the FE list and expose a single portable playlist.
    source=SD+'/.plumos-rg350-tests-20261118/Fatal Fury WAV'
    dest=SD+'/roms/neogeocd/.discs/Fatal Fury'
    listing=shell('find '+Q(source)+' -type f')
    for file in listing.splitlines():
        verified.append(sd_copy(file,dest+'/'+file[len(source)+1:]))
    playlist=OUT/'Fatal Fury.m3u';playlist.write_text('.discs/Fatal Fury/Fatal Fury.iso\n')
    push(playlist,SD+'/roms/neogeocd/Fatal Fury.m3u')
finally:
    shell('sync')
    if was_ro:shell('mount -o remount,ro '+SD)
(OUT/'sd2-copies.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n')

# Preserve the accepted Unreal input mapping and saved gameplay under its new ROM path.
home=BASE+'/home/opk/unrealspeccy'
oldrom=SD+'/.plumos-rg350-tests-20261118/relocated/rom-candidates/zx/01.tap'
newrom=SD+'/roms/zxspectrum/10th Frame.tap'
def fnv(s):
    h=2166136261
    for c in s.encode():h=((h^c)*16777619)&0xffffffff
    return f'{h:08x}'
source=home+'/states/'+fnv(oldrom)+'.sna';dest=home+'/states/'+fnv(newrom)+'.sna'
shell('if test -f '+Q(source)+' && ! test -e '+Q(dest)+'; then cp -p '+Q(source)+' '+Q(dest)+'; fi')
xml=shell('cat '+Q(home+'/unreal_speccy_portable.xml')).replace(oldrom,newrom)
p=OUT/'unreal_speccy_portable.xml';p.write_text(xml+'\n');push(p,home+'/unreal_speccy_portable.xml')

# Commit the UI/config update only after all runtime assets are ready.
shell('/media/data/local/init.d/S95frontend stop')
try:
    service=shell('cat /media/data/local/init.d/S95frontend')
    service=service.replace('nohup "$root/bin/plumos-fe-launch"', 'nohup setsid "$root/bin/plumos-fe-launch"')
    service_file=OUT/'S95frontend-detached';service_file.write_text(service+'\n')
    push(service_file,'/media/data/local/init.d/S95frontend','0755')
    for name in ['plumos-controller-ui','plumos-text-ui']:
        push(ROOT/'output/rg280v-fe'/name,BASE+'/bin/'+name,'0755')
    for default in (ROOT/'assets/frontend/standalone-defaults').iterdir():
        push(default,BASE+'/config/standalone/'+default.name)
    for name in ['plumos-standalone-launch','plumos-opk-emulator-launch']:
        push(ROOT/'assets/frontend/bin'/name,BASE+'/bin/'+name,'0755')
    for icon in json.loads((ROOT/'assets/frontend/logos/opk-system-icons.json').read_text())['icons']:
        push(ROOT/'assets/frontend/logos/systems'/icon['file'],BASE+'/themes/default/logos/systems/'+icon['file'])
    push(config,BASE+'/config/frontend/systems.json')
    assert json.loads(shell('cat '+BASE+'/config/frontend/systems.json'))==merged
    shell('PLUMOS_ROOT='+BASE+' PLUMOS_SDCARD_ROOT='+SD+' '+BASE+'/bin/plumos-library-scan >'+BASE+'/Logs/opk-integration-scan.log 2>&1')
finally:
    shell('/media/data/local/init.d/S95frontend start')
print('Registered',len(records),'OPK packages; backup:',backup)
(OUT/'deployment.json').write_text(json.dumps(dict(backup=backup,records=records,rom_files=len(verified)),indent=2)+'\n')
