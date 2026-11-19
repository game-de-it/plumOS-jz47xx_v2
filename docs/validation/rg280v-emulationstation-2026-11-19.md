# RG280V EmulationStation integration — 2026-11-19

## Sources and integration

- Original JZ4770 source: `lualiliu/emulationstation-on-jz4770`, commit `3ab83b15b7bf033bd1a02c9e307b4fc4219107b7`.
- RG350 distribution/theme: `ManuelSch81/RG350-EmulationStation_configured`, commit `3c8f0473e539ae7a36e8dd5e39180dcdc33cf0f8`. Only the original `simplegcw` theme is taken; its bundled emulators, ROMs and BIOS are not installed.
- Source build with the existing MIPS/uClibc soft-float toolchain. The distributed OPK binary is hard-float; it is not used.
- SDL2/OpenGL ES uses the installed KMSDRM/Mesa stack. Logical 320×240 is drawn to the panel's 320×480 buffer; viewport and scissor follow the vertical doubling.
- FreeImage replaced with the existing SDL image API; EmulationStation gets private PNG/JPEG/SVG support and libcurl. Global SDL/ALSA and other frontends remain unchanged.
- Fixes for modern GCC/Eigen: conflicting `round` helper renamed, missing `<stack>` included. Character case conversion casts to unsigned byte so UTF-8 Japanese filenames do not abort uClibc assertions.
- Existing FE CJK fallback fonts are reused. Offline port omits network scraping UI and OS restart/shutdown actions. START → `RETURN TO PLUMOS` exits the frontend; physical OS power handling remains in plumOS.
- 26 enabled systems use the current formal FE defaults. Generated full names include `SA:core` or `PICO:core`; launchers validate the SD2 path and invoke the existing `plumos-text-ui` route.
- Gamelist writes are forced into the app's SD1 home. SD2 remains read-only. Settings/input stay user owned; generated system routes and stock theme refresh on install. Other theme sets remain untouched.

## Device checks

- SDL2 OpenGL ES context initialized successfully on the real RG280V.
- Main carousel, original JPEG artwork, NES ROM list, START menu and launch/exit displays captured from the active DRM plane.
- Native FE Apps → EmulationStation opens the port. A opens NES; arrows select ROMs; A launches `Baseball.nes` through formal SA FCEUX.
- SELECT+START opens FCEUX's menu; normal Exit returns to the EmulationStation ROM list. This was repeated after the final rendering changes.
- START → `RETURN TO PLUMOS` returns to the existing native FE Apps screen, preserving selection. No forced reboot or default-FE replacement.
- Startup initially showed a black interval while preloading all views. ROM views now build lazily, 1280×720 theme backdrops are reduced proportionally to 240 pixels high, and frame clearing occurs before drawing rather than immediately after presenting the loading screen. The system carousel appears without input after startup; no exact startup-time benchmark is claimed.
- Diagnostics removed from the final binary. Audio quality, physical button feel and every machine/core combination were not re-audited; existing accepted emulator routes are reused.

## Build and install

- `scripts/build-rg280v-emulationstation.sh`: pinned sources, dependency packages, checked-in patch and private runtime. Restores the prior Buildroot configuration; no OS image build or flash.
- `python3 scripts/install-rg280v-emulationstation.py --register`: space check, archive hash verification, config backup, app-owned runtime/theme installation and Apps registration. Requires Pillow on the host for background reduction.
- HOME: `/media/data/plumos/home/emulationstation`.
- Runtime: `/media/data/plumos/emulationstation`.
- Logs: `/media/data/plumos/Logs/emulationstation.log` and the app home's `.emulationstation/es_log.txt`.
- Ignored captures/build evidence: `output/rg280v-emulationstation/`.

Sources: https://github.com/lualiliu/emulationstation-on-jz4770 and https://github.com/ManuelSch81/RG350-EmulationStation_configured .

## Follow-up: category navigation crash

The reported category-entry/back crash was reproduced with the original installed GPU driver. The failing copy was identified in the matching Mesa 23.2.1 etnaviv driver. The correction is packaged in an application-private DRI directory, selected only by the EmulationStation wrapper. Emulator launchers clear that selection before starting a game. The operating system's shared driver is unchanged.

- Regression check: `scripts/verify-rg280v-es-mesa-blit.py` extracts the actual Mesa copy function and runs it with checked memory boundaries. Original fails; corrected R8/RGBA copies and partial-tile fallback pass.
- Device check: all 26 categories, three complete circuits, five actions per category (enter/down/up/back/next): **390 actions, zero abnormal exits**, same frontend process throughout.
- Private-driver loading was checked against the running process. Diagnostic handlers were removed from the installed frontend binary.
- `scripts/build-rg280v-emulationstation-mesa.sh` builds the private driver and restores the SDK source and library afterward. The main frontend build script invokes it automatically.
- The installer preserves runtime symlinks; generated child launchers unset the private driver search path. Wrapper logs include the frontend exit status.
