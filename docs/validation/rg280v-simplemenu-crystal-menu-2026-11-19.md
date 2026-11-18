# CrystalMenu dynamic RPG window theme

## Request and final behavior

Implemented the user's five-window reference as a SimpleMenu theme. Common
background and frames are drawn procedurally; category/system/ROM text and one
pointing-hand sprite are drawn from the actual selection state. No per-selection
screen image or system-specific background is used. Central black space remains
reserved, as in the agreed layout.

User steering during implementation: use English-oriented short system labels
like NES and GB. CrystalMenu therefore uses NES/SNES/GB/GBC/GBA/MD/SMS/PCE/PSX etc.
in the right list and heading, with full system names in the left detail panel.
ROM names/aliases retain their actual language, including Japanese. Left detail
metadata follows the title's actual line count; profile and Favorite status fit
below short titles. Long text is UTF-8 wrapped/clipped, with ellipsis where needed.

## Implementation

- Opt-in `[WINDOW_MENU]` configuration, generic rectangles/font size/UI strings
  and `[LABELS]` / `[DETAIL_LABELS]` mappings. No CrystalMenu name check in native
  rendering or input logic. Unconfigured themes retain their original path.
- Native source patch adds window_menu.c/h, theme load/unload integration and
  navigation draw dispatch for category/system/ROM screens. Settings/core menu
  retain normal SimpleMenu rendering. Existing shared input fixes are unchanged.
- CJK rendering font uses the existing plumOS fallback font. Frames/hand are
  original code-drawn shapes guided by the reference; no game artwork is copied.
- Installer seeds project themes and updates installed project copies with a
  backup, preserving the existing selected theme by name when indices shift.
- User theme files and the original external themes are unmodified. No kernel,
  global SDL/ALSA, emulator, ROM or BIOS changes.

Configuration/usage: `docs/simplemenu-window-themes.md`.

## Validation

- MIPS soft-float build passed. Final device binary SHA256 matches host:
  `fb16ea3c8597e4ea16d81409b7d88afc7e97b8df64143b130e7f5a8f3a50f214`.
- Patch applied to clean pinned upstream source and byte-compared against all
  fourteen changed/new native source files. Python syntax and non-patch whitespace
  checks passed; no new unit tests mirroring the renderer were added.
- Common nine-case input suite: CrystalMenu passed, including final text layout;
  0A, SimUI and ArtBook each also passed after the new rendering path was added.
  Existing-theme drawing is bypassed only when the new opt-in configuration is on.
- Dedicated `check-rg280v-simplemenu-window.py` passed on final binary:
  category DOWN sequence 2,3,0,1; A/B transitions between all three hierarchy
  levels; system down/up; last NES ROM (index119, 魔界村) then wrap to index0;
  settings-based CrystalMenu -> 0A -> CrystalMenu switch; NES Akumajou Densetsu
  launch via existing FCEUX223 route; SELECT+START menu -> Exit; same theme/ROM
  restored with exit0 and next input accepted; X favorite/Y favorites list roundtrip.
- Screenshots inspected for category, systems, English/Japanese ROMs, native
  settings switch, emulator menu, return and favorites. Final short-title metadata
  includes visible Default core and Favorite lines. Audio quality/performance is
  not a new emulator validation claim for this UI change.
- Diagnostics used a temporary HOME; test favorite was not written to user HOME.
  Saved user state and original binary were backed up before deployment under
  `/media/data/plumos/backup/simplemenu-window-menu-20261119/` and project-theme
  updates have timestamped backups. No SD image created.

The first dedicated harness attempt waited for a SimpleMenu key-release trace
after SimpleMenu had exec'd the emulator. Corrected the harness to expect exec
at game launch. Another harness read caught a partial trace line; parser now
requires the complete field set. These failed diagnostic attempts were cleaned
up/restored and were not counted as successful checks. Final run above passed.

## Final device state / evidence

Opened SimpleMenu through the real plumOS FE Apps route, selected CrystalMenu,
and left the handheld system list visible for physical feedback. GB/GBC/GBA/GG/
NGPC/WS abbreviations and the pointing hand are visible. Parent plumOS FE remains
running so normal SimpleMenu Quit returns to it. User was asked to judge physical
readability and input; that confirmation is separate from automated device checks.

Ignored evidence:

- `output/rg280v-simplemenu/window-build.log`, `window-install.log`
- `output/rg280v-simplemenu/window-check/{events.log,results.json}`
- same directory: `category-*.png`, `systems.png`, `japanese-rom.png`,
  `switched-0A.png`, `switched-back.png`, `game.png`, `emulator-menu.png`,
  `returned.png`, `favorite-added.png`, `favorites.png`
- `output/rg280v-simplemenu/input-check-theme-{CrystalMenu,0A,SimUI,ArtBook}/`
- `output/rg280v-simplemenu/window-live.png` (actual Apps-launched instance)
