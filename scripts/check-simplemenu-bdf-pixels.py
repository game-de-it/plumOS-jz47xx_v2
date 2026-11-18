#!/usr/bin/env python3
"""Compare a captured CrystalMenu heading against the original BDF pixel grid."""
import argparse
import json
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('font', type=Path)
parser.add_argument('screenshot', type=Path)
parser.add_argument('--text', default='Consoles')
parser.add_argument('--origin', nargs=2, type=int, help='Explicit text top-left, instead of centered heading')
parser.add_argument('--region', nargs=4, type=int, default=(128, 15, 65, 22), metavar=('X', 'Y', 'W', 'H'))
parser.add_argument('--find-offset', action='store_true', help='Find an exact horizontally clipped marquee position')
args = parser.parse_args()
glyphs = {}
ascent = descent = 0
glyph = None
bitmap = False
for line in args.font.read_text().splitlines():
    fields = line.split()
    if not fields:
        continue
    if fields[0] == 'FONT_ASCENT':
        ascent = max(ascent, int(fields[1]))
    elif fields[0] == 'FONT_DESCENT':
        descent = max(descent, int(fields[1]))
    elif fields[0] == 'STARTCHAR':
        glyph = dict(rows=[])
        bitmap = False
    elif fields[0] == 'ENCODING':
        glyph['code'] = int(fields[1])
    elif fields[0] == 'DWIDTH':
        glyph['advance'] = int(fields[1])
    elif fields[0] == 'BBX':
        glyph['box'] = tuple(map(int, fields[1:]))
    elif fields[0] == 'BITMAP':
        bitmap = True
    elif fields[0] == 'ENDCHAR':
        glyphs[glyph['code']] = glyph
        bitmap = False
    elif bitmap:
        glyph['rows'].append(int(line, 16))

width = sum(glyphs[ord(char)]['advance'] for char in args.text)
x = 128 + (65 - width) // 2
y = 10 + (32 - (ascent + descent + 1)) // 2
if args.origin:
    x, y = args.origin
expected = set()
for char in args.text:
    glyph = glyphs[ord(char)]
    w, h, dx, dy = glyph['box']
    assert len(glyph['rows']) == h
    top = y + ascent - h - dy
    stride = (w + 7) // 8 * 8
    for row, bits in enumerate(glyph['rows']):
        for col in range(w):
            if bits & (1 << (stride - 1 - col)):
                expected.add((x + dx + col, top + row))
    x += glyph['advance']

image = Image.open(args.screenshot).convert('RGB')
rx, ry, rw, rh = args.region
actual = {(x, y) for y in range(ry, ry + rh) for x in range(rx, rx + rw)
          if image.getpixel((x, y)) == (255, 255, 255)}
assert expected, 'Reference rendered no pixels'
offsets = range(max(0, width - rw) + 1) if args.find_offset else [0]
matches = []
for offset in offsets:
    clipped = {(x - offset, y) for x, y in expected
               if rx <= x - offset < rx + rw and ry <= y < ry + rh}
    if actual == clipped:
        matches.append(offset)
assert len(matches) == 1, dict(matches=matches, actual_pixels=len(actual))
print(json.dumps(dict(exact_match=True, white_pixels=len(actual),
                      ascent=ascent, descent=descent, text=args.text, offset=matches[0])))
