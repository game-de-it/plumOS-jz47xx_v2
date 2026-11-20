#!/usr/bin/env python3
"""Install original Esoteric 1.0.12 UI, using the registered plumOS ROM routes."""
import hashlib,json,pathlib,re,shlex,shutil,subprocess,tarfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORK=ROOT/'output/rg280v-350teric'
BASE='/media/data/plumos'
HOME=BASE+'/home/350teric/.esoteric'
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
LEGACY_FONT_SHA256 = 'db5b86c44b31406e306cd3dde23ff4b44722c3ce7061a313915229d6d88a2ac6'
Q=shlex.quote
def shell(s): return subprocess.check_output(ADB+['shell',s],text=True).strip()
if shell("pidof esoteric || true"): raise SystemExit('350teric is running')
if int(shell('df -k '+BASE).splitlines()[-1].split()[3]) < 40000: raise SystemExit('SD1 requires 40 MiB free')
systems=json.loads(shell('cat '+BASE+'/config/frontend/systems.json'))['systems']
stage=WORK/'install'
if stage.exists(): shutil.rmtree(stage)
shutil.copytree(WORK/'runtime',stage/'350teric')
seed=stage/'350teric/seed/.esoteric'
seed.mkdir(parents=True)
source=WORK/'source'
for d in ['skins','translations','input']: shutil.copytree(source/'assets'/d,seed/d)
project_skins=ROOT/'assets/rg280v-350teric/skins'
if project_skins.exists():
 for skin in project_skins.iterdir():
  if skin.is_dir():shutil.copytree(skin,seed/'skins'/skin.name)
for d in ['applications','emulators','settings','favorites']:(seed/'sections'/d).mkdir(parents=True)
shutil.copyfile(source/'about.txt',seed/'about.txt')
shutil.copyfile(source/'COPYING',seed/'COPYING')
# SDL_ttf reads the font format from the file. Esoteric expects this shared filename.
frontend_assets = ROOT / 'assets/frontend'
shutil.copyfile(frontend_assets / 'default.otf', seed / 'skins/font.ttf')
shutil.copyfile(frontend_assets / 'licenses/NotoSansJP-OFL.txt', seed / 'skins/font-license.txt')
conf=(source/'assets/rg-350/esoteric.conf').read_text()
for a,b in [('resolutionX=-1','resolutionX=320'),('resolutionY=-1','resolutionY=240'),('videoBpp=32','videoBpp=16'),('backlightTimeout=30','backlightTimeout=0'),('powerTimeout=10','powerTimeout=0'),('cpuMenu=0','cpuMenu="Default"'),('globalVolume=60','globalVolume=40'),('buttonRepeatRate=50','buttonRepeatRate=100')]:conf=conf.replace(a,b)
(seed/'esoteric.conf').write_text(conf)
inputconf=(source/'assets/input/generic.input.conf').read_text().replace('power=keyboard,278','power=keyboard,0')
(seed/'input.conf').write_text(inputconf)
launch=stage/'350teric/launchers';launch.mkdir()
count=0
labels={'fceux':'FCEUX','fceux223':'FCEUX 2.2.3','fceumm':'FCEUmm','nestopia':'Nestopia',
 'quicknes':'QuickNES','pocketsnes':'PocketSNES','snes9x2005':'Snes9x 2005',
 'snes9x2005_plus':'Snes9x 2005 Plus','chimerasnes':'ChimeraSNES','gambatte':'Gambatte',
 'gambatte2020':'Gambatte 2020','gearboy':'Gearboy','vbam':'VBA-M','ohboy':'OhBoy',
 'regba':'ReGBA','gpsp':'gpSP','picodrive':'PicoDrive','genesisgx':'Genesis GX',
 'genesis_plus_gx':'Genesis Plus GX','gearsystem':'Gearsystem','smsplusms':'SMS Plus',
 'smsplusgg':'SMS Plus','mednafen_pce_fast':'PCE Fast','mednafen_supergrafx':'SuperGrafx',
 'mednafen_wswan':'WonderSwan','pcsx4all':'PCSX4ALL','race':'Race','oswan':'Oswan',
 'fmsx':'fMSX','bluemsx':'blueMSX','atari800':'Atari800','stella':'Stella',
 'pokemini':'PokeMini','handy':'Handy','crocods':'CrocoDS','unrealspeccy':'Unreal Speccy',
 'gngeo':'GnGeo','neo4all':'NEO4ALL','uae4all':'UAE4ALL','fba44':'FBA44','temper':'Temper'}
