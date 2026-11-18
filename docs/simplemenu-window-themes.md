# Dynamic window themes for SimpleMenu

CrystalMenu is the project's RPG-style theme for the RG280V logical 320x240
screen. It uses a common black background, stepped silver frames, blue content
windows, a purple heading and green position counter. There are no per-item
background/selection images. Text, lists and the pointing hand are drawn live.
The supplied reference was used for the layout; no game screenshot or character
art is included in the theme.

## Navigation and layout

| Window | Content |
| --- | --- |
| Purple, upper center | Current category or short system name |
| Tall blue, right | Categories, systems or ROMs; the hand indicates selection |
| Blue, upper left | Full system/ROM name, selected launch profile and favorite state |
| Blue, lower left | A: Select, B: Back, START: Setup |
| Green, lower right | Selected position / total |

Categories -> systems -> ROMs use the native SimpleMenu selection state. A
confirms; B returns up a level. In the ROM list, native SELECT opens launch
preferences, X marks a favorite and Y toggles the favorites section. Settings,
help and core-selection submenus retain native SimpleMenu rendering. R1's native
view flag does not replace the fixed window layout with artwork in this theme.
Central black space is intentionally reserved; it contains no rotating image.

The default labels are English and use NES, SNES, GB, GBC, GBA, MD, SMS, etc.
ROM filenames/aliases are not translated; Japanese names remain Japanese. Lists
use bounded UTF-8 wrapping and ellipsis. The detail window allows up to four name
lines; extremely long names can still be ellipsized to stay inside the frame.
Metadata follows the actual number of title lines and is clipped to the window.

## Opt-in theme configuration

Without `[WINDOW_MENU] enabled = 1`, existing themes keep their ordinary rendering.
The implementation does not identify themes by name, system order or asset hashes.

```ini
[GENERAL]
items = 6
items_in_fullscreen_mode = 6

[WINDOW_MENU]
enabled = 1
font_size = 10
heading = 122,10,77,32
list = 222,10,87,190
detail = 11,27,88,103
help = 61,150,88,84
counter = 182,203,98,31
```

Rectangles are logical x,y,width,height and must fit the screen. Font size is
8..18; list rows are 1..20 and must fit the list window. Native theme `items`
defines the page size; `items_in_fullscreen_mode` should match it for this layout.
Window text uses the existing plumOS CJK fallback font, supporting English and
Japanese with the same measurement/rendering font. The ordinary theme font path
references the standard 0A font for native fallback/submenu compatibility.

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

Native source changes remain in `patches/rg280v-simplemenu.patch`, applied against
the pinned upstream checkout by the build script. Original 0A, SimUI, ArtBook and
SimpleQuest assets are not modified. Source integration frees the renderer's font
and config on theme changes and before SDL_ttf shutdown.
