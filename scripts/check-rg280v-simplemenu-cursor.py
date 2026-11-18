#!/usr/bin/env python3
"""Replay fast/queued GPIO inputs against SimpleMenu without changing user state."""
import json
import argparse
import pathlib
import re
import shlex
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--theme-index', type=int, default=0,
                    help='Installed theme index (prefer --theme-name after adding themes)')
parser.add_argument('--theme-name', help='Resolve an installed theme by name, without assuming its index')
args = parser.parse_args()
label = args.theme_name or str(args.theme_index)
assert re.fullmatch(r'[A-Za-z0-9_-]+', label), 'Unsafe output label'
OUT = ROOT / f'output/rg280v-simplemenu/input-check-theme-{label}'
OUT.mkdir(parents=True, exist_ok=True)
ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
BASE = '/media/data/plumos'
TMP = '/tmp/plumos-simplemenu-input-check'
INJECT = BASE + '/bin/rg280v-inject-key /dev/input/event2 '
Q = shlex.quote


def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True).strip()


if args.theme_name:
    names = sorted(shell('for d in ' + BASE + '/home/simplemenu/.simplemenu/themes/320x240/*; '
                         'do if test -d "$d"; then echo "${d##*/}"; fi; done').splitlines(), key=str.lower)
    args.theme_index = names.index(args.theme_name)


def key(code, milliseconds=50):
    shell(INJECT + str(code) + ' ' + str(milliseconds))
    time.sleep(0.08)


def capture_screen(name):
    for attempt in range(3):
        time.sleep(0.15)
        capture = subprocess.run(['env', 'ADB_SERVER_PORT=5041',
                                  str(ROOT / 'scripts/capture-rg280v-drm.sh'),
                                  str(OUT / name)], stdout=subprocess.DEVNULL)
        if capture.returncode == 0:
            return
        assert attempt < 2, 'Unable to capture settled display'


log = OUT / 'events.log'


def events():
    result = []
    for line in log.read_text(errors='replace').splitlines():
        if line.startswith('SM_INPUT after '):
            fields = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
            if {'type', 'key', 'state', 'setting', 'section', 'choice'} <= fields.keys():
                result.append(fields)
    return result


def downs(start=0):
    return [e for e in events()[start:] if e['type'] == 2]


def reset_settings():
    key(56)  # Settings -> game list.
    key(28)  # Open settings with Session/quit selected.
    assert events()[-1]['state'] == 3 and events()[-1]['setting'] == 0