shorts={'mastersystem':'MS','gamegear':'GG','megadrive':'MD','pcengine':'PCE',
 'pcenginecd':'PCE CD','supergrafx':'SGX','neogeocd':'NGCD','atari2600':'A2600',
 'atari800':'A800','zxspectrum':'ZX','wonderswan':'WS','pokemini':'PokeMini'}
(seed/'icons').mkdir()
for sys in systems:
 if not sys.get('enabled') or not sys.get('launch_profiles'):continue
 ident=sys['id']
 dirs=[('/media/data/sd2/roms/'+a['name'].strip('/')) for a in sys['directory_aliases']]
 selected=None
 for d in dirs:
  if shell('test -d '+Q(d)+' && echo yes || true')=='yes': selected=d;break
 if selected is None:continue
 # One concrete entry per registered route, including the default route.
 for index,profile in enumerate(sys['launch_profiles'],1):
  name=ident+'__'+str(index)
  cmd=[BASE+'/bin/plumos-text-ui','launch',ident]
  extra=' --profile '+Q(profile) if profile else ''
  script=launch/name
  script.write_text('''#!/bin/sh
set -eu
sdcard=${PLUMOS_SDCARD_ROOT:-/media/data/sd2}
rom=$(readlink -f "$1")
case "$rom" in "$sdcard/roms/"*) relative=${rom#"$sdcard/roms/"} ;; *) exit 2 ;; esac
'''+ 'exec '+' '.join(map(Q,cmd))+' "$relative" --no-scan --execute'+extra+'\n')
  script.chmod(0o755)
  kind,core=profile.split(':',1)
  prefix={'standalone':'SA','picoarch':'PICO','retroarch':'RA'}.get(kind,kind.upper())
  title=shorts.get(ident,sys.get('short_name',ident.upper()))+' - '+prefix+':'+labels.get(core,core)
  icon=ROOT/'assets/frontend/logos/systems'/(ident+'.png')
  icon_path='skin:icons/section.png'
  if icon.exists():
   shutil.copyfile(icon,seed/'icons'/icon.name)
   icon_path=HOME+'/icons/'+icon.name
  description=sys['display_name']+' / '+profile+(' (default)' if profile==sys.get('default_launch_profile') else '')
  (seed/'sections/emulators'/name).write_text('\n'.join(['title='+title,'description='+description,'icon='+icon_path,'exec='+BASE+'/350teric/launchers/'+name,'params=[selFullPath]','selectordir='+selected+'/','selectorbrowser=true','selectorfilter='+','.join('.'+e.lstrip('.') for e in sys['extensions']),'consoleapp=false'])+'\n')
  count+=1
# Add normal shell Apps without introducing OPK test entries or recursive frontend launches.
apps=json.loads(shell('cat '+BASE+'/config/frontend/apps.json'))
for app in apps['apps']:
 profile=app.get('launch_profile','')
 if app.get('visible',True) and app['id'] not in ['350teric','simplemenu'] and profile.startswith('shell:'):
  (seed/'sections/applications'/app['id']).write_text('title='+app['display_name']+'\nexec='+profile[6:]+'\nconsoleapp=false\n')
# Reuse plumOS's compatible OPK app launcher, not stock OpenDingux execution.
for filename in shell('for f in /media/data/apps/*.opk; do test -f "$f" && basename "$f"; done').splitlines():
 if not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*[.]opk',filename) or '..' in filename:continue
 info=shell('/usr/bin/opkinfo '+Q('/media/data/apps/'+filename))
 title=next((line[6:].strip() for line in info.splitlines() if line.startswith('Name: ')),None)
 if title:
  (seed/'sections/applications'/('opk_'+filename[:-4])).write_text('title='+title+'\nexec='+BASE+'/bin/plumos-opk-app-launch\nparams='+Q(filename)+'\nconsoleapp=false\n')
