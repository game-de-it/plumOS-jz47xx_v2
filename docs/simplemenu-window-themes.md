# Dynamic window themes for SimpleMenu

CrystalMenu is the project's RPG-style theme for the RG280V logical 320x240
screen. Category/system selection uses five windows; ROM selection uses a wide
blue list with purple system heading and green position counter. All use a common
black background and stepped silver frames. There are no per-item background/
selection images. Text, lists and the pointing hand are drawn live.
The main category/system artwork is the user-supplied `resources/main.png`, shared
across every selection. Its frames contain no baked-in list text or pointer.

## Navigation and layout

| Window | Content |
| --- | --- |
| Purple, upper center | Current category or short system name |
| Tall blue, right | Categories/systems; the hand indicates selection |
| Blue, upper left | Full system name on one scrolling line |
| Blue, lower left | A: Select, B: Back, START: Setup |
| Green, lower right | Selected position / total |

On the ROM screen a 304x192 blue window replaces the narrow list and detail/help
panels. Six ROM names use single lines across a 279px text area. System name and
position count are above the list. Launch profile remains accessible via SELECT;
favorite operations remain X/Y, and A/B/START retain the same behavior.

Categories -> systems -> ROMs use the native SimpleMenu selection state. A
confirms; B returns up a level. In the ROM list, native SELECT opens launch
preferences, X marks a favorite and Y toggles the favorites section. Settings,
help and core-selection submenus retain native SimpleMenu rendering. R1's native
view flag does not replace the fixed window layout with artwork in this theme.
The category/system screens show the common shop artwork in the center; the ROM
view uses that space for the wide list. No per-item image rotation is used.

Fresh Apps -> SimpleMenu launches open the category screen, highlighting the
remembered category. System/ROM selections are still saved and restored when you
enter those lists. Exiting an emulator returns directly to the previous ROM list.
The Apps wrapper passes `--start-groups`; the emulator invoker omits that flag.
Native launch-at-boot configurations, if explicitly set, retain their existing
precedence. Direct native launches without the flag retain ROM-list restoration.

The default labels are English and use NES, SNES, GB, GBC, GBA, MD, SMS, etc.
ROM filenames/aliases are not translated; Japanese names remain Japanese. Names
do not wrap. A selected name wider than its area waits one second, scrolls left
at24 logical pixels/second, pauses one second at its end, then returns to the
beginning. Selection/screen changes restart the scroll. Unselected long names
use UTF-8-safe ellipsis. All moving text is clipped to its own area; fonts keep
their original bitmap size. Long detail/core/system labels can scroll likewise.

## Opt-in theme configuration

Without `[WINDOW_MENU] enabled = 1`, existing themes keep their ordinary rendering.
The implementation does not identify themes by name, system order or asset hashes.

```ini
[GENERAL]
items = 6
items_in_fullscreen_mode = 6

[WINDOW_MENU]
enabled = 1
font = resources/fonts/umplus_j10r.bdf
font_size = 10
background = resources/main.png
background_contains_frames = 1
heading = 122,10,77,32
list = 222,10,87,190
detail = 11,27,88,103
help = 61,150,88,84
counter = 182,203,98,31
rom_heading = 8,8,188,26
rom_list = 8,40,304,192
rom_counter = 204,8,108,26
scroll_speed = 24
scroll_delay = 1000
scroll_pause = 1000
```

Rectangles are logical x,y,width,height and must fit the screen. Font size is
8..18; list rows are 1..20 and must fit the list window. Native theme `items`
defines the page size; `items_in_fullscreen_mode` should match it for this layout.
Optional `background` is a theme-relative image, loaded once and nearest-neighbor
scaled to the logical screen. `background_contains_frames = 1` uses its existing
frames instead of drawing the five native frames over it. Missing backgrounds
fall back to native frames. The wide ROM layout remains drawn separately.
CrystalMenu uses `resources/fonts/umplus_j10r.bdf`; CrystalMenu12 uses the supplied
`umplus_j12r.bdf`. These original M+ bitmap fonts from Pyxel example assets include
both Japanese and Latin BDF blocks. The renderer reads all blocks, uses a shared
ascent/descent baseline, and draws the source bits at integer coordinates without
resampling. English and Japanese use the same bitmap measurements. Their license
and source notice are included beside the font files.

`[WINDOW_MENU] font` accepts a theme-relative BDF path (or TTF path). BDF pixels
are fixed by the file; `font_size` does not resize them. Without this key, the
existing plumOS CJK fallback TTF remains supported. The ordinary GENERAL font path
still references standard 0A for native fallback/submenu compatibility.

Optional WINDOW_MENU strings: `title`, `choose_category`, `choose_system`,
`default_core`, `favorite`, `help_text`. A literal `\n` separates text lines.
`[LABELS]` maps actual group/section names to compact display labels;
`[DETAIL_LABELS]` independently maps them to full detail names. These maps change
text only, never section order, IDs or launch targets. Unlisted items use their
registered names. Category/system/ROM content and selection counts come from
SimpleMenu's real data, including its normal empty-system skipping behavior.

## Install and select

```sh
scripts/build-rg280v-simplemenu.sh
python3 scripts/install-rg280v-simplemenu.py
```

Exit SimpleMenu first. The installer includes project-authored themes in fresh
seeds and updates their installed copies with a timestamped backup. It preserves
the selected theme by name when adding folders shifts numeric theme indices.
Existing external theme assets, section INIs, favorites and ROM settings remain.
Choose Apps -> SimpleMenu -> START -> Theme -> CrystalMenu, then B to apply.
Choose CrystalMenu12 for the 12-dot version. It shares the same layout and points
to the 12-dot file in CrystalMenu's resources; retain both installed folders.

Native source changes remain in `patches/rg280v-simplemenu.patch`, applied against
the pinned upstream checkout by the build script. Original 0A, SimUI, ArtBook and
SimpleQuest assets are not modified. Source integration frees the renderer's font
and config on theme changes and before SDL_ttf shutdown.
