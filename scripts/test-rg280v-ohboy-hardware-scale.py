#!/usr/bin/env python3
"""Exercise each OhBoy hardware mode in an isolated HOME on the RG280V."""
import subprocess,time,shlex,pathlib,os
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
adb=['adb','-P','5041','-s','10.1.1.2:5555'];out=pathlib.Path('output/rg280v-apps/ohboy-scale-test');out.mkdir(exist_ok=True)
def sh(s):return subprocess.check_output(adb+['shell',s],text=True)
def key(code,second=None):sh(f'/media/data/plumos/bin/rg280v-inject-key /dev/input/event2 {code} 120'+(f' {second}' if second else ''))
sh('/media/data/local/init.d/S95frontend stop')
try:
 for mode in [5,6,7]:
  home=f'/media/data/local/rg350-rom-candidates/scale-test-{mode}'
  sh(f'mkdir -p {home}/.ohboy; echo "set upscaler {mode}" > {home}/.ohboy/video.rc')
  log=f'/media/data/local/rg350-rom-candidates/log/ohboy-scale-{mode}.log'
  command=f'HOME={home} LD_LIBRARY_PATH=/media/data/plumos/lib SDL_VIDEODRIVER=kmsdrm /usr/bin/opkrun /media/data/local/rg350-rom-candidates/opk/49-scale-test.opk /media/data/local/rg350-rom-candidates/gb/01.gb >{log} 2>&1; echo RC:$?'
  proc=subprocess.Popen(adb+['shell',command],stdout=subprocess.PIPE)
  time.sleep(3);assert sh('pidof ohboy.gcw0').strip(),sh('cat '+log)
  subprocess.run(['scripts/capture-rg280v-drm.sh',str(out/f'{mode}-game.png')],check=True,capture_output=True)
  for i in range(2):
   key(1,28);time.sleep(.7);key(29);time.sleep(.7)
   assert sh('pidof ohboy.gcw0').strip()
  key(1,28);time.sleep(.7)
  subprocess.run(['scripts/capture-rg280v-drm.sh',str(out/f'{mode}-menu.png')],check=True,capture_output=True)
  key(103);key(29)
  result=proc.communicate(timeout=10)[0].decode();assert 'RC:0' in result,result
  text=sh('cat '+log);(out/f'{mode}.log').write_text(text)
  print(mode,result,text.strip(),flush=True)
finally:
 sh('/media/data/local/init.d/S95frontend restart')
 for _ in range(10):
  fe=sh('pidof plumos-controller-ui').strip()
  if fe: break
  time.sleep(1)
 assert fe, 'FE did not restart'
 print('FE',fe)
