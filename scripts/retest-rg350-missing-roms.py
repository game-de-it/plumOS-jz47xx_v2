#!/usr/bin/env python3
"""Retest previously unassigned OPKs with complete data in an isolated device tree."""
import pathlib,json,subprocess,shlex,hashlib,zipfile,time
from rg350_test_rom_storage import writable_sd2
R=pathlib.Path(__file__).resolve().parents[1];NAS=pathlib.Path('<local-path>');base='/media/data/local/rg350-missing-rom-retest';adb=['adb','-P','5041','-s','10.1.1.2:5555']
subprocess.run(['adb','-P','5041','connect','10.1.1.2:5555'],check=True)
def shell(s):
 if s.startswith('rm ') and base in s:
  with writable_sd2():return subprocess.check_output(adb+['shell',s],text=True,errors='replace')
 return subprocess.check_output(adb+['shell',s],text=True,errors='replace')
def push(src,dest):
 with writable_sd2():
  if src.is_file():
   free=int(shell('df -k /media/data').splitlines()[-1].split()[3])*1024
   if src.stat().st_size > free-32*1024*1024:raise RuntimeError('Insufficient SD1 space for '+str(src))
  shell('mkdir -p '+shlex.quote(str(pathlib.PurePosixPath(dest).parent)))
  subprocess.run(adb+['push',str(src),dest],check=True,capture_output=True)
  if src.is_file():assert shell('sha256sum '+shlex.quote(dest)).split()[0]==hashlib.sha256(src.read_bytes()).hexdigest()
def done(n,i):
 p=R/f'output/rg280v-apps/rg350-device-audit-rom-retest-extra-20261118-{n:02d}-{i}/results.jsonl'
 return p.exists() and any(not json.loads(line).get('error') for line in p.read_text().splitlines())
def run(n,rom,i,override=True):
 if done(n,i): return
 args=['python3',str(R/'scripts/audit-rg350-opks-device.py'),'--only',str(n),'--seconds','25','--screenshot-delay','21','--start-presses','6','--tag',f'rom-retest-extra-20261118-{n:02d}-{i}','--rom',f'{n}={rom}','--extra-lib-dir',base+'/lib']
 p=R/f'output/rg280v-apps/missing-rom-opks/{n:02d}.opk'
 if override and p.exists():args+=['--opk',f'{n}={p}']
 subprocess.run(args,cwd=R,check=True)
# Only test data within this isolated tree is removed between large cases.
for n,src,dest in [(1,'bios/panafz1.bin','/.3doh/bios.bin'),(6,'bios/tos.img','/.DCaSTaway/bios/rom'),(30,'bios/kick13.rom','/.uae4all/kick.rom'),(60,'bios/kick13.rom','/.uae4all/kick.rom'),(42,'bios/exec.bin','/bios/exec.bin'),(42,'bios/grom.bin','/bios/grom.bin')]:push(NAS/src,base+f'/home-{n:02d}'+dest)
# BioFury is the only available 3DO title.
if not done(1,1):
 push(NAS/'_etc/3do/biofury.iso',base+'/large/biofury.iso');run(1,base+'/large/biofury.iso',1);shell('rm -f '+base+'/large/biofury.iso')
# EasyRPG requires the complete project, not just its LDB file.
if not done(10,1):
 push(NAS/'_etc/EASYRPG/TurnedIntoAGirl',base+'/large/TurnedIntoAGirl');run(10,base+'/large/TurnedIntoAGirl/RPG_RT.ldb',1);shell('rm -rf '+base+'/large/TurnedIntoAGirl')
# Three OpenBOR games that fit the available SD1 space, one at a time.
for i,f in enumerate(['Crisis Evil 1.pak','Dragon Ball [v.3.0 Build 4086].PAK','Rushing Beat.pak'],1):
 if done(17,i): continue
 push(NAS/'openbor'/f,base+'/large/test.pak');run(17,base+'/large/test.pak',i);shell('rm -f '+base+'/large/test.pak')
