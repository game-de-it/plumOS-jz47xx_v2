#!/usr/bin/env python3
"""Build pinned standalone sources and package isolated RG280V diagnostic OPKs."""
import argparse
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILES = ROOT / 'assets/rg280v-apps/source-repair-profiles.json'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('numbers', nargs='+', type=int)
parser.add_argument('--pack-only', action='store_true')
args = parser.parse_args()
profiles = json.loads(PROFILES.read_text())
for number in args.numbers:
    p = profiles[str(number)]
    assert re.fullmatch('[a-z0-9-]+', p['slug'])
    src = ROOT / 'output/rg280v-apps/source-repairs' / p['slug']
    if not src.exists():
        subprocess.run(['git', 'clone', p['url'], str(src)], check=True)
        subprocess.run(['git', '-C', str(src), 'checkout', '--detach', p['revision']], check=True)
    revision = subprocess.check_output(['git', '-C', str(src), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == p['revision'], (number, revision)
    if p.get('patch'):
        patch = str(ROOT / p['patch'])
        if subprocess.run(['git', '-C', str(src), 'apply', '--reverse', '--check', patch], capture_output=True).returncode:
            subprocess.run(['git', '-C', str(src), 'apply', '--check', patch], check=True)
            subprocess.run(['git', '-C', str(src), 'apply', patch], check=True)
    cfg = ROOT / f'output/rg280v-apps/source-repair-profile-{number}.json'
    cfg.write_text(json.dumps(dict(p, number=number)))
    command = '''
t=/workspace/output/rg280v/host
export PATH="$t/bin:$PATH"
'''
    if not args.pack_only:
        command += 'cd /workspace/output/rg280v-apps/source-repairs/' + p['slug'] + '\n'
        command += p['build'] + ' >../' + p['slug'] + '-build.log 2>&1\n'
    command += 'cd /workspace\npython3 scripts/build-rg280v-source-repair-opks-pack.py ' + str(number)
    subprocess.run(['docker', 'run', '--rm', '--platform', 'linux/arm64',
        '-v', str(ROOT) + ':/workspace', '-v', 'plumos-jz47xx-rg280v-build:/workspace/output/rg280v',
        '-w', '/workspace', 'plumos-jz47xx-build:bookworm', 'bash', '-euc', command], check=True)
