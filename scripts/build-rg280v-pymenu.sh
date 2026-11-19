#!/bin/bash
# Private Python/Pygame environment; does not rebuild or flash the OS image.
set -euo pipefail
cd "$(dirname "$0")/.."
work="$PWD/output/rg280v-pymenu"
mkdir -p "$work"
if [ ! -d "$work/source/.git" ]; then git clone https://github.com/JackD83/PyMenu.git "$work/source"; fi
if [ ! -d "$work/pygame-source/.git" ]; then git clone https://github.com/pygame/pygame.git "$work/pygame-source"; fi
[ "$(git -C "$work/source" rev-parse HEAD)" = 68ceb9d17c4016d68abd6cd7c382eea5cbfd2009 ] || git -C "$work/source" checkout 68ceb9d17c4016d68abd6cd7c382eea5cbfd2009
[ "$(git -C "$work/pygame-source" rev-parse HEAD)" = 34f25f42f7c44774460eb8cbc8de19c1903e1e66 ] || git -C "$work/pygame-source" checkout 34f25f42f7c44774460eb8cbc8de19c1903e1e66
for pair in 'source:0001-plumos-runtime-and-launch.patch' 'pygame-source:0002-pygame-python3-pixel-coordinates.patch' 'source:0003-missing-artwork-and-clean-return.patch'; do
 repo=${pair%%:*}; patch="$PWD/patches/pymenu/${pair#*:}"
 if ! git -C "$work/$repo" apply --reverse --check "$patch" 2>/dev/null; then git -C "$work/$repo" apply "$patch"; fi
done
docker run --rm --platform linux/arm64 -i -v "$PWD:/workspace" \
 -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v -w /workspace \
 plumos-jz47xx-build:bookworm bash -s <<'BUILD'
set -eu
t=/workspace/output/rg280v/host
export PATH="$t/bin:$PATH"
cp /workspace/output/rg280v/.config /workspace/output/rg280v-pymenu/buildroot-config-before-build
restore_config() { cp /workspace/output/rg280v-pymenu/buildroot-config-before-build /workspace/output/rg280v/.config; }
trap restore_config EXIT
work/buildroot/utils/config --file output/rg280v/.config --enable BR2_PACKAGE_PYTHON3 --enable BR2_PACKAGE_PYTHON3_ZLIB --enable BR2_PACKAGE_PYTHON3_PYEXPAT --enable BR2_PACKAGE_PYTHON3_UNICODEDATA
make -C work/buildroot O=/workspace/output/rg280v BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace olddefconfig
make -C work/buildroot O=/workspace/output/rg280v BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace BR2_DL_DIR=/workspace/work/dl -j8 python3
cd /workspace/output/rg280v-pymenu/pygame-source
"$t/bin/python3" - <<'PY'
from pathlib import Path
s=Path('buildconfig/Setup.SDL1.in').read_text()
s=s.replace('-I/usr/include/SDL', '-I/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL')
for name in ['scrap','pypm','_freetype']:
 s='\n'.join('#'+line if line.startswith(name+' ') else line for line in s.split('\n'))
Path('Setup').write_text(s)
PY
export CC="$t/bin/mipsel-gcw0-linux-uclibc-gcc" LDSHARED="$t/bin/mipsel-gcw0-linux-uclibc-gcc -shared"
export CFLAGS="-O2 -fPIC -I$t/mipsel-gcw0-linux-uclibc/sysroot/usr/include/python3.11"
export PYTHONPATH=/workspace/output/rg280v/target/usr/lib/python3.11
export _PYTHON_SYSCONFIGDATA_NAME=_sysconfigdata__linux_ _PYTHON_HOST_PLATFORM=linux-mipsel
"$t/bin/python3" - <<'PY'
import sys,sysconfig,runpy
v=sysconfig.get_config_vars()
r='/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot'
for k in ['LIBDIR','LIBPL','INCLUDEPY','CONFINCLUDEPY']:
 if v.get(k,'').startswith('/usr/'):v[k]=r+v[k]
sys.argv=['setup.py','build_ext','-j8']
runpy.run_path('setup.py',run_name='__main__')
PY
runtime=/workspace/output/rg280v-pymenu/runtime/python
mkdir -p "$runtime/bin" "$runtime/lib/python3.11/site-packages/pygame" "$runtime/licenses"
cp /workspace/output/rg280v/target/usr/bin/python3.11 "$runtime/bin/"
cp -a /workspace/output/rg280v/target/usr/lib/libpython3.11* "$runtime/lib/"
cp -a /workspace/output/rg280v/target/usr/lib/python3.11/. "$runtime/lib/python3.11/"
cp -a src_py/. "$runtime/lib/python3.11/site-packages/pygame/"
cp build/lib.linux-mipsel-cpython-311/pygame/*.so "$runtime/lib/python3.11/site-packages/pygame/"
"$t/bin/mipsel-gcw0-linux-uclibc-strip" "$runtime/bin/python3.11" "$runtime/lib/python3.11/site-packages/pygame/"*.so
cp docs/LGPL "$runtime/licenses/pygame-LGPL"
cp /workspace/output/rg280v/build/python3-3.11.6/LICENSE "$runtime/licenses/python-LICENSE"
cd /workspace/output/rg280v-pymenu/runtime
tar -czf ../python-runtime.tar.gz python
BUILD
printf 'Built %s/python-runtime.tar.gz\n' "$work"
