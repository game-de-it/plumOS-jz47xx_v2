# Wide ROM window and single-line marquee

User requests: a larger ROM-only window, then horizontal text scrolling instead
of wrapping. Implemented both for CrystalMenu and CrystalMenu12. Existing BDF
fonts, pointing hand and common frame style remain unchanged.

## Behavior

- Category/system screens retain the five-window geometry. Names no longer wrap:
  selected overflowing list/detail/header labels scroll; unselected list labels
  use UTF-8-safe ellipsis.
- ROM screen has a304x192 blue list window (8,40), a188x26 purple heading (8,8),
  and a108x26 green counter (204,8). Six rows, each one line, with279px text width.
  The narrow detail/help windows are replaced in this screen. SELECT still opens
  launch preferences; native A/B/START/X/Y actions remain unchanged.
- Selected text holds1000ms at its beginning, scrolls24 logical px/s, holds1000ms
  at its end, then restarts. Selection/screen changes reset it. Text is clipped
  within its own window. Fonts never shrink or use fractional positioning.
- Main loop requests a refresh only when a marquee's integer offset changes.
  Ordinary themes and suspended screens do not activate this animation path.
- Optional rom_heading/rom_list/rom_counter and scroll_speed/scroll_delay/
  scroll_pause keys are documented in `docs/simplemenu-window-themes.md`.

## Common alias ownership bug found by the test

The temporary long-alias test initially failed on launch after theme switches.
`getRomRealName` returned a borrowed `ht_get` value, while its caller `getAlias`
freed the result; later hash-table destruction could free it again. Return an
owned strdup consistently, as the function already does in the no-match branch.
This existing common bug is separate from the new layout, but fixing it is needed
to verify alias display -> real ROM launch -> exit/return safely. No ROM renamed.

## Validation

- MIPS soft-float build passed. Clean pinned-upstream patch application and source
  comparison checked, as well as Python syntax and non-patch whitespace.
- CrystalMenu12 and CrystalMenu each passed all nine common cursor checks after
  this change. Standard0A passed all nine checks with no new theme feature enabled.
- `check-rg280v-simplemenu-window.py --theme-name CrystalMenu12 --marquee-check`
  uses an isolated HOME and copied section INIs with a temporary long display
  alias for existing Akumajou Densetsu. Live user aliases/config/ROMs are untouched.
- Independent source-BDF pixel comparison measured successive selected-title
  offsets **0,22,60px**. After down/up selection the offset was **0px** again.
  No wrapping: the gap below the selected title contains no white text pixels.
  Changed-pixel bounding box between captures was (27,57)-(306,69), entirely
  within the selected line: frames, counter, hand and other rows stayed fixed.
- Category cycle2,3,0,1; systems down/up; Japanese NES last title index119;
  0A switch and return; long-alias game launch through the existing FCEUX223
  profile, menu Exit, exit0, correct theme/list restoration and input afterward;
  favorites roundtrip all passed.
- Japanese 魔界村 in the new ROM window matched all161 original BDF white pixels
  exactly at the new (27,201) origin. No font rendering change from the accepted
  bitmap version.
- The first alias run's launch failure was not counted as a pass. It motivated
  the ownership fix above; the complete rerun passed.

The actual FE Apps route was used to reopen the user's selected CrystalMenu12
ROM screen. Final screenshot shows the large NES list (position102/120), with
Japanese names on one line. Left visible for user feedback; no further automated
input after asking for physical width/readability/control confirmation.

Evidence (ignored):

- `output/rg280v-simplemenu/window-scroll-{build,install,test}.log`
- `output/rg280v-simplemenu/window-check-CrystalMenu12-marquee/`
  (temporary aliases, input trace, results.json, scroll0/1/2/reset and all other
  functional screenshots)
- `output/rg280v-simplemenu/input-check-theme-{CrystalMenu12,CrystalMenu,0A}/`
- `output/rg280v-simplemenu/scroll-live.png`
