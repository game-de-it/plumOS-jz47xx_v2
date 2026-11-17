#!/usr/bin/env python3
"""Compare catalog emulator ELF payloads with active standalone packages (in build container)."""
import hashlib,json,pathlib,re,subprocess,tempfile
ROOT=pathlib.Path('/workspace')
OUT=ROOT/'output/rg280v-apps/rg350-sa-duplicates.json'
UNSQUASH=ROOT/'output/rg280v/host/bin/unsquashfs'
active={'fceux':('fceux_gcw0-2.6.6-2023-08-30.opk','fceux_gcw0'),
'gambatte':('gambatte-dms-rg280v.opk','gambatte-dms.gcw0'),
'pocketsnes':('PocketSNES_2019-12-12.opk','PocketSNES.dge'),
'regba':('ReGBA_1.9.2_rg280v.opk','regba.gcw0'),
'picodrive':('PicoDrive_rg280v.opk','picodrive')}
def inspect(p):
 result=[]
 with tempfile.TemporaryDirectory(prefix='rg350-duplicate-') as t:
  subprocess.run([str(UNSQUASH),'-no-progress','-d',t,str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  for f in pathlib.Path(t).rglob('*'):
   if not f.is_file():continue
   with f.open('rb') as stream:
    if stream.read(4)!=b'\x7fELF':continue
   data=f.read_bytes()
   strings=re.findall(rb'[ -~]{8,}',data)
   hints=[s.decode()[:180] for s in strings if re.search(rb'(FCEUX.*[0-9]\.[0-9]|[Vv]ersion.*[0-9]\.[0-9]|Gambatte.*r[0-9]|ReGBA.*[0-9])',s)][:15]
   result.append(dict(path=str(f.relative_to(t)),sha256=hashlib.sha256(data).hexdigest(),hints=hints))
 return result
base={}
for k,(p,binary) in active.items():
 elf=inspect(ROOT/'output/rg280v-emulators'/p)
 matches=[e for e in elf if pathlib.Path(e['path']).name==binary]
 if not matches:raise RuntimeError((k,binary,[e['path'] for e in elf]))
 base[k]=dict(opk=p,**matches[0])
manifest=json.loads((ROOT/'output/rg280v-apps/rg350-catalog/manifest.json').read_text())
rows=[]
for n,item in enumerate(manifest,1):
 elfs=inspect(ROOT/'output/rg280v-apps/rg350-catalog'/item['name'])
 dup=[k for k,e in base.items() if any(x['sha256']==e['sha256'] for x in elfs)]
 rows.append(dict(number=n,name=item['name'],duplicates=dup,elf=elfs))
 print(n,item['name'],dup,flush=True)
OUT.write_text(json.dumps(dict(active=base,catalog=rows),ensure_ascii=False,indent=2))
