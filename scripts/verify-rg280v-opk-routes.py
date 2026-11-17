#!/usr/bin/env python3
"""Exercise the real text-frontend launch plans for every installed OPK route."""
import argparse
import json
import os
import pathlib
import re
import shlex
import subprocess
import time
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'output/rg280v-opk-integration/smoke';OUT.mkdir(exist_ok=True)
ADB=['adb','-P','5041','-s','10.1.1.2:5555'];Q=shlex.quote
ENV='PLUMOS_ROOT=/media/data/plumos PLUMOS_SDCARD_ROOT=/media/data/sd2 '
UI='/media/data/plumos/bin/plumos-text-ui'
def shell(s):return subprocess.check_output(ADB+['shell',s],text=True,errors='replace').strip()
def key(k,ms=100,second=None):
    shell(f'/media/data/plumos/bin/rg280v-inject-key /dev/input/event2 {k} {ms}'+(f' {second}' if second else ''))
def stop_native():
    ids=shell("ps | awk '$5 ~ /^\\/opk\\// {print $1}'").split()
    assert all(p.isdigit() for p in ids),ids
    if ids:shell('kill -TERM '+' '.join(ids));time.sleep(.5)
    ids=shell("ps | awk '$5 ~ /^\\/opk\\// {print $1}'").split()
    if ids:shell('kill -KILL '+' '.join(ids))
index=json.loads(shell('cat /media/data/plumos/state/frontend/library-index.json'))
systems={s['id']:s for s in index['systems']}
routes=json.loads((ROOT/'assets/rg280v-apps/standalone-opk-routes.json').read_text())
prefer={'fceux223':'Super Mario Bros.','genesisgx':'Bare Knuckle','gambatte2020':'Super Mario Land','ohboy':'Super Mario Land','temper':'Blazing','smsplusms':'Wonder Boy','smsplusgg':'Puyo','race':'Baseball','oswan':'Puzzle','fba44':'kungfum','atari800':'Caverns','stella':'Asteroids','gngeo':'aof','crocods':'Abyssal'}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only', nargs='+')
args=parser.parse_args()
results=json.loads((OUT/'results.json').read_text()) if args.only else []
for route in routes:
    slug=route['id']
    if args.only and slug not in args.only: continue
    results=[r for r in results if r['id']!=slug]
    system=route['systems'][0];roms=systems[system]['roms']
    choices=[r for r in roms if prefer.get(slug,'').lower() in r['title'].lower()]
    rom=(choices or roms)[0];relative=rom['relative_path']
    command=ENV+UI+' launch '+Q(system)+' '+Q(relative)+' --profile '+Q('standalone:'+slug)+' --no-scan'
    plan=shell(command);assert 'can_execute: yes' in plan,(slug,plan)
    (OUT/(slug+'-plan.txt')).write_text(plan+'\n')
    shell('/media/data/local/init.d/S95frontend stop')
    shell('rm -f /media/data/plumos/Logs/standalone/'+slug+'.log')
    started=time.monotonic();process=subprocess.Popen(ADB+['shell',command+' --execute'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    method='menu';early=False
    try:
        time.sleep(5)
        if process.poll() is None:
            if slug=='unrealspeccy':key(14)
            elif slug=='stella':key(1)
            elif slug=='pokemini':key(29)  # START is the emulated power key.
            elif slug not in {'uae4all','neo4all'}:key(28)
        time.sleep(3)
        early=process.poll() is not None
        if not early:
            subprocess.run(['scripts/capture-rg280v-drm.sh',str(OUT/(slug+'.png'))],cwd=ROOT,env=dict(os.environ,ADB_SERVER_PORT='5041'),capture_output=True,check=True)
            key(1,180,28);time.sleep(.7);key(103);key(29);time.sleep(1)
            if process.poll() is None:
                key(29);time.sleep(.7)
        if process.poll() is None:
            method='terminated-after-capture';stop_native()
        try:stdout=process.communicate(timeout=5)[0]
        except subprocess.TimeoutExpired:
            process.kill();stdout=process.communicate()[0];method='host-command-timeout'
        log=shell('cat /media/data/plumos/Logs/standalone/'+slug+'.log 2>/dev/null || true')
        (OUT/(slug+'.log')).write_text(stdout+'\n'+log)
        exits=[int(x) for x in re.findall(r'PLUMOS_EMULATOR_EXIT=(\d+)',log)]
        errors=re.findall(r'[^\n]*(?:Segmentation fault|not found|corrupted shared library|invalid BIOS|Fatal Error)[^\n]*',log,re.I)
        result=dict(id=slug,system=system,rom=relative,plan_ok=True,early_exit=early,exit_method=method,
                    child_exits=exits,errors=errors,elapsed_s=round(time.monotonic()-started,1))
    finally:
        shell('/media/data/local/init.d/S95frontend start')
    results.append(result);(OUT/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False),flush=True)
print('Completed',len(results),'formal launch routes')
