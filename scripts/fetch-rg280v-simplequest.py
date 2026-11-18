#!/usr/bin/env python3
"""Fetch the author's theme for private device installation, not redistribution."""
import hashlib
import pathlib
import urllib.request
import zipfile

WORK = pathlib.Path(__file__).resolve().parents[1] / 'output/rg280v-simplemenu'
URL = 'https://drive.google.com/uc?export=download&id=1XuKKNxqXetgvHlDtcNpxhVtTSSHTwr9v'
SHA256 = 'b30d4fdae5fa5fde5e6d559e13848c4477adbb1a3de2d22237c8f454a27b81e6'
WORK.mkdir(parents=True, exist_ok=True)
archive = WORK / 'SimpleQuest.zip'
if not archive.exists():
    urllib.request.urlretrieve(URL, archive)
if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
    raise SystemExit('Theme archive differs from the reviewed version; retained for inspection')
with zipfile.ZipFile(archive) as bundle:
    for entry in bundle.infolist():
        path = pathlib.PurePosixPath(entry.filename)
        if path.is_absolute() or '..' in path.parts or path.parts[0] not in {'SimpleQuest', 'SimpleQuest2'}:
            raise SystemExit('Unexpected theme archive path')
        if (entry.external_attr >> 16) & 0o170000 == 0o120000:
            raise SystemExit('Theme archive contains a symbolic link')
    bundle.extractall(WORK / 'themes')
print('SimpleQuest and SimpleQuest2 verified; keep theme data outside redistributed images and Git')