# Extract the real Game & Watch cartridge; the frontend takes .mgw, not ZIP.
for i,f in enumerate(['Snoopy (Nintendo, Table Top).zip','Tennis Menace.zip'],1):
 with zipfile.ZipFile(NAS/'_etc/gameandwatch'/f) as z:
  member=next(x for x in z.namelist() if x.lower().endswith('.mgw'));data=z.read(member)
 p=R/f'output/rg280v-apps/gw-retest-{i}.mgw';p.write_bytes(data);d=base+f'/gw/{i}.mgw';push(p,d);run(41,d,i,False)
run(42,'/media/data/local/rg350-rom-candidates/intv/01.bin',1)
# CD data is tiny for this PC-FX homebrew; include its referenced BIN.
push(NAS/'_etc/pcfx/SimpleBattle_FX',base+'/large/SimpleBattle_FX');run(47,base+'/large/SimpleBattle_FX/simplebattle.cue',1);shell('rm -rf '+base+'/large/SimpleBattle_FX')
# VICE receives an uncompressed disk rather than a ROM browser ZIP.
p=R/'output/rg280v-apps/c64-pacmania-retest.prg'
with zipfile.ZipFile(NAS/'_etc/c64/Pacmania.zip') as z:
 print('C64 ZIP',z.namelist(),flush=True)
 member=next((m for m in z.namelist() if m.lower().endswith(('.d64','.prg','.t64','.tap'))),None)
 if member:
  p=p.with_suffix(pathlib.Path(member).suffix);p.write_bytes(z.read(member));d=base+'/c64/'+p.name;push(p,d);run(31,d,1)
run(31,'/media/data/local/rg350-rom-candidates/c64/02.d64',2)
# A disk environment for UAE4All, plus the game ADF.
for n in [30,60]:
 for i in [1,2]:run(n,f'/media/data/local/rg350-rom-candidates/amiga/{i:02d}.adf',i)
# Neo Geo arcade uses a matching BIOS, outside the production BIOS directory.
with zipfile.ZipFile(NAS/'bios/neogeo.zip') as z:
 for name in z.namelist():
  if '/' in name:continue
  p=R/'output/rg280v-apps/gngeo-bios-stage'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(z.read(name));push(p,base+'/home-39/bios/'+name)
for i,f in enumerate(['aof.zip','aof2.zip','aof3.zip'],1):
 push(NAS/'_etc/neogeo/ART OF FIGHTING'/f,base+'/large/'+f);run(39,base+'/large/'+f,i);shell('rm -f '+base+'/large/'+f)
# DOS executable folders must be mounted, not passed as a ZIP to DOSBox.
for i,(f,exe) in enumerate([('DOSBOX_ALIENBREED.ZIP','ALIEN.EXE'),('DOSBOX_DOOM.ZIP','DOOM.EXE'),('DOSBOX_TV.ZIP','TV.EXE')],1):
 local=R/f'output/rg280v-apps/dos-retest-{i}';local.mkdir(exist_ok=True)
 with zipfile.ZipFile(NAS/'pc'/f) as z:
  for item in z.infolist():
   if '..' in pathlib.PurePosixPath(item.filename).parts or item.filename.startswith('/'):raise RuntimeError('unsafe archive path')
  z.extractall(local)
 dest=base+f'/dos/game-{i}';push(local,dest)
 cfg=R/f'output/rg280v-apps/dos-retest-{i}.conf'
 cfg.write_text('[cpu]\ncycles=auto\n[autoexec]\nmount c '+dest+'\nc:\n'+exe+'\nexit\n')
 remote=base+f'/dos/game-{i}.conf';push(cfg,remote);run(7,remote,i)
 shell('rm -rf '+dest)
# Smaller complete ScummVM games fit on SD1. The 215 MB Baseball set does not.
for i,f in enumerate(["Monkey Island 2 LeChuck's Revenge (Floppy DOS VGA)",'BASS-Floppy-1.3'],1):
 dest=base+'/large/'+f;push(NAS/'scummvm'/f,dest);run(56,dest,i);shell('rm -rf '+shlex.quote(dest))
# Neo Geo CD is tested separately with the complete WAV data on SD2.
# The ST sample is Lattice C, not a game; record only boot/display reachability.
run(6,'/media/data/local/rg350-rom-candidates/atarist/01.st',1)
print('extra tests finished',flush=True)
