# RG280V hardware controls and power menu — 2026-11-16

## Scope

- A boot service reads the RG280V hardware input event device. Volume buttons adjust the saved 20-step volume setting and START with D-pad left/right adjusts the saved 6-step brightness setting. Both use the existing plumOS control scripts.
- The frontend defers its START action until release so START with left/right does not open the frontend menu. Opening Settings reloads values changed by the boot service.
- A short power-button press during a game pauses the emulator and displays Sleep, Reboot, Shutdown and Cancel. B or the power button cancels; A chooses the highlighted action. FE keeps its own power menu.

## Display failure and correction

The first game overlay wrote into the emulator's live DRM framebuffer. Cursor movement produced transient noise. A second version handed DRM master to the FE overlay. It restored the plane but left the physical game screen in a four-way split although DRM plane metadata looked normal. Exiting the game to FE restored the display.

The replacement keeps the game's DRM master, mode, plane geometry and pixel format. It creates two dumb buffers with the game's framebuffer dimensions and format, renders the plumOS menu into the buffer that is not visible, and changes the plane framebuffer only after a frame is complete. It restores the original framebuffer before resuming the emulator. This avoids both live-buffer writes and display-mode handoff. A 3-second diagnostic overlay and physical cursor movement/cancel on FCEUX returned to a normal game image, with no reported noise or split display.

## Checks

- Physical: volume up/down and START plus left/right changed volume/brightness during a game.
- Physical: FE power menu labels fit on the screen.
- Physical: FCEUX power menu opened, cursor moved, B returned to a normal game screen with no noise or split image.
- Physical: PicoArch SuperGrafx (Air Zonk) power menu opened, cursor moved, B returned to the game normally.
- Capture: the final in-game menu follows the FE power screen's header, title, spacing, selection colors and 4-item order; the game plane remained 320×240 RGB565 scaled to the existing 320×480 output.
- Build: `bash scripts/build-rg280v-fe.sh` completed for MIPS.
- Transfer: checked SHA-256 of the uploaded power-menu binary before replacing the device copy.
- Syntax: `sh -n` on shell services and `bash -n` on deployment/image scripts completed.

## Power action trial

- Reboot: selected from the game menu. The device restarted into FE. The kernel boot ID changed from `9bb999fb-600e-46e3-8bb1-c84dc0e032dd` to `7883f112-f019-4dfb-88db-0338b1b6fa02`.
- Shutdown: selected from the game menu. The device powered off, then started normally with the physical power button and displayed FE. The subsequent boot ID was `92d1ce11-6dfe-4963-9b10-a1e66ddb8911`.
- Sleep: `mem` with the default `deep` mode turned off the screen but did not respond to a short power-button press. A trial with `freeze` had the same result. Ping and ADB were unavailable while suspended, and RESET restored FE in both cases. Repeating `mem` with the USB cable unplugged still failed to resume, so USB power alone does not explain it. `gpio-keys/power/wakeup` was `enabled`, and the device tree's power key has `wakeup-source`.
- A screen-off-only fallback was considered but rejected because it would keep the system running. No such fallback was installed. The temporary `freeze` script was removed and the original `mem` script restored. Sleep remains a failed physical gate; avoid selecting it until the kernel wake path is corrected.

PicoArch FCEUmm showed green color artifacts in Akumajou Densetsu before opening the power menu. This is a separate emulator display issue. It was not used as evidence for power-menu rendering; SuperGrafx was the PicoArch control.
