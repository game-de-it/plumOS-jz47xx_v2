# Original external SimpleMenu theme validation

The user selected Simple Quest only as a compatibility test and requested a more
general external-theme test instead of further adapting that theme's fixed menu.
No additional Simple Quest handling or section-order changes were deployed.

## Candidates and original sources

| Theme | Source revision | Original files verified on SD1 |
| --- | --- | --- |
| SimUI (320x240, v1.2) | dkodr/SimUI `13d35f79f9b6c75f034c51838496aa922b272045` | 71 |
| ArtBook (320x240) | anthonycaccese/sm-theme-art-book `f64636382fbcc5c5bb9b9e79fbf116e43cbcc79b` | 125 |

Sources: https://github.com/dkodr/SimUI and
https://github.com/anthonycaccese/sm-theme-art-book . SimUI documents SimpleMenu
10.3.1 compatibility and 320x240 support; Art Book documents testing on RG280V with
Adam image. Both use ordinary SimpleMenu theme.ini options and independent system
logos, without a complete fixed system list/selection arrow embedded in each
system image. Neither requires the Simple Quest section ordering correction.
This is a functional compatibility test, not a claim that Simple Quest violates
SimpleMenu's theme specification.

`scripts/install-rg280v-simplemenu-external-themes.py` fetches pinned sources and
installs the original theme folders. It refuses a modified checkout or running
SimpleMenu, backs up saved state/existing theme folders, verifies the archive and
every source file on the device, and preserves the previously selected theme by
name when adding folders changes numeric theme indices. Original assets remain
in ignored output and on the private device; no third-party artwork is committed
or added to a public OS image. SimUI has an upstream MIT license; ArtBook public
redistribution permission was not established by this test.

## Device results

Same installed SimpleMenu executable, existing section INIs/launch profiles and
ROMs. No source/binary, kernel, global SDL or emulator changes. No SD image made.

- `check-rg280v-simplemenu-cursor.py --theme-name SimUI`: all nine checks passed.
- `check-rg280v-simplemenu-cursor.py --theme-name ArtBook`: all nine checks passed.
- Checks cover queued/opposite keys, taps/hold/release, another button while
  held, B+DOWN section switching, held A entering once, thirteen system selection
  samples (initial plus twelve DOWN taps), and ROM list five DOWN/five UP.
- Both system sequences: `1,2,3,4,5,6,7,8,9,10,0,1,2`.
- Both ROM sequences: `1,2,3,4,5,4,3,2,1,0`.
- System screenshots and ArtBook's ROM list inspected. No fixed-list cursor jump
  like Simple Quest's Genesis -> Master System transition.
- Separate temporary HOME: SimUI NES list -> A -> Akumajou Densetsu via existing
  default FCEUX223 profile -> SELECT+START -> Exit -> same SimUI list. Screenshot
  shows emulator 60.0 FPS; exit log is `SimpleMenu emulator exit=0`.
- Repeated the same game launch/menu exit/return with ArtBook; return screenshot
  confirms the original selected ROM. Audio audibility was not judged in this
  theme test. A transient black screen during restart was not treated as failure;
  subsequent captures confirmed the list restored.
- Tests use isolated settings. Normal selected theme remains 0A; favorites and
  normal ROM positions are not reset. Ended diagnostics and restored plumOS FE.

Themes are available from Apps -> SimpleMenu -> START -> Theme. Choose SimUI or
ArtBook with left/right and B to apply. Existing SimpleQuest folders remain
available, but are not the external compatibility acceptance test.

## Evidence (ignored local output)

- `output/rg280v-simplemenu/external-themes/installed-manifest.json`
- `output/rg280v-simplemenu/input-check-theme-{SimUI,ArtBook}/`: results.json,
  events.log and thirteen section screenshots (ArtBook also rom-list.png)
- `output/rg280v-simplemenu/{SimUI,ArtBook}-launch-initial.png`
- `output/rg280v-simplemenu/{SimUI,ArtBook}-emulator-menu.png`
- `output/rg280v-simplemenu/{SimUI,ArtBook}-after-game.png`
- `output/rg280v-simplemenu/SimUI-game-running.png`

One manually prepared temporary launch initially used a stale numeric theme
index, showing SimpleQuest instead of SimUI. It was stopped and replaced before
game testing. Final launch preparation resolves the theme name against the
installed case-insensitive sort order. This reinforces why scripts should use
`--theme-name`, not hard-coded indices, after external themes are added.
