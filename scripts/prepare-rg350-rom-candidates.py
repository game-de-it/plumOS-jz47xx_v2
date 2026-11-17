#!/usr/bin/env python3
"""Inventory ROM candidates for all 62 OPKs; optionally stage small ROMs."""
import argparse,os,json,re,hashlib,subprocess,zipfile,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rom-root',type=Path,default=Path('<local-path>'))
parser.add_argument('--deploy',action='store_true')
parser.add_argument('--refresh-inventory',action='store_true')
args=parser.parse_args(); NAS=args.rom_root
inventory=ROOT/'output/rg280v-apps/rg350-rom-inventory.json'
if not NAS.is_dir(): parser.error('ROM root is not mounted')
if args.rom_root != Path('<local-path>'):
 args.refresh_inventory=True
if args.refresh_inventory or not inventory.exists():
 files=[]
 for base,dirs,names in os.walk(NAS):
  dirs[:]=[d for d in dirs if not d.startswith('.')]
  files.extend(str((Path(base)/n).relative_to(NAS)) for n in names if not n.startswith('.'))
 inventory.parent.mkdir(parents=True,exist_ok=True)
 inventory.write_text(json.dumps(files,ensure_ascii=False,indent=2))
files=json.loads(inventory.read_text())
# Each catalog entry points to one family; alternate OPKs share the same three games.
groups={
'3do':([1],['_etc/3do'],['iso','cue']), 'cpc':([2,33],['_etc/amstradcpc'],['dsk','sna','bin']),
'atari800':([3,4],['ATARI/800'],['rom','car','xex','atr','dsk']), 'coleco':([5],['_etc/coleco'],['col','rom']),
'atarist':([6],['_etc/atarist'],['st','msa']), 'dos':([7],['pc'],['zip']), 'daphne':([8],['_etc/daphne'],['txt','zip']),
'vectrex':([9],['_etc/vectrex'],['vec','bin']), 'easyrpg':([10],['_etc/EASYRPG'],['ldb']),
'nes':([11,16],['nes'],['nes']), 'md':([12,19,54],['megadrive'],['md','gen','smd','bin']),
'lynx':([13],['ATARI/Lynx'],['lnx']), 'apple2gs':([14],['_etc/apple2gs'],['2mg','po','dsk']),
'neogeocd':([15],['_etc/neogeocd'],['cue']), 'openbor':([17],['openbor'],['pak']),
'ws':([18],['wonderswan'],['ws','wsc']), 'snes':([20,27],['snes'],['sfc','smc']),
'pokemini':([21],['_etc/pokemini'],['zip','min']), 'supervision':([22],['_etc/supervision'],['bin','sv']),
'atari7800':([23],['ATARI/7800'],['a78','bin']), 'ngpc':([24,25],['ngpc'],['ngc','ngp']),
'gba':([26,40],['gba'],['gba']), 'atari2600':([28],['ATARI/2600'],['bin','a26']),
'pce':([29,46],['pcengine'],['pce']), 'amiga':([30,60],['_etc/amiga'],['adf']),
'c64':([31],['_etc/c64'],['d64','zip']), 'mame':([32,43,44],['mame'],['zip']),
'fba':([34],['fbneo'],['zip']), 'gb':([35,36,37,49],['gb'],['gb']), 'gbc':([38],['gbc'],['gbc']),
'neogeo':([39],['_etc/neogeo'],['zip']), 'gw':([41],['_etc/gameandwatch'],['zip']),
'intv':([42],['_etc/intellivision'],['int','bin']), 'mednafen':([45],['pcengine'],['pce']),
'pcfx':([47],['_etc/pcfx'],['cue']), 'n64':([48],['n64'],['z64','n64','v64']),
'msx':([50],['msx2'],['rom','mx1','mx2']), 'psx':([51],['psx'],['cue','pbp','chd']),
'32x':([52],['_etc/sega32x'],['32x']), 'segacd':([53],['_etc/segacd'],['cue','chd']),
'pico8':([55],['pico-8'],['p8','png']), 'scummvm':([56],['scummvm'],['scummvm','dsk','000','he0']),
'gg':([57],['gamegear'],['gg']), 'sms':([58],['mastersystem'],['sms']),
'tic80':([59],['_etc/tic80'],['tic']), 'zx':([61,62],['_etc/zxspectrum'],['tap','tzx','z80','sna'])}
prefs={'gb':['Super Mario Land','Dr. Mario','Dracula Densetsu'],'ngpc':['Baseball Stars','Metal Slug - 1st','Sonic'],'md':['Bare Knuckle','Sonic','VampireKiller'],'fba':['kungfum.zip','bchopper.zip','nspirit.zip'],'pce':['AirZonk','Blazing','BONK'],'nes':['Super Mario Bros.','Baseball','Rockman'],'pokemini':['Pichu','Anime','Europe']}
adb=['adb','-P','5041','-s','10.1.1.2:5555'];remote='/media/data/local/rg350-rom-candidates'
def shell(s):return subprocess.check_output(adb+['shell',s],text=True).strip()
manifest=[];staged=[]
for family,(ids,dirs,exts) in groups.items():
 matches=[f for f in files if any(f.startswith(d+'/') for d in dirs) and Path(f).suffix.lower()[1:] in exts]
 def rank(f):
  name=Path(f).name
  return (next((i for i,p in enumerate(prefs.get(family,[])) if p.lower() in name.lower()),99),len(Path(f).parts),f.lower())
 matches.sort(key=rank);chosen=[];seen=set()
 for f in matches:
  title=re.sub(r'\([^)]*\)|\[[^]]*\]','',Path(f).stem).lower().strip()
  if family=='neogeocd':title=title.replace(' wav','')
  if title in seen:continue
  seen.add(title);chosen.append(f)
  if len(chosen)==3:break
 entries=[]
 for i,f in enumerate(chosen,1):
  p=NAS/f; item={'source':f,'title':p.stem,'bytes':p.stat().st_size,'remote':None}
  # CD media and game directories require their full data set; keep them at source.
  directory_game=family in ['easyrpg','scummvm','neogeocd','pcfx','segacd','psx','3do']
  if args.deploy and not directory_game and item['bytes']<=8*1024*1024:
   dest=f'{remote}/{family.strip()}/{i:02d}{p.suffix.lower()}'
   if p.suffix.lower()=='.zip' and family not in ['fba','mame','neogeo','dos','c64']:
    with zipfile.ZipFile(p) as z:
     inner=[x for x in z.infolist() if not x.is_dir() and not x.filename.startswith('__MACOSX') and Path(x.filename).suffix.lower() in ['.min','.rom','.gw']]
     if len(inner)==1:
      data=z.read(inner[0]);local=ROOT/'output/rg280v-apps/rom-candidate-stage'/family.strip()/f'{i:02d}{Path(inner[0].filename).suffix.lower()}'
      local.parent.mkdir(parents=True,exist_ok=True);local.write_bytes(data);p=local;dest=str(Path(dest).with_suffix(local.suffix))
   # Arcade loaders depend on the original ZIP basename.
   if family in ['fba','mame','neogeo']:dest=f'{remote}/{family}/{p.name}'
   shell('mkdir -p '+shlex.quote(str(Path(dest).parent)))
   subprocess.run(adb+['push',str(p),dest],check=True,capture_output=True)
   digest=hashlib.sha256(p.read_bytes()).hexdigest()
   actual=shell('sha256sum '+shlex.quote(dest)).split()[0];assert actual==digest
   item.update(remote=dest,sha256=digest);staged.append(item)
  entries.append(item)
 manifest.append({'family':family.strip(),'catalog_numbers':ids,'available_file_count':len(matches),'candidates':entries})
 print(family,len(matches),len(entries),flush=True)
out=ROOT/'output/rg280v-apps/rg350-rom-candidates.json';out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('staged',len(staged),'bytes',sum(x['bytes'] for x in staged))
