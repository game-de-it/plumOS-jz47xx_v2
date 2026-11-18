#!/usr/bin/env python3
"""Generate Amber's small original UI assets at native 320x240 resolution."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / 'assets/rg280v-350teric/skins/Amber'
NORMAL = (184, 188, 190, 255)
ACCENT = (242, 140, 40, 255)
FAMILIES = {
    'nes': 'nes', 'sfc': 'snes', 'gb': 'gb', 'gbc': 'gb', 'gba': 'gba',
    'psx': 'psx', 'megadrive': 'pad', 'mastersystem': 'nes', 'gamegear': 'gba',
    'segacd': 'pad', 'pcengine': 'nes', 'supergrafx': 'nes', 'pcenginecd': 'nes',
    'ngpc': 'gba', 'wonderswan': 'gba', 'msx': 'computer', 'atari800': 'computer',
    'atari2600': 'joystick', 'pokemini': 'gb', 'lynx': 'gba', 'cpc': 'computer',
    'zxspectrum': 'computer', 'neogeo': 'arcade', 'neogeocd': 'pad',
    'amiga': 'computer', 'arcade': 'arcade', 'generic': 'gear',
}
NATIVE = {'generic': 'gear', 'about': 'info', 'configure': 'gear', 'device': 'gear',
          'skin': 'palette', 'exit': 'power', 'explorer': 'folder',
          'section': 'folder', 'ebook': 'info', 'imgv': 'info',
          'commander': 'folder', 'utilities-terminal': 'computer'}


def icon(kind, color):
    image = Image.new('RGBA', (28, 24))
    d = ImageDraw.Draw(image)
    def rect(box): d.rectangle(box, outline=color)
    def line(points): d.line(points, fill=color, width=1)
    def cross(x, y):
        line([(x, y-3), (x, y+3)]); line([(x-3, y), (x+3, y)])
    if kind == 'nes':
        rect((1,5,26,18)); cross(7,12)
        rect((19,11,21,13)); rect((23,11,25,13)); line([(12,14),(15,14)])
    elif kind in ('snes','pad','psx'):
        line([(1,10),(4,6),(9,5),(18,5),(23,6),(26,10),(26,18),
              (22,20),(17,16),(10,16),(5,20),(1,18),(1,10)])
        cross(7,11)
        for x,y in [(20,9),(23,12),(17,12),(20,15)]:
            d.rectangle((x,y,x+1,y+1),fill=color)
        line([(12,13),(14,13)])
    elif kind == 'gb':
        rect((7,1,20,22)); rect((9,3,18,11)); cross(11,16)
        d.rectangle((16,17,17,18),fill=color)
        d.rectangle((18,15,19,16),fill=color)
    elif kind == 'gba':
        line([(1,8),(5,4),(22,4),(26,8),(26,18),(22,21),(5,21),
              (1,18),(1,8)])
        rect((8,6,19,17)); cross(4,12)
        d.rectangle((22,11,23,12),fill=color)
        d.rectangle((24,9,25,10),fill=color)
    elif kind == 'computer':
        rect((5,1,22,13)); rect((7,3,20,10))
        line([(3,16),(24,16),(27,22),(0,22),(3,16)])
        line([(4,19),(23,19)]); line([(8,20),(19,20)])
    elif kind == 'arcade':
        line([(4,1),(23,1),(23,15),(26,22),(1,22),(4,15),(4,1)])
        rect((7,4,20,12)); line([(4,16),(23,16)])
        line([(9,14),(9,18)]); d.point((17,18),fill=color); d.point((20,18),fill=color)
    elif kind == 'joystick':
        line([(3,17),(24,17),(26,22),(1,22),(3,17)])
        line([(13,7),(13,17)]); rect((10,3,16,8)); rect((20,18,22,20))
    elif kind == 'folder':
        line([(2,6),(11,6),(14,9),(25,9),(25,20),(2,20),(2,6)])
        line([(3,11),(24,11)])
    elif kind == 'info':
        d.ellipse((5,3,22,20),outline=color); line([(14,10),(14,16)]); d.point((14,7),fill=color)
    elif kind == 'power':
        d.arc((5,4,22,21),-50,230,fill=color); line([(14,1),(14,12)])
    elif kind == 'palette':
        rect((4,3,23,20))
        for x,y in [(8,7),(18,7),(8,15),(18,15)]:rect((x-1,y-1,x+1,y+1))
    else:
        d.ellipse((7,5,20,18),outline=color); d.ellipse((11,9,16,14),outline=color)
        for a,b in [((14,2),(14,5)),((14,18),(14,21)),((4,12),(7,12)),
                    ((20,12),(23,12)),((6,4),(8,6)),((20,18),(22,20)),
                    ((6,20),(8,18)),((20,6),(22,4))]:line([a,b])
    return image


for folder in ['systems','icons','imgs','wallpapers']:
    (SKIN/folder).mkdir(parents=True,exist_ok=True)
for name, family in {**FAMILIES, **NATIVE}.items():
    icon(family,NORMAL).save(SKIN/'systems'/(name+'.png'))
    icon(family,ACCENT).save(SKIN/'systems'/(name+'-selected.png'))
for name,family in NATIVE.items():
    icon(family,NORMAL).save(SKIN/'icons'/(name+'.png'))
# Native dialogs inherit these neutral symbols instead of colorful default ones.
for name,kind in [('folder','folder'),('file','info'),('go-up','folder')]:
    icon(kind,NORMAL).resize((14,12),Image.Resampling.NEAREST).save(SKIN/'imgs'/(name+'.png'))
frame=Image.new('RGBA',(320,240),(8,10,11,255));d=ImageDraw.Draw(frame)
edge=(80,85,88,255)
d.line([(8,4),(311,4),(315,8),(315,231),(311,235),(8,235),(4,231),(4,8),(8,4)],fill=edge)
for a,b in [((4,8),(8,4)),((311,4),(315,8)),((315,231),(311,235)),((8,235),(4,231))]:
    d.line([a,b],fill=ACCENT,width=1)
d.line([(5,29),(314,29)],fill=ACCENT)
d.line([(5,218),(314,218)],fill=edge)
frame.save(SKIN/'wallpapers/frame.png')
print('Generated Amber UI assets:', SKIN)

# Small neutral input symbols for inherited native dialogs.
from PIL import ImageFont
(SKIN/'imgs/buttons').mkdir(exist_ok=True)
for name in ['a','b','x','y','l','r','left','right','up','down','start','select']:
    im=Image.new('RGBA',(14,14));d=ImageDraw.Draw(im)
    if name in ['left','right','up','down']:
        points={'left':[(9,3),(4,7),(9,11)],'right':[(4,3),(9,7),(4,11)],
                'up':[(3,9),(7,4),(11,9)],'down':[(3,4),(7,9),(11,4)]}[name]
        d.line(points,fill=NORMAL)
    elif name=='start':
        d.line([(4,3),(10,7),(4,11),(4,3)],fill=NORMAL)
    elif name=='select':
        d.rectangle((3,4,10,5),fill=NORMAL);d.rectangle((3,8,10,9),fill=NORMAL)
    else:
        d.rectangle((0,0,13,13),outline=NORMAL)
        d.text((4,1),name.upper(),font=ImageFont.load_default(),fill=NORMAL)
    im.save(SKIN/'imgs/buttons'/(name+'.png'))
