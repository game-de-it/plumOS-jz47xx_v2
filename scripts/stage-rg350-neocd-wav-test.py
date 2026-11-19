#!/usr/bin/env python3
"""Copy the complete Fatal Fury WAV test set into one new, isolated SD2 directory."""
import hashlib,json,pathlib,shlex,subprocess,signal,time
from rg350_test_rom_storage import host_rom_root
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=(host_rom_root() / '_etc/neogeocd/Fatal Fury WAV')
DEST='/media/data/sd2/.plumos-rg350-tests-20261118/Fatal Fury WAV'
ADB=['adb','-P','5041','-s','10.1.1.2:5555']
def sh(s):
 for attempt in range(3):
  try:return subprocess.check_output(ADB+['shell',s],text=True,errors='replace')
  except subprocess.CalledProcessError:
   if attempt==2:raise
   subprocess.run(['adb','-P','5041','connect','10.1.1.2:5555'],capture_output=True,timeout=15)
   time.sleep(1)
def interrupted(signum,frame):raise SystemExit(128+signum)
signal.signal(signal.SIGTERM,interrupted)
subprocess.run(['adb','-P','5041','connect','10.1.1.2:5555'],check=True)
files=sorted(p for p in SOURCE.iterdir() if p.is_file())
if not files:raise RuntimeError('WAV source is not mounted')
mount=next(l for l in sh('cat /proc/mounts').splitlines() if l.split()[1]=='/media/data/sd2')
assert mount.split()[0]=='/dev/mmcblk1p1' and 'ro' in mount.split()[3].split(','),mount
free=int(sh('df -k /media/data/sd2').splitlines()[-1].split()[3])*1024
assert free > sum(p.stat().st_size for p in files)+64*1024*1024
# A marker limits resumed writes to a directory created by this script.
marker=DEST+'/.plumos-wav-test'
state=sh('if [ -e '+shlex.quote(DEST)+' ]; then test -f '+shlex.quote(marker)+' && echo resume || echo conflict; else echo new; fi').strip()
if state=='conflict':raise RuntimeError('Destination already contains unowned data')
results=[]
try:
 sh('mount -o remount,rw /media/data/sd2')
 sh('mkdir -p '+shlex.quote(DEST)+'; touch '+shlex.quote(marker))
 for i,p in enumerate(files,1):
  dest=DEST+'/'+p.name;digest=hashlib.sha256(p.read_bytes()).hexdigest()
  remote=sh('sha256sum '+shlex.quote(dest)+' 2>/dev/null || true').split()
  if not remote or remote[0]!=digest:
   subprocess.run(ADB+['push',str(p),dest],capture_output=True,check=True)
  assert sh('sha256sum '+shlex.quote(dest)).split()[0]==digest
  results.append(dict(name=p.name,bytes=p.stat().st_size,sha256=digest))
  print(f'{i}/{len(files)} verified {p.name}',flush=True)
 sh('sync')
finally:
 sh('mount -o remount,ro /media/data/sd2')
 final=next(l for l in sh('cat /proc/mounts').splitlines() if l.split()[1]=='/media/data/sd2')
 assert 'ro' in final.split()[3].split(','),final
out=ROOT/'output/rg280v-apps/neocd-wav-stage-status.json'
out.write_text(json.dumps(dict(source=str(SOURCE),destination=DEST,mount_before=mount,mount_after=final,files=results),ensure_ascii=False,indent=2))
print('Complete; SD2 restored read-only',flush=True)
