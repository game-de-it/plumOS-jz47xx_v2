# Separate fresh SimpleMenu launch from emulator return

User reported opening a fixed ROM screen on SimpleMenu startup. Native main()
always set BROWSING_GAME_LIST after loading saved state when no explicit auto-
launch was configured. Thus both fresh Apps launches and emulator returns opened
the remembered system/ROM list; no ROM was intentionally hard-coded.

Added native `--start-groups`, used only by `plumos-simplemenu` (Apps entry).
It sets CHOOSING_GROUP and beforeTryingToSwitchGroup to the remembered active
group, so confirming that group uses the already loaded sections correctly.
`plumos-simplemenu-invoker` keeps its bare native exec, preserving ROM-list return
after a game. Saved state is not cleared or rewritten as a workaround. Existing
explicit native launch-at-boot handling remains prior to this default branch.

Checks:

- MIPS soft-float build passed; shell wrapper syntax passed.
- `check-rg280v-simplemenu-window.py --theme-name CrystalMenu12 --startup-check`
  passed. The temporary saved state deliberately remembers NES ROM index7, not0.
  First processed input is in category state2; down/up remains in categories.
  A -> system state4, A -> ROM state0 restores game7, proving selection is kept.
  Subsequent category cycle, Japanese last ROM119, theme roundtrip, FCEUX223
  launch/menu Exit/return with exit0 and accepted ROM input, favorites all passed.
- Initial diagnostic capture before readiness was black during startup; capture
  is now taken after the first category down/up event pair. Input trace establishes
  the first actual selection state was2. Real Apps captures below are ready frames.
- Normal FE Apps launch showed the category screen. START -> Session quit -> A
  returned to FE Apps. Opened SimpleMenu again and again got categories. Left this
  screen visible, with the existing shop background and category highlight.
- No theme, font, ROM, core profile or user selection reset. Native direct calls
  used by existing tests keep their previous no-flag behavior.
- Clean upstream patch application/source comparison and whitespace checks passed.

Ignored evidence: `startup-{build,install,test}.log`,
`window-check-CrystalMenu12-startup/{events.log,results.json,remembered-rom.png,returned.png}`,
and `startup-live-{first,reopen}.png`, `startup-fe-after-quit.png` under
`output/rg280v-simplemenu/`.
