#!/usr/bin/env python3
"""Install original PyMenu UI with existing, managed plumOS launch profiles."""
import hashlib, json, pathlib, shlex, shutil, subprocess, tarfile, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORK=ROOT/'output/rg280v-pymenu'
BASE='/media/data/plumos'
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
Q=shlex.quote
def shell(s): return subprocess.check_output(ADB+['shell',s],text=True).strip()
def writejson(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if shell('pidof python3.11 || true'):raise SystemExit('PyMenu is running')
systems=json.loads(shell('cat '+BASE+'/config/frontend/systems.json'))['systems']
stage=WORK/'install'
if stage.exists():shutil.rmtree(stage)
ui=stage/'pymenu/ui';ui.mkdir(parents=True)
source=WORK/'source'
for p in source.glob('*.py'):shutil.copyfile(p,ui/p.name)
if '--ui-only' not in __import__('sys').argv:
 shutil.copytree(WORK/'runtime/python',stage/'pymenu/python',symlinks=True)
shutil.copytree(source/'theme',ui/'theme')
shutil.copytree(source/'images',ui/'images')
# Reuse the existing FE Japanese font; FreeType detects OTF regardless of suffix.
shutil.copyfile(ROOT/'assets/frontend/default.otf',ui/'theme/NotoSans-Regular.ttf')
shutil.copytree(ROOT/'assets/frontend/licenses',ui/'font-licenses')
for f in ['LICENSE','LICENSE.md','LICENSE.txt']:
 if (source/f).exists():shutil.copyfile(source/f,ui/f)
config=json.loads((source/'config/config_OpenDinguX.json').read_text())
config.update(linkPath=BASE+'/pymenu/ui/links',opkPath=BASE+'/pymenu/ui/empty-opks',batteryLow=3300000,batteryHigh=4200000,mainMenu=[])
config['options'].update(allowEdit=False,showAll=False)
links=ui/'links';links.mkdir()
(ui/'empty-opks').mkdir()
launchers=stage/'pymenu/launchers';launchers.mkdir()
known={'mastersystem':'SMS','megadrive':'SMD','gamegear':'GG','pcengine':'PCE','pcenginecd':'PCE CD','supergrafx':'SGX','neogeocd':'NGCD','atari2600':'A26','atari800':'A800','zxspectrum':'SZX','wonderswan':'WS','pokemini':'PokeMini','lynx':'LNX','psx':'PS'}
count=0
for system in systems:
 if not system.get('enabled') or not system.get('launch_profiles'):continue
 ident=system['id']
 dirs=['/media/data/sd2/roms/'+a['name'].strip('/') for a in system['directory_aliases']]
 selected=next((d for d in dirs if shell('test -d '+Q(d)+' && echo yes || true')=='yes'),None)
 if not selected:continue
 title=known.get(ident,system.get('short_name',ident.upper()))
 entry=dict(name=title,description=system['display_name'],type='emulator',system=ident,selectionPath=selected,previews=selected+'/previews',useFileFilter=True,useGamelist=False,limitSelection=True,hideFolders=False,useSelection=True)
 # For unsupported stock-theme system names use the existing plumOS system logo.
 logo=ROOT/'assets/frontend/logos/systems'/(ident+'.png')
 if logo.exists():
  (ui/'theme/plumos').mkdir(exist_ok=True);shutil.copyfile(logo,ui/'theme/plumos'/logo.name)
  entry['icon']='theme/plumos/'+logo.name
 config['mainMenu'].append(entry)
 profiles=list(system['launch_profiles'])
 default=system.get('default_launch_profile')
 if default in profiles:profiles.remove(default);profiles.insert(0,default)
 for index,profile in enumerate(profiles):
  name=ident+'__'+str(index)
  script=launchers/name
  script.write_text('''#!/bin/sh
set -eu
sdcard=${PLUMOS_SDCARD_ROOT:-/media/data/sd2}
rom=$(readlink -f "$1")
case "$rom" in "$sdcard/roms/"*) relative=${rom#"$sdcard/roms/"} ;; *) exit 2 ;; esac
exec '''+Q(BASE+'/bin/plumos-text-ui')+' launch '+Q(ident)+' "$relative" --no-scan --execute --profile '+Q(profile)+'\n')
  script.chmod(0o755)
  kind,core=profile.split(':',1);label={'standalone':'SA','picoarch':'PICO','retroarch':'RA'}.get(kind,kind.upper())+':'+core
  (links/name).write_text('system='+ident+'\ntitle='+label+'\nexec='+BASE+'/pymenu/launchers/'+name+'\nselectordir='+selected+'\nselectorfilter='+','.join('.'+e.lstrip('.') for e in system['extensions'])+'\n')
  count+=1
# Stock artwork is kept where available; other machines reuse the formal FE logo.
for theme_path in (ui/'theme/themes').glob('*.json'):
 theme=json.loads(theme_path.read_text())
 for item in config['mainMenu']:
  if item['name'] not in theme and item.get('icon'):
   theme[item['name']]=dict(icon=item['icon'],folderIcon=item['icon'],background='theme/defaultBackground.png')
  artwork=theme.get(item['name'],{})
  for key in ['icon','folderIcon','background','preview']:
   if key=='preview' and key not in artwork:continue
   old=artwork.get(key)
   if old and (ui/old).is_file():continue
   # Upstream Pixel's Neo Geo entry references a non-existent images/pixel tree.
   corrected=old.replace('images/pixel/','images/pixel97/') if isinstance(old,str) else None
   if corrected and (ui/corrected).is_file():artwork[key]=corrected
   else:artwork[key]='theme/defaultBackground.png' if key=='background' else item['icon']
 writejson(theme_path,theme)
config['mainMenu'] += [dict(name='Last Played',description='Last played games',type='lastPlayed'),dict(name='Favourites',description='Favourite games',type='favourites',data=[])]
seed=stage/'pymenu/seed';seed.mkdir()
writejson(seed/'config.json',config)
options=json.loads((source/'config/options.json').read_text())
options=[o for o in options if o['id'] in ['showLastPlayed','showFavourites','showFPS','themeName']]
writejson(seed/'options.json',options)
for p in (source/'config').glob('options*.json'):
 if p.name!='options.json':shutil.copyfile(p,seed/p.name)
# A private writable configuration prevents edits to the original theme/runtime.
(ui/'config').symlink_to(BASE+'/home/pymenu/config')
(stage/'bin').mkdir()
for n in ['plumos-pymenu','plumos-pymenu-invoker']:
 shutil.copyfile(ROOT/'assets/frontend/bin'/n,stage/'bin'/n);(stage/'bin'/n).chmod(0o755)
archive=WORK/'install.tar'
with tarfile.open(archive,'w') as tar:
 for p in stage.iterdir():tar.add(p,arcname=p.name)
if int(shell('df -k '+BASE).splitlines()[-1].split()[3]) < archive.stat().st_size//1024*2+12000:raise SystemExit('Insufficient SD1 space')
subprocess.run(ADB+['push',str(archive),BASE+'/pymenu-install.tar'],check=True)
assert shell('sha256sum '+BASE+'/pymenu-install.tar').split()[0]==hashlib.sha256(archive.read_bytes()).hexdigest()
backup=BASE+'/backup/pymenu-'+time.strftime('%Y%m%d-%H%M%S')
shell('set -e; mkdir -p '+backup+'; cp -p '+BASE+'/config/frontend/apps.json '+backup+'/apps.json; tar -xf '+BASE+'/pymenu-install.tar -C '+BASE+'; rm '+BASE+'/pymenu-install.tar; mkdir -p '+BASE+'/home/pymenu; if ! test -d '+BASE+'/home/pymenu/config; then cp -a '+BASE+'/pymenu/seed '+BASE+'/home/pymenu/config; fi')
# Registration is a separate post-validation step.
if '--register' in __import__('sys').argv:
 apps=json.loads(shell('cat '+BASE+'/config/frontend/apps.json'))
 apps['apps']=[a for a in apps['apps'] if a['id']!='pymenu']
 apps['apps'].append(dict(id='pymenu',display_name='PyMenu',menu='apps',kind='shell',visible=True,launch_profile='shell:'+BASE+'/bin/plumos-pymenu'))
 p=WORK/'apps.json';writejson(p,apps)
 subprocess.run(ADB+['push',str(p),BASE+'/config/frontend/apps.json.new'],check=True)
 assert json.loads(shell('cat '+BASE+'/config/frontend/apps.json.new'))==apps
 shell('mv '+BASE+'/config/frontend/apps.json.new '+BASE+'/config/frontend/apps.json')
print('Installed',count,'managed routes; registration requires --register')
