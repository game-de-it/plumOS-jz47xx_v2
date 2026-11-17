#!/usr/bin/env python3
"""Build pinned standalone sources and package isolated RG280V diagnostic OPKs."""
import argparse
import hashlib
import tarfile
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
    for spec in [p] + p.get('dependencies', []):
        checkout = ROOT / 'output/rg280v-apps/source-repairs' / spec['slug']
        if spec.get('archive_url'):
            archive = checkout.with_suffix(checkout.suffix + '.tar.gz')
            if not archive.exists():
                subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error', spec['archive_url'], '-o', str(archive)], check=True)
            assert hashlib.sha256(archive.read_bytes()).hexdigest() == spec['sha256'], archive
            if not checkout.exists():
                with tarfile.open(archive) as package:
                    for member in package.getmembers():
                        parts = pathlib.PurePosixPath(member.name).parts
                        assert parts and parts[0] == spec['slug'] and '..' not in parts and not member.name.startswith('/'), member.name
                subprocess.run(['tar', '-xzf', str(archive), '-C', str(checkout.parent)], check=True)
            continue
        if not checkout.exists():
            subprocess.run(['git', 'init', str(checkout)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(checkout), 'remote', 'add', 'origin', spec['url']], check=True)
            subprocess.run(['git', '-C', str(checkout), 'fetch', '--depth', '1', 'origin', spec['revision']], check=True)
            subprocess.run(['git', '-C', str(checkout), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
        revision = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        assert revision == spec['revision'], (number, spec['slug'], revision)
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
        command += '{\n' + p['build'] + '\n} >../' + p['slug'] + '-build.log 2>&1\n'
    command += 'cd /workspace\npython3 scripts/build-rg280v-source-repair-opks-pack.py ' + str(number)
    subprocess.run(['docker', 'run', '--rm', '--platform', 'linux/arm64',
        '-v', str(ROOT) + ':/workspace', '-v', 'plumos-jz47xx-rg280v-build:/workspace/output/rg280v',
        '-w', '/workspace', 'plumos-jz47xx-build:bookworm', 'bash', '-euc', command], check=True)
