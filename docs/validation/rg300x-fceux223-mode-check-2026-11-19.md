# RG300X FCEUX 2.2.3 startup correction

## Cause and scope

The installed FCEUX OPK matched the accepted pinned package
`7834f7b191e6eafde2986b2ab4ef77e29903b6996a3afbe6c84fb3ab927c9b5b`.
Both the ordinary profile and a clean `/tmp` HOME failed, without telemetry.
The clean launch printed `Initializing video...` before exiting 139.

An SDL call probe showed the actual failing check:

```text
SDL_MODE_OK 320x240x16 flags=40000101 result=0
Segmentation fault
```

The OpenDingux SDL source in the SDK, `sdl-97557d6bd`, separates physical display
modes from the scalable application surface. The public `SDL_VideoModeOK` checks
`SDL_ListModes`, which KMSDRM implements using physical panel modes. The actual
`SDL_SetVideoMode` path instead uses the backend's `VideoModeOK` callback.
Thus a 640×480 RG300X can create a scaled 320×240 surface, while the public
preflight says no. This older FCEUX then continues with its screen unset.

The correction is in the existing compatibility library source
`scripts/rg280v-fceux-menu.c`. Only the FCEUX 2.2.3 launcher enables
`PLUMOS_FCEUX_LEGACY_MODE_CHECK=1`. It preserves positive SDL answers, and only
corrects zero for the legacy 16-bit NES modes on an initialized KMSDRM backend
whose panel can fit that surface. The recognized widths/heights cover software
320×240 and native/clipped NES modes. Unsupported sizes/depths, other drivers,
and other routes retain their existing answers. The accepted emulator binary,
its renderer, ROMs and user input settings were not replaced.

## Validation

- New library MIPS build and remote SHA-256 matched:
  `36e0867c3e81991fac7a8bd7f1b438d07519d30f81a8d441dec2e87ef196d57f`.
- With correction: check returned 16, actual SDL mode creation returned a valid
  320×240 RGB565 surface, and audio initialized. This proves actual mode creation,
  rather than merely changing the reported error.
- Baseball reached an active match, with about 60.0–60.1 FPS windows, nonzero
  32 kHz PCM and zero observed ALSA write errors/underruns. SELECT+START opened
  the menu and its Exit terminated the application normally (child exit 0).
- Super Mario Bros. reached World 1-1 using the production launcher and existing
  HOME/config, at about 59.9–60.2 FPS in the initial measured windows. Its game
  capture showed normal colors and no leftover frontend image.
- The user confirmed Mario's picture, BGM, controls, SELECT+START menu and
  return-to-game were all normal, and additionally verified physical volume
  buttons and START+left/right brightness controls.
- Final-library validation used the ordinary native FE and the unchanged system
  selection `standalone:fceux223` to load Akumajou Densetsu. Its emulator menu
  identified that ROM; normal Exit logged child and route exit 0 and returned
  to the same FE PID 1814 / NES ROM list. No FCEUX process remained.
- `scripts/verify-fceux-legacy-mode-check.sh` compiles the actual hook source
  against a fake SDL backend and tests 18 panel/mode combinations plus negative
  cases: disabled flag, other driver, failed driver query, insufficient panel,
  unknown mode/depth and unchanged positive backend result. It runs natively in
  the SDK container; it is not physical validation of the other handhelds.
  A mode-switch case also checks returning to software size after a smaller
  native surface: physical modes, not mutable current surface dimensions, are
  used to bound the correction.
- Original library and launcher were retained on the test SD under
  `plumos/backups/rg300x-fceux223-mode-fix/` before replacement. The global rootfs
  SDL library was not changed. The common test-image assembly now also overlays
  the updated launcher and built compatibility library over the older runtime
  snapshot. The already-created image file is not silently rewritten.

Private logs/screenshots are under `output/rg300x-validation/`. ROMs, BIOS,
other emulator binaries and core-selection preferences were not replaced.
