import concurrent.futures
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
root = Path(__file__).resolve().parent
cross = '/workspace/output/rg280v/host/bin/mipsel-gcw0-linux-uclibc-'
src = []
for project in ('pdfviewer.cbp', 'libxpdf.cbp'):
    tree = ET.parse(root / project)
    src += [unit.attrib['filename'] for unit in tree.findall('.//Unit') if unit.attrib.get('filename', '').endswith('.cpp')]
build = root / 'build-rg280v'
build.mkdir(exist_ok=True)
flags = ['-O2', '-msoft-float', '-DGCW0', '-DPLUMOS_RG280V', '-I.', '-Ifogoo', '-Isplash', '-Ixpdf', '-I/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/freetype2', '-I/workspace/output/rg280v/host/mipsel-gcw0-linux-uclibc/sysroot/usr/include/SDL', '-std=gnu++98', '-fpermissive']
def compile_one(path):
    obj = build / (path.replace('/', '_')+'.o')
    cmd = [cross+'g++', *flags, '-c', str(root/path), '-o', str(obj)]
    p = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode: print(path, p.stdout[-6000:], flush=True)
    return obj, p.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(compile_one, src))
if any(rc for obj, rc in results): sys.exit(1)
cmd = [cross+'g++', '-msoft-float', '-o', str(build/'pdfviewer'), *[str(obj) for obj, rc in results], '-lSDL', '-lSDL_gfx', '-lSDL_image', '-lfreetype', '-lpng', '-lz', '-lexpat', '-lpthread', '-lm']
p = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print(p.stdout[-6000:])
sys.exit(p.returncode)
