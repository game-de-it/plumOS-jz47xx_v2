"""Storage helpers: test ROM payloads live on SD2; runtime state stays on SD1."""
import contextlib
import hashlib
import os
import pathlib
import shlex
import subprocess

ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
ROM_ROOT = '/media/data/sd2/.plumos-rg350-tests-20261118/relocated'
CANDIDATES = ROM_ROOT + '/rom-candidates'

def host_rom_root():
    root = os.environ.get("PLUMOS_ROM2_ROOT")
    if not root:
        raise SystemExit("Set PLUMOS_ROM2_ROOT to the test ROM directory.")
    return pathlib.Path(root)


def shell(command):
    return subprocess.check_output(ADB + ['shell', command], text=True, errors='replace').strip()

@contextlib.contextmanager
def writable_sd2():
    mount = next(x for x in shell('cat /proc/mounts').splitlines() if x.split()[1] == '/media/data/sd2')
    assert mount.split()[0] == '/dev/mmcblk1p1', mount
    readonly = 'ro' in mount.split()[3].split(',')
    if readonly:
        shell('mount -o remount,rw /media/data/sd2')
    try:
        yield
    finally:
        shell('sync')
        if readonly:
            shell('mount -o remount,ro /media/data/sd2')

def stage_file(source, target):
    source = pathlib.Path(source)
    assert target.startswith('/media/data/sd2/.plumos-rg350-tests-20261118/'), target
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    current = shell('sha256sum ' + shlex.quote(target) + ' 2>/dev/null || true').split()
    if not current or current[0] != digest:
        with writable_sd2():
            shell('mkdir -p ' + shlex.quote(str(pathlib.PurePosixPath(target).parent)))
            subprocess.run(ADB + ['push', str(source), target], capture_output=True, check=True)
            assert shell('sha256sum ' + shlex.quote(target)).split()[0] == digest
    return digest


def stage_tree(source, target, manifest_path):
    """Transfer a complete game once, then verify every file before restoring SD2."""
    source = pathlib.Path(source)
    dest = pathlib.PurePosixPath(target)
    assert target.startswith(ROM_ROOT + '/'), target
    assert source.is_dir() and source.name == dest.name, (source, target)
    records = []
    for path in sorted(source.rglob('*')):
        if path.is_file():
            relative = path.relative_to(source).as_posix()
            assert '\n' not in relative and '\r' not in relative and '\\' not in relative
            records.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + relative)
    assert records, source
    manifest_path = pathlib.Path(manifest_path)
    manifest_path.write_text('\n'.join(records) + '\n')
    remote_manifest = '/tmp/rg350-stage-tree.sha256'
    with writable_sd2():
        shell('mkdir -p ' + shlex.quote(str(dest.parent)))
        subprocess.run(ADB + ['push', str(source), str(dest.parent)], check=True, capture_output=True)
        subprocess.run(ADB + ['push', str(manifest_path), remote_manifest], check=True, capture_output=True)
        shell('cd ' + shlex.quote(target) + ' && sha256sum -c ' + remote_manifest + ' >/tmp/rg350-stage-tree.result')
    return len(records)
