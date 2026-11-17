#!/usr/bin/env python3
"""Use emulator-specific controls instead of mistaking START menus for gameplay."""
import pathlib,json,subprocess,hashlib,shlex
R=pathlib.Path(__file__).resolve().parents[1]
subprocess.run(['adb','-P','5041','connect','10.1.1.2:5555'],check=True)
groups=json.loads((R/'output/rg280v-apps/rg350-rom-candidates.json').read_text())
adb=['adb','-P','5041','-s','10.1.1.2:5555']
# The original Atari 2600 choices are quiet board/adventure games. Add three
# action games so that sound is exercised rather than calling silence a pass.
stella=next(g for g in groups if 28 in g['catalog_numbers'])
for i,name in enumerate(['Asteroids.bin','Centipede.bin','Breakout.bin'],4):
 src=pathlib.Path('<local-path>')/name
 dest=f'/media/data/local/rg350-rom-candidates/atari2600/{i:02d}.bin'
 subprocess.run(adb+['push',str(src),dest],capture_output=True,check=True)
 actual=subprocess.check_output(adb+['shell','sha256sum '+shlex.quote(dest)],text=True).split()[0]
 assert actual==hashlib.sha256(src.read_bytes()).hexdigest()
 stella['candidates'].append(dict(source='ATARI/2600/'+name,remote=dest))
profiles={
 5:['2:2:120','4:29:500','7:106:1200','10:29:1200'],
 23:['3:28:120','5:29:500','7:106:1200','10:29:1500','13:105:1000'],
 28:['3:1:120','5:29:500','7:106:1200','10:29:1500','13:103:1000'],
 22:['3:29:150','5:29:150','8:28:150','10:29:150'],
 50:['3:28:150','6:29:500','9:106:1200','12:29:500'],
 55:['4:29:500','7:106:1200','10:29:500'],
 48:['3:28:150','6:28:150','9:28:150','12:29:500']}
for n,events in profiles.items():
 g=next(g for g in groups if n in g['catalog_numbers'])
 for i,rom in enumerate(g['candidates'],1):
  if not rom['remote']:continue
  if n==50 and '/03.' in rom['remote']:continue # The original inventory misidentified a BIOS as a game.
  tag=f'rom-retest-play-20261118-{n:02d}-{i}'
  prior=R/f'output/rg280v-apps/rg350-device-audit-{tag}/results.jsonl'
  if prior.exists() and any(not json.loads(line).get('error') for line in prior.read_text().splitlines()):continue
  args=['python3',str(R/'scripts/audit-rg350-opks-device.py'),'--only',str(n),'--seconds','25','--screenshot-delay','21','--tag',tag,'--rom',f'{n}={rom["remote"]}']
  if n in (22,50):args+=['--opk',f'{n}={R}/output/rg280v-apps/missing-rom-opks/{n:02d}.opk']
  for e in events:args+=['--key-event',e]
  subprocess.run(args,cwd=R,check=True)