(stage/'bin').mkdir()
for n in ['plumos-350teric','plumos-350teric-invoker']:
 shutil.copyfile(ROOT/'assets/frontend/bin'/n,stage/'bin'/n);(stage/'bin'/n).chmod(0o755)
archive=WORK/'install.tar'
with tarfile.open(archive,'w') as tar:
 for p in stage.iterdir():tar.add(p,arcname=p.name)
subprocess.run(ADB+['push',str(archive),BASE+'/350teric-install.tar'],check=True)
assert shell('sha256sum '+BASE+'/350teric-install.tar').split()[0]==hashlib.sha256(archive.read_bytes()).hexdigest()
shell('set -e; rm -rf '+BASE+'/350teric/seed; tar -xf '+BASE+'/350teric-install.tar -C '+BASE+'; rm '+BASE+'/350teric-install.tar; mkdir -p '+BASE+'/home/350teric; if ! test -d '+HOME+'; then cp -a '+BASE+'/350teric/seed/.esoteric '+BASE+'/home/350teric/; fi')
# Upgrade the original shared font while retaining any user's own replacement.
shell(f'''set -e
skins={Q(HOME + '/skins')}
seed_skins={Q(BASE + '/350teric/seed/.esoteric/skins')}
if ! test -L "$skins/font.ttf"; then
    if ! test -e "$skins/font.ttf" ||
       printf '%s  %s\\n' {LEGACY_FONT_SHA256} "$skins/font.ttf" | sha256sum -c >/dev/null 2>&1; then
        mkdir -p "$skins"
        cp -p "$seed_skins/font.ttf" "$skins/font.ttf.new"
        cp -p "$seed_skins/font-license.txt" "$skins/font-license.txt.new"
        mv "$skins/font-license.txt.new" "$skins/font-license.txt"
        mv "$skins/font.ttf.new" "$skins/font.ttf"
    fi
fi''')
# Project-owned skins are available on fresh installs; existing skin edits survive.
if project_skins.exists():
 for skin in project_skins.iterdir():
  if skin.is_dir():
   destination=HOME+'/skins/'+skin.name
   shell('if ! test -d '+Q(destination)+'; then cp -a '+Q(BASE+'/350teric/seed/.esoteric/skins/'+skin.name)+' '+Q(HOME+'/skins/')+'; fi')
# Refresh only installer-owned route files; retain custom links, favorites and settings.
backup=BASE+'/backup/350teric-'+time.strftime('%Y%m%d-%H%M%S')
shell('mkdir -p '+backup+'; cp -a '+HOME+'/sections '+backup+'/; cp -p '+BASE+'/config/frontend/apps.json '+backup+'/apps.json')
for filename in shell('for f in '+HOME+'/sections/emulators/*; do printf \'%s\\n\' "${f##*/}"; done').splitlines():
 if re.fullmatch(r'[a-z0-9_]+__[0-9]+',filename):
  shell('rm -f '+Q(HOME+'/sections/emulators/'+filename))
shell('set -e; cp -a '+BASE+'/350teric/seed/.esoteric/sections/emulators/. '+HOME+'/sections/emulators/; cp -a '+BASE+'/350teric/seed/.esoteric/sections/applications/. '+HOME+'/sections/applications/; mkdir -p '+HOME+'/icons; cp -a '+BASE+'/350teric/seed/.esoteric/icons/. '+HOME+'/icons/')
apps['apps']=[a for a in apps['apps'] if a['id']!='350teric']
apps['apps'].append(dict(id='350teric',display_name='350teric',menu='apps',kind='shell',visible=True,launch_profile='shell:'+BASE+'/bin/plumos-350teric'))
p=WORK/'apps.json';p.write_text(json.dumps(apps,ensure_ascii=False,indent=2)+'\n')
subprocess.run(ADB+['push',str(p),BASE+'/config/frontend/apps.json.new'],check=True)
assert json.loads(shell('cat '+BASE+'/config/frontend/apps.json.new'))==apps
shell('mv '+BASE+'/config/frontend/apps.json.new '+BASE+'/config/frontend/apps.json')
print('Installed',count,'emulator routes; existing user configuration preserved')
