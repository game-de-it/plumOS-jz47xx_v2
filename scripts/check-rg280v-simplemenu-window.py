#!/usr/bin/env python3
"""Exercise dynamic hierarchy, Japanese text and real emulator return in temporary HOME."""
import json
import pathlib
import re
import shlex
import subprocess
import time
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--theme-name', choices=('CrystalMenu', 'CrystalMenu12'), default='CrystalMenu')
args = parser.parse_args()
suffix = '' if args.theme_name == 'CrystalMenu' else '-' + args.theme_name
OUT = ROOT / ('output/rg280v-simplemenu/window-check' + suffix)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'results.json').unlink(missing_ok=True)
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/plumos'
HOME = '/tmp/plumos-simplemenu-window-check'
INJECT = BASE + '/bin/rg280v-inject-key /dev/input/event2 '
Q = shlex.quote


def shell(cmd):
    return subprocess.check_output(ADB + ['shell', cmd], text=True).strip()


def events():
    parsed = [{k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
              for line in (OUT / 'events.log').read_text(errors='replace').splitlines()
              if line.startswith('SM_INPUT after ')]
    return [e for e in parsed if {'type', 'key', 'state', 'group', 'section', 'game', 'choice'} <= e.keys()]


def key(code, second=None):
    before = len(events())
    shell(INJECT + str(code) + ' 120' + (' ' + str(second) if second else ''))
    symbols = {29: 306, 56: 308, 28: 13, 108: 274, 103: 273, 105: 276, 106: 275, 57: 32, 42: 304}
    deadline = time.monotonic() + 5
    if second is None:
        while not any(e['type'] == 3 and e['key'] == symbols[code] for e in events()[before:]):
            assert time.monotonic() < deadline, ('key release timeout', code)
            time.sleep(0.02)
    time.sleep(0.15)
    return events()[-1]


def capture(name):
    for attempt in range(3):
        time.sleep(0.2)
        result = subprocess.run(['env', 'ADB_SERVER_PORT=5041',
                                 str(ROOT / 'scripts/capture-rg280v-drm.sh'), str(OUT / name)],
                                stdout=subprocess.DEVNULL)
        if result.returncode == 0:
            return
        assert attempt < 2, 'Screenshot failed'


assert not shell("ps | awk '$5==\"./simplemenu\" {print $1}'"), 'Exit SimpleMenu first'
names = sorted(shell('for d in ' + BASE + '/home/simplemenu/.simplemenu/themes/320x240/*; '
                     'do if test -d "$d"; then echo "${d##*/}"; fi; done').splitlines(), key=str.lower)
index = names.index(args.theme_name)
shell('/media/data/local/init.d/S95frontend stop')
process = None
pid = None
try:
    folder = HOME + '/.simplemenu'
    shell('mkdir -p ' + folder + '/apps ' + folder + '/games ' + folder + '/tmp ' + folder + '/rom_preferences; '
          'ln -sfn ' + BASE + '/home/simplemenu/.simplemenu/themes ' + folder + '/themes; '
          'ln -sfn ' + BASE + '/home/simplemenu/.simplemenu/section_groups ' + folder + '/section_groups; '
          'cp ' + BASE + '/home/simplemenu/.simplemenu/config.ini ' + folder + '/config.ini; : >' + folder + '/favorites.sav')
    state = OUT / 'initial-state.sav'
    state.write_text(f'10;\n1;\n0;\n1;\n1;\n{index};\n0;\n1;\n0;\n3;\n')
    subprocess.run(ADB + ['push', str(state), folder + '/last_state.sav'], check=True, capture_output=True)
    cmd = ('cd ' + BASE + '/simplemenu; echo $$ >' + HOME + '/pid; exec env HOME=' + Q(HOME) +
           ' PLUMOS_ROOT=' + BASE + ' PLUMOS_SDCARD_ROOT=/media/data/sd2 '
           'SDL_VIDEODRIVER=kmsdrm SDL_VIDEO_KMSDRM_SCALING_MODE=0 LD_LIBRARY_PATH=' + BASE + '/lib '
           'PLUMOS_SIMPLEMENU_INPUT_TRACE=1 ./simplemenu')
    with (OUT / 'events.log').open('wb') as stream:
        process = subprocess.Popen(ADB + ['shell', cmd], stdout=stream, stderr=subprocess.STDOUT)
        time.sleep(1)
        pid = shell('cat ' + HOME + '/pid')
        assert pid.isdigit() and int(pid) > 1
        capture('nes-roms.png')
        assert key(56)['state'] == 4
        capture('systems.png')
        assert key(56)['state'] == 2
        groups = []
        for step in range(4):
            capture(f'category-{step}.png')
            event = key(108)
            groups.append(event['group'])
            assert event['group'] == (2 + step) % 4 and event['state'] == 2
        assert key(29)['state'] == 4
        assert key(108)['section'] == 1
        assert key(103)['section'] == 0
        assert key(29)['state'] == 0
        last = key(103)['game']
        assert last > 0
        capture('japanese-rom.png')
        assert key(108)['game'] == 0
        # Exercise normal settings-based switching, including resource teardown.
        assert key(28)['state'] == 3
        key(108)
        for _ in range(index):
            key(105)
        key(56)
        capture('switched-0A.png')
        assert key(28)['state'] == 3
        key(108)
        for _ in range(index):
            key(106)
        key(56)
        capture('switched-back.png')
        assert events()[-1]['state'] == 0
        shell(INJECT + '29 100')  # exec replaces SimpleMenu; no SimpleMenu KEYUP trace.
        time.sleep(3)
        assert shell("ps | grep '[/]opk/fceux'"), 'Expected registered NES FCEUX runtime'
        capture('game.png')
        shell(INJECT + '1 200 28')
        time.sleep(0.2)
        capture('emulator-menu.png')
        shell(INJECT + '103 100; ' + INJECT + '29 100')
        deadline = time.monotonic() + 8
        while 'SimpleMenu emulator exit=0' not in (OUT / 'events.log').read_text(errors='replace'):
            assert time.monotonic() < deadline, 'Emulator did not exit normally'
            time.sleep(0.1)
        time.sleep(2)
        assert shell('cat /proc/' + pid + '/comm') == 'simplemenu'
        capture('returned.png')
        assert key(108)['state'] == 0 and events()[-1]['game'] == 1
        assert key(57)['state'] == 0
        capture('favorite-added.png')
        assert key(42)['state'] == 4
        assert key(29)['state'] == 0
        capture('favorites.png')
        assert key(42)['state'] == 4
        assert key(29)['state'] == 0
        (OUT / 'results.json').write_text(json.dumps(dict(
            category_groups=groups, japanese_last_game=last,
            theme_switch_roundtrip=True, game_exit=0, returned_input=True,
            favorites_roundtrip=True), indent=2) + '\n')
finally:
    if pid:
        shell('kill -TERM ' + pid + ' 2>/dev/null || true')
    if process:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            shell('kill -KILL ' + pid + ' 2>/dev/null || true')
            process.wait(timeout=5)
    shell('/media/data/local/init.d/S95frontend start; sleep 1')
