"""Storage helpers: test ROM payloads live on SD2; runtime state stays on SD1."""
import contextlib
import hashlib
import pathlib
import shlex
import subprocess

ADB = ['adb', '-P', '5041', '-s', '10.1.1.2:5555']
ROM_ROOT = '/media/data/sd2/.plumos-rg350-tests-20261118/relocated'
CANDIDATES = ROM_ROOT + '/rom-candidates'

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
