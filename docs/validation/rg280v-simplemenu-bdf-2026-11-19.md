# M+ bitmap fonts for CrystalMenu

The user reported jagged / apparently non-horizontal text, then suggested Pyxel's
umplus_j10r.bdf and umplus_j12r.bdf. Adopted both original files with their M+
bitmap font license and source notice. CrystalMenu uses j10r; CrystalMenu12 uses
j12r with the same windows and navigation. No frame geometry, display mode,
kernel, emulator or global SDL scaling change.

## Cause and implementation

The first window implementation used WenQuanYi Micro Hei TrueType at size10,
monochrome rasterization. It did not give the desired fixed-dot appearance.
Captured DRM metadata is SRC320x240 -> CRTC320x480 (exact vertical2x), not a
fractional/rotated text transform. Physical perception remains a user check.

These Pyxel BDF assets concatenate **two STARTFONT/ENDFONT blocks**, Japanese and
Latin. SDL_ttf opened the first block only; our first single-block direct parser
likewise omitted Latin. An opened font / passing input suite was not treated as
successful text rendering. The final BDF reader consumes all font blocks, uses
the maximum ascent/descent to form one baseline and applies DWIDTH/BBX offsets
without scaling or hinting. Repeated Unicode codes use the last block's glyph,
deterministically. Unknown glyphs fall back to '?'; this is a Japanese font, not
unrestricted Unicode coverage. Glyph dimensions/counts and clipping are bounded.

Bitmap text is composed in a software SDL surface and blitted normally, matching
the existing display path. TTF mode remains supported when configured or when the
window theme does not select a BDF. Resources are freed on theme switch/shutdown.
The optional WINDOW_MENU `font` path supports theme-relative resources. Both BDF
assets are unchanged; license permits use/copy/distribution with or without edits.

## Original font integrity and metrics

| Asset | SHA256 |
| --- | --- |
| umplus_j10r.bdf | e0172aed90f8768dd10d74ab3b3a9a14c86c5fb4b36b92c03b73c978971bd69d |
| umplus_j12r.bdf | 41ecb8e016acf69476a4cbf82fc100dc66a0259607bc12245ae7dcdf41349ab7 |

Local original copies were obtained from the existing Y1 theme project's font
assets, attributed there to Pyxel examples. Source BDF header was checked at
https://raw.githubusercontent.com/kitao/pyxel/main/python/pyxel/examples/assets/umplus_j10r.bdf .
The Pyxel custom font example also documents this BDF usage:
https://github.com/kitao/pyxel/blob/main/python/pyxel/examples/13_custom_font.py .

Both final merged fonts contain 7169 unique glyphs. Their common cells are13 px
high: j10r ascent9/descent4, j12r ascent11/descent2. The nominal 10/12-dot sizes
refer to the original glyph designs, not rescaled vectors.

## Device verification

- Both variants passed the common nine-case cursor suite, with screenshots
  inspected for visible Latin text (earlier blank Latin captures were failures).
- Both passed dedicated category/system/ROM transitions, Japanese ROM selection,
  native 0A switch and return, FCEUX223 launch/menu Exit/return, resumed input,
  and temporary favorite/list roundtrip. Each uses isolated HOME.
- Pixel comparison against the original BDF, using independent Python reference
  parsing of all blocks and actual captured white pixels:

| Text | j10r | j12r |
| --- | --- | --- |
| Consoles, heading | exact99 white pixels | exact112 white pixels |
| 魔界村, detail | exact123 white pixels | exact161 white pixels |

`scripts/check-simplemenu-bdf-pixels.py` verifies glyph position/bitmap and absence
of extra text pixels, not merely non-black output. It proves source-grid placement
in captured frames; it does not substitute for the user's LCD/readability judgment.

The final normal Apps route was used to open **CrystalMenu12**, then the Arcade
system list was left visible. Requested physical confirmation of whether the
perceived jaggedness/tilt improved. No further UI automation after that request.
User settings/ROM selections and original external themes remain; selected theme
is intentionally set to the new 12-dot variant for this comparison.

Evidence in ignored output:

- `window-text-before.png` / `.drm.txt` (old TTF)
- `input-check-theme-{CrystalMenu,CrystalMenu12}/` (BDF input/capture runs)
- `window-check/` and `window-check-CrystalMenu12/` (complete functional runs)
- `window-bdf-{build,install}.log`, `window-bdf-live.png`
- `font-probe.c` / `font-probe` (actual device glyph metrics / raster probe)

The diagnostic parser also discards incomplete live trace records and deletes a
stale results.json before starting, so a failed run cannot reuse an earlier pass.
