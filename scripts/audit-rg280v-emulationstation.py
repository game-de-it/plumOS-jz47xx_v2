#!/usr/bin/env python3
"""Read-only comparison of every installed ES system against the native FE."""
import json,pathlib,shlex,subprocess,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
WORK=ROOT/'output/rg280v-emulationstation'
BASE='/media/data/plumos'
HOME=BASE+'/home/emulationstation/.emulationstation'
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
def shell(s):return subprocess.check_output(ADB+['shell',s],text=True).strip()
def read(p):return shell('cat '+shlex.quote(p))
systems=json.loads(read(BASE+'/config/frontend/systems.json'))['systems']
expected={s['id']:s for s in systems if s.get('enabled') and s.get('launch_profiles')}
installed=ET.fromstring(read(HOME+'/es_systems.cfg'))
assert [n.findtext('name') for n in installed]==list(expected),'System identity/order differs from FE'
seen=set();rows=[]
for node in installed:
 ident=node.findtext('name');system=expected[ident]
 path=node.findtext('path');profile=system['default_launch_profile']
 aliases={'/media/data/sd2/roms/'+a['name'].strip('/') for a in system['directory_aliases']}
 assert path.casefold() in {a.casefold() for a in aliases},(ident,'ROM path',path)
 assert {e.lower().lstrip('.') for e in node.findtext('extension').split()}=={e.lower().lstrip('.') for e in system['extensions']},(ident,'extensions')
 launcher=BASE+'/emulationstation/launchers/'+ident
 assert shlex.split(node.findtext('command'))==[launcher,'%ROM%'],(ident,'command')
 code=read(launcher)
 line=next(l for l in code.splitlines() if l.startswith('exec '))
 args=shlex.split(line)
 assert args[1:4]==[BASE+'/bin/plumos-text-ui','launch',ident],(ident,'launcher system')
 assert args[args.index('--profile')+1]==profile,(ident,'launcher profile')
 assert 'LIBGL_DRIVERS_PATH' in code,(ident,'private driver isolation')
 theme=node.findtext('theme');assert theme not in seen,(ident,'theme shared with another system',theme)
 seen.add(theme)
 theme_root=HOME+'/themes/simplegcw/'+theme
 theme_xml=ET.fromstring(read(theme_root+'/theme.xml'))
 header=[];logos=[]
 for view in theme_xml.findall('view'):
  for text in view.findall('text'):
   if text.get('name','').startswith('system_name_') and text.findtext('text'):
    if text.findtext('text') not in header:header.append(text.findtext('text'))
  for image in view.findall('image'):
   if image.get('name')=='logo' and image.findtext('path'):
    value=image.findtext('path')
    if value not in logos:logos.append(value)
    assert shell('test -f '+shlex.quote(theme_root+'/'+value)+' && echo yes')=='yes',(ident,'missing logo',value)
 if ident=='pokemini':assert header==['Nintendo','Pokemon Mini'] and theme=='pokemini',(ident,header)
 if ident=='pcenginecd':assert header==['NEC','PC Engine CD'] and theme=='pcenginecd',(ident,header)
 if ident=='gb':assert header==['Nintendo','Game Boy'] and theme=='gb',(ident,header)
 # Check a real file through the launch planner, without executing any emulator.
 extensions={'.'+e.lower().lstrip('.') for e in system['extensions']}
 files=shell('find '+shlex.quote(path)+' -type f').splitlines()
 rom=next((f for f in files if pathlib.PurePosixPath(f).suffix.lower() in extensions and not any(part.startswith('.') for part in pathlib.PurePosixPath(f).parts) and pathlib.PurePosixPath(f).name.lower() not in {'neogeo.zip','bios.zip'}),None)
 assert rom,(ident,'no ROM for launch-plan audit')
 relative=rom[len('/media/data/sd2/roms/'):]
 plan=shell('PLUMOS_ROOT='+BASE+' PLUMOS_SDCARD_ROOT=/media/data/sd2 '+shlex.join([BASE+'/bin/plumos-text-ui','launch',ident,relative,'--no-scan','--profile',profile]))
 assert 'system: '+ident+'\n' in plan and 'launch_profile: '+profile+'\n' in plan,(ident,'launch plan mismatch')
 assert 'rom_exists: yes' in plan and 'can_execute: yes' in plan,(ident,'launch plan unavailable',plan)
 rows.append(dict(system=ident,rom_path=path,profile=profile,theme=theme,header=' / '.join(header),logos=logos,plan_rom=relative,status='PASS'))
 print('PASS',ident,'|',theme,'|',' / '.join(header),'|',profile,flush=True)
WORK.mkdir(parents=True,exist_ok=True)
(WORK/'system-binding-audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('PASS:',len(rows),'systems; unique themes, ROM directories, extensions, launchers, profiles, artwork and launch plans')
