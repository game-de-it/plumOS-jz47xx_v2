# Shared shop background replacement

User requested replacing the main artwork with
`478314d9-c683-406d-8217-634eca37eea6-207x155@4x.png`.

Copied the original828x620 paletted PNG, unchanged, to CrystalMenu's
`resources/main.png`; CrystalMenu12 references the same file. Original, tracked
asset and installed user-HOME asset SHA256 all match:
`f2675f4e5a0cf5bc774221ff8581723c9c43e2d2ac51d287bd0c883a26021bd5`.

The optional WINDOW_MENU `background` setting loads the image once per theme
load, converts it to the screen format and uses SDL_SoftStretch (nearest-neighbor)
to fit logical320x240. Cached surface is released on theme switch/shutdown.
`background_contains_frames = 1` avoids drawing native frames over the supplied
framed artwork. Load failures fall back to the existing native five frames.

This background is shared for every category/system selection; all list text,
labels, counters and pointing-hand positions remain dynamic. The large single-line
ROM list retains its prior layout and procedural frames, without this background.
No font, scrolling, launch route or input handler was changed.

Validation:

- MIPS soft-float build and archive installation passed.
- Original/host/installed artwork hashes match; no edit/re-encoding of the PNG.
- `check-rg280v-simplemenu-window.py --theme-name CrystalMenu12` passed category
  cycle2,3,0,1; system down/up; Japanese last NES ROM index119; native0A theme
  switch and return; FCEUX223 launch/menu Exit/return with exit0 and resumed input;
  favorites roundtrip. Used temporary HOME.
- Inspected category/system captures: shop art visible centrally, text/hand inside
  the intended windows, no duplicate procedural frames. Inspected dedicated ROM
  capture and restored list after game exit.
- Reopened normal Apps -> SimpleMenu and left the new main category screen visible
  (Consoles selected). No user ROM or preference reset; selected theme remains12.
- Final patch checked against clean pinned upstream source; Python/config/whitespace
  checks as appropriate. Existing external themes/assets are unchanged.

Ignored evidence: `output/rg280v-simplemenu/window-background-{build,install,test}.log`,
`window-check-CrystalMenu12/{category-*.png,systems.png,returned.png,results.json}`,
and `output/rg280v-simplemenu/background-live.png`.
