#!/usr/bin/env python3
"""Install JZ4770 EmulationStation, reusing default formal plumOS routes."""
import hashlib,json,pathlib,shlex,shutil,subprocess,tarfile,time,xml.etree.ElementTree as ET
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORK=ROOT/'output/rg280v-emulationstation'
BASE='/media/data/plumos'
HOME=BASE+'/home/emulationstation/.emulationstation'
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
Q=shlex.quote
def shell(s):return subprocess.check_output(ADB+['shell',s],text=True).strip()
if shell('pidof emulationstation || true'):raise SystemExit('EmulationStation is running')
systems=json.loads(shell('cat '+BASE+'/config/frontend/systems.json'))['systems']
stage=WORK/'install'
if stage.exists():shutil.rmtree(stage)
shutil.copytree(WORK/'runtime',stage/'emulationstation',symlinks=True)
seed=stage/'emulationstation/seed';seed.mkdir()
launchers=stage/'emulationstation/launchers';launchers.mkdir()
# Original low-resolution RG350 theme. No emulator binaries, BIOS or ROMs copied.
shutil.copytree(WORK/'distribution/Internal SD Card/data/themes/simplegcw',seed/'themes/simplegcw')
# Backgrounds are 1280x720 upstream; retain aspect while matching panel height.
for image_path in (seed/'themes/simplegcw').rglob('*_art_blur.jpg'):
 with Image.open(image_path) as image:
  image.thumbnail((640,240),Image.Resampling.LANCZOS)
  image.save(image_path,quality=92)
config=ET.Element('systemList')
mapping={'sfc':'snes','lynx':'atarilynx','cpc':'amstradcpc','arcade':'fba'}
platforms={'sfc':'snes','lynx':'atarilynx','cpc':'amstradcpc',
 'supergrafx':'ignore','pcenginecd':'ignore','pokemini':'ignore','neogeocd':'ignore'}
count=0
for system in systems:
 if not system.get('enabled') or not system.get('launch_profiles'):continue
 ident=system['id']
 dirs=['/media/data/sd2/roms/'+a['name'].strip('/') for a in system['directory_aliases']]
 selected=next((d for d in dirs if shell('test -d '+Q(d)+' && echo yes || true')=='yes'),None)
 if not selected:continue
 profile=system['default_launch_profile']
 script=launchers/ident
 script.write_text('''#!/bin/sh
set -eu
unset SDL_VIDEO_KMSDRM_SCALING_MODE LIBGL_DRIVERS_PATH
sdcard=${PLUMOS_SDCARD_ROOT:-/media/data/sd2}
rom=$(readlink -f "$1")
case "$rom" in "$sdcard/roms/"*) relative=${rom#"$sdcard/roms/"} ;; *) exit 2 ;; esac
exec '''+Q(BASE+'/bin/plumos-text-ui')+' launch '+Q(ident)+' "$relative" --no-scan --execute --profile '+Q(profile)+'\n')
 script.chmod(0o755)
 kind,core=profile.split(':',1);prefix={'standalone':'SA','picoarch':'PICO','retroarch':'RA'}.get(kind,kind.upper())
 theme=mapping.get(ident,ident)
 if not (seed/'themes/simplegcw'/theme/'theme.xml').exists():
  # Missing artwork must never borrow another machine's identity.
  folder=seed/'themes/simplegcw'/theme
  (folder/'art').mkdir(parents=True,exist_ok=True)
  logo=ROOT/'assets/frontend/logos/systems'/(ident+'.png')
  if not logo.exists():raise SystemExit('Missing system artwork: '+ident)
  shutil.copyfile(logo,folder/'art/system.png')
  # Keep the stock layout, replacing all machine-specific artwork and labels.
  tree=ET.parse(seed/'themes/simplegcw/gb/theme.xml')
  manufacturers={'pokemini':'Nintendo','pcenginecd':'NEC'}
  for view in tree.getroot().findall('view'):
   for image in view.findall('image'):
    if image.get('name')=='logo':image.find('path').text='./art/system.png'
    elif image.get('name')=='background':
     image.find('path').text='./../art/mid.png'
     ET.SubElement(image,'size').text='1 1'
   for text in view.findall('text'):
    if text.get('name')=='system_name_1':text.find('text').text=manufacturers.get(ident,'')
    elif text.get('name')=='system_name_2':text.find('text').text=system['display_name']
   if view.get('name')=='system':
    title=ET.SubElement(view,'text',name='system_title',extra='true')
    for key,value in {'text':system['display_name'],'pos':'0.05 0.28','size':'0.9 0.1',
     'color':'333333','fontPath':'./../art/OPENSANS.TTF','fontSize':'0.065','alignment':'center'}.items():
     ET.SubElement(title,key).text=value
  ET.indent(tree)
  tree.write(folder/'theme.xml',encoding='utf-8',xml_declaration=True)
 node=ET.SubElement(config,'system')
 values=dict(name=ident,fullname=system['display_name']+' / '+prefix+':'+core,path=selected,
  extension=' '.join('.'+e.lstrip('.')+' .'+e.lstrip('.').upper() for e in system['extensions']),
  command=Q(BASE+'/emulationstation/launchers/'+ident)+' %ROM%',platform=platforms.get(ident,ident),theme=theme)
 for key,value in values.items():ET.SubElement(node,key).text=value
 count+=1
