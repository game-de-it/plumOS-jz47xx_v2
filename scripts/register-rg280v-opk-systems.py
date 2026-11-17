#!/usr/bin/env python3
"""Merge accepted OPK profiles without reverting existing device core choices."""
import copy
import json
import pathlib
import sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROUTES=json.loads((ROOT/'assets/rg280v-apps/standalone-opk-routes.json').read_text())
NEW={
 'atari800':('Atari 800','ATARI800',['car','atr','xex','rom','xfd','bin'],['atari800','ATARI800','ATARI/800']),
 'atari2600':('Atari 2600','ATARI2600',['a26','bin','rom'],['atari2600','ATARI2600']),
 'pokemini':('Pokemon Mini','POKEMINI',['min'],['pokemini','POKEMINI']),
 'lynx':('Atari Lynx','LYNX',['lnx','lyx'],['lynx','LYNX']),
 'cpc':('Amstrad CPC','CPC',['dsk','sna','bin','cpr'],['cpc','CPC','amstradcpc']),
 'zxspectrum':('ZX Spectrum','ZX',['tap','tzx','sna','z80','trd','scl'],['zxspectrum','ZXSPECTRUM','ZX']),
 'neogeo':('Neo Geo','NEOGEO',['zip'],['neogeo','NEOGEO']),
 'neogeocd':('Neo Geo CD','NEOGEOCD',['m3u','cue','iso'],['neogeocd','NEOGEOCD']),
 'amiga':('Amiga','AMIGA',['adf','adz'],['amiga','AMIGA']),
 'arcade':('Arcade','ARCADE',['zip'],['arcade','ARCADE','fbneo','FBNEO']),
}
def merge(data):
    data=copy.deepcopy(data);systems={s['id']:s for s in data['systems']}
    for ident,(name,short,ext,aliases) in NEW.items():
        if ident in systems:continue
        system=dict(id=ident,display_name=name,short_name=short,sort_order=200+list(NEW).index(ident)*10,
          hardware='computer' if ident in {'atari800','cpc','zxspectrum','amiga'} else 'console',
          enabled=True,pinned=False,directory_aliases=[dict(name=n,source='plumos',priority=(i+1)*10) for i,n in enumerate(aliases)],
          extensions=ext,artwork={'lookup':[{'root':'sdcard','path':'Images/'+ident}]},
          launch_profiles=[],default_launch_profile='',default_cpu_policy='ondemand',
          scraper={'enabled':False,'reason':'not_configured'})
        systems[ident]=system;data['systems'].append(system)
    for route in ROUTES:
        profile='standalone:'+route['id']
        for ident in route['systems']:
            system=systems[ident]
            if ident=='ngpc' and not system.get('enabled'):
                # The previous disabled RA route was explicitly rejected on RG280V.
                system['launch_profiles']=[];system['default_launch_profile']=''
            if profile not in system['launch_profiles']:system['launch_profiles'].append(profile)
            if not system['default_launch_profile']:system['default_launch_profile']=profile
            if ident in NEW or ident=='ngpc':system['enabled']=True
    return data
if __name__=='__main__':
    source=pathlib.Path(sys.argv[1]);dest=pathlib.Path(sys.argv[2])
    dest.write_text(json.dumps(merge(json.loads(source.read_text())),ensure_ascii=False,indent=2)+'\n')