assert not shell("ps | awk '$5==\"./simplemenu\" {print $1}'"), 'Exit SimpleMenu before testing'
shell('/media/data/local/init.d/S95frontend stop')
pid = None
process = None
results = []
try:
    home = TMP + '/.simplemenu'
    shell('mkdir -p ' + home + '/apps ' + home + '/games ' + home + '/tmp ' + home + '/rom_preferences; '
          'ln -sfn ' + BASE + '/home/simplemenu/.simplemenu/themes ' + home + '/themes; '
          'ln -sfn ' + BASE + '/home/simplemenu/.simplemenu/section_groups ' + home + '/section_groups; '
          'cp ' + BASE + '/home/simplemenu/.simplemenu/config.ini ' + home + '/config.ini; '
          ': >' + home + '/favorites.sav')
    state = OUT / 'initial-state.sav'
    state.write_text(f'10;\n1;\n0;\n1;\n1;\n{args.theme_index};\n0;\n1;\n0;\n3;\n')
    subprocess.run(ADB + ['push', str(state), home + '/last_state.sav'], check=True, capture_output=True)
    command = ('cd ' + BASE + '/simplemenu; echo $$ >' + TMP + '/pid; exec env '
               'HOME=' + Q(TMP) + ' PLUMOS_ROOT=' + Q(BASE) + ' PLUMOS_SDCARD_ROOT=/media/data/sd2 '
               'SDL_VIDEODRIVER=kmsdrm SDL_VIDEO_KMSDRM_SCALING_MODE=0 LD_LIBRARY_PATH=' + BASE + '/lib '
               'PLUMOS_SIMPLEMENU_INPUT_TRACE=1 ./simplemenu')
    with log.open('wb') as stream:
        process = subprocess.Popen(ADB + ['shell', command], stdout=stream, stderr=subprocess.STDOUT)
        time.sleep(1)
        pid = shell('cat ' + TMP + '/pid')
        assert pid.isdigit() and int(pid) > 1
        assert shell('cat /proc/' + pid + '/comm') == 'simplemenu'
        key(28, 100)
        deadline = time.monotonic() + 5
        while not events() and time.monotonic() < deadline:
            assert process.poll() is None, 'SimpleMenu exited during startup'
            time.sleep(0.1)
        assert events()[-1]['state'] == 3 and events()[-1]['setting'] == 0

        start = len(events())
        shell('kill -STOP ' + pid + '; ' + INJECT + '108 10; ' + INJECT +
              '103 180 & keypid=$!; sleep 0.05; kill -CONT ' + pid + '; wait "$keypid"')
        time.sleep(0.15)
        states = [e['setting'] for e in downs(start)]
        assert states == [1, 0], ('queued DOWN then UP', states)
        results.append(dict(case='queued opposite directions', settings=states))

        reset_settings()
        start = len(events())
        shell('kill -STOP ' + pid + '; for n in 1 2 3 4 5 6; do ' + INJECT +
              '108 10; done; kill -CONT ' + pid)
        time.sleep(0.15)
        states = [e['setting'] for e in downs(start)]
        assert states == [1, 2, 3, 4, 5, 6], ('six queued taps', states)
        results.append(dict(case='six queued taps', settings=states))

        reset_settings()
        start = len(events())
        shell(INJECT + '108 180 & keypid=$!; sleep 0.05; ' + INJECT + '57 30; wait "$keypid"')
        time.sleep(0.1)
        sample = downs(start)
        assert [(e['key'], e['setting']) for e in sample] == [(274, 1), (32, 1)], sample
        results.append(dict(case='another button while DOWN held', settings=[e['setting'] for e in sample]))

        reset_settings()
        start = len(events())
        key(108, 650)
        sample = downs(start)
        assert 5 <= len(sample) <= 7, sample
        intervals = [b['tick'] - a['tick'] for a, b in zip(sample, sample[1:])]
        assert intervals[0] >= 240 and all(n >= 75 for n in intervals[1:]), intervals
        count = len(downs(start))
        time.sleep(0.25)
        assert len(downs(start)) == count, 'Movement continued after release'
        results.append(dict(case='hold and release', moves=count, intervals_ms=intervals))

        reset_settings()
        start = len(events())
        key(57, 650)
        assert len(downs(start)) == 1 and events()[-1]['setting'] == 0
        results.append(dict(case='buttons do not autorepeat', keydowns=len(downs(start))))

        key(56)  # Game list.
        assert events()[-1]['state'] == 0
        section = events()[-1]['section']
        shell(INJECT + '56 180 & keypid=$!; sleep 0.05; ' + INJECT + '108 30; wait "$keypid"')
        time.sleep(0.15)
        assert events()[-1]['state'] == 0 and events()[-1]['section'] == section + 1
        results.append(dict(case='native B + DOWN combination', section=events()[-1]['section']))

        key(56)
        assert events()[-1]['state'] == 4  # System selection.
        # Compare logical selection against the captured theme image. Theme
        # artwork can contain its own fixed list/marker, unlike the real INIs.
        navigation = []
        for step in range(13):
            if step:
                before = len(events())
                key(108)
                deadline = time.monotonic() + 5
                while not any(e['type'] == 3 and e['key'] == 274
                              for e in events()[before:]):
                    assert process.poll() is None, 'SimpleMenu exited during navigation'
                    assert time.monotonic() < deadline, 'DOWN release was not processed'
                    time.sleep(0.02)
                assert len(downs(before)) == 1, 'One tap advanced multiple times'
            navigation.append(dict(step=step, group=events()[-1]['group'],
                                   section=events()[-1]['section']))
            capture_screen(f'section-{step:02d}.png')
        results.append(dict(case='system selection artwork comparison',
                            theme_index=args.theme_index, navigation=navigation))
        start = len(events())
        key(29, 650)
        assert process.poll() is None and events()[-1]['state'] == 0
        assert len(downs(start)) == 1, 'Holding A entered more than one screen'
        results.append(dict(case='hold A enters once without launching game', keydowns=len(downs(start))))
        rom_moves = []
        for code in [108] * 5 + [103] * 5:
            before = len(events())
            key(code)
            deadline = time.monotonic() + 5
            sym = 274 if code == 108 else 273
            while not any(e['type'] == 3 and e['key'] == sym for e in events()[before:]):
                assert time.monotonic() < deadline, 'ROM-list key release was not processed'
                time.sleep(0.02)
            assert len(downs(before)) == 1
            assert events()[-1]['state'] == 0
            rom_moves.append(dict(key=code, game=events()[-1]['game']))
        results.append(dict(case='ROM list down five up five', navigation=rom_moves))
        capture_screen('rom-list.png')
finally:
    if pid:
        shell('kill -CONT ' + pid + ' 2>/dev/null || true; kill -TERM ' + pid + ' 2>/dev/null || true')
    if process:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            shell('kill -KILL ' + pid + ' 2>/dev/null || true')
            process.wait(timeout=5)
    shell('/media/data/local/init.d/S95frontend start; sleep 1')
(OUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