theme_ids=[node.findtext('theme') for node in config]
assert len(theme_ids)==len(set(theme_ids)), 'Each enabled machine must have its own theme identity'
ET.indent(config);ET.ElementTree(config).write(seed/'es_systems.cfg',encoding='utf-8',xml_declaration=True)
inputs=ET.Element('inputList');keyboard=ET.SubElement(inputs,'inputConfig',type='keyboard',deviceName='Keyboard',deviceGUID='-1')
for name,key in dict(up=1073741906,down=1073741905,left=1073741904,right=1073741903,a=1073742048,b=1073742050,x=32,y=1073742049,start=13,select=27,pageup=9,pagedown=8).items():
 ET.SubElement(keyboard,'input',name=name,type='key',id=str(key),value='1')
ET.ElementTree(inputs).write(seed/'es_input.cfg',encoding='utf-8',xml_declaration=True)
settings=ET.Element('config')
for tag,name,value in [('string','ThemeSet','simplegcw'),('string','TransitionStyle','instant'),('int','ScreenSaverTime','0'),('bool','EnableSounds','false'),('bool','ShowExit','true'),('bool','VSync','true')]:ET.SubElement(settings,tag,name=name,value=value)
ET.ElementTree(settings).write(seed/'es_settings.cfg',encoding='utf-8',xml_declaration=True)
(stage/'bin').mkdir();shutil.copyfile(ROOT/'assets/frontend/bin/plumos-emulationstation',stage/'bin/plumos-emulationstation');(stage/'bin/plumos-emulationstation').chmod(0o755)
archive=WORK/'install.tar'
with tarfile.open(archive,'w') as tar:
 for p in stage.iterdir():tar.add(p,arcname=p.name)
if int(shell('df -k '+BASE).splitlines()[-1].split()[3])<archive.stat().st_size//1024*2+12000:raise SystemExit('Insufficient SD1 space')
subprocess.run(ADB+['push',str(archive),BASE+'/es-install.tar'],check=True)
assert shell('sha256sum '+BASE+'/es-install.tar').split()[0]==hashlib.sha256(archive.read_bytes()).hexdigest()
backup=BASE+'/backup/emulationstation-'+time.strftime('%Y%m%d-%H%M%S')
shell('set -e; mkdir -p '+backup+'; cp -p '+BASE+'/config/frontend/apps.json '+backup+'/apps.json; tar -xf '+BASE+'/es-install.tar -C '+BASE+'; rm '+BASE+'/es-install.tar; mkdir -p '+HOME+'; if ! test -f '+HOME+'/es_systems.cfg; then cp -a '+BASE+'/emulationstation/seed/. '+HOME+'/; fi')
if '--register' in __import__('sys').argv:
 apps=json.loads(shell('cat '+BASE+'/config/frontend/apps.json'))
 apps['apps']=[a for a in apps['apps'] if a['id']!='emulationstation']
 apps['apps'].append(dict(id='emulationstation',display_name='EmulationStation',menu='apps',kind='shell',visible=True,launch_profile='shell:'+BASE+'/bin/plumos-emulationstation'))
 p=WORK/'apps.json';p.write_text(json.dumps(apps,ensure_ascii=False,indent=2)+'\n')
 subprocess.run(ADB+['push',str(p),BASE+'/config/frontend/apps.json.new'],check=True)
 assert json.loads(shell('cat '+BASE+'/config/frontend/apps.json.new'))==apps
 shell('mv '+BASE+'/config/frontend/apps.json.new '+BASE+'/config/frontend/apps.json')
# Generated routes track the accepted FE defaults; bindings/settings remain user owned.
shell('if test -f '+HOME+'/es_systems.cfg; then cp -p '+HOME+'/es_systems.cfg '+backup+'/es_systems.cfg; fi; cp -p '+BASE+'/emulationstation/seed/es_systems.cfg '+HOME+'/es_systems.cfg')
# Refresh only the installer-owned stock theme, retaining other user theme sets.
shell('mkdir -p '+HOME+'/themes; cp -a '+BASE+'/emulationstation/seed/themes/simplegcw '+HOME+'/themes/')
print('Installed',count,'default routes; registration requires --register')
