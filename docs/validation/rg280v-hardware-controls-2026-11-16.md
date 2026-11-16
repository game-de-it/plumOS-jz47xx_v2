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
- A screen-off-only fallback was considered but rejected because it would keep the system running. No such fallback was installed. The temporary `freeze` script was removed and the original `mem` script restored. This was the failing baseline before the OST fix documented below.

## Sleep wake-path diagnosis

- The FE-only Sleep path also failed to wake with the power key. Reconnecting USB during Sleep did not wake it. RESET returned to FE after each trial, so the failure does not require an emulator or USB bus power.
- While awake, the power key incremented GPIOA IRQ 44 and `gpio-keys/power/wakeup` reported `enabled`. Neither a trial changing the device-tree power-key wake action to asserted edge nor a trial reading the actual GPIO level during IRQ acknowledgement restored wake. Both trial kernels were reverted to the original boot image after their failed physical tests.
- The JZ4740 RTC clock had initially been unset. After setting the time, `rtcwake -m no -s 25` raised RTC IRQ 32 while awake and cleared the alarm. `rtcwake -m mem -s 20` did not restore ping, ADB or FE after the alarm deadline; RESET restored FE. The RTC date after RESET had advanced beyond the target. This does not prove the alarm was delivered in suspend, but it disproves a power-key-only explanation.
- A temporary 6.8 diagnostic kernel with `CONFIG_PM_DEBUG=y` and `CONFIG_PM_SLEEP_DEBUG=y` enabled `/sys/power/pm_test`. The `freezer` stage returned after five seconds (`RESULT:0`). The `devices` stage also returned (`RESULT:0`) but emitted `WARNING` from `__flush_work` during `drm_kms_helper_poll_disable` / `drm_mode_config_helper_suspend`; the warning needs follow-up, though this stage did resume. The `platform` stage did not return after its five-second interval and ADB/ping stayed offline. The user pressed RESET, and FE booted. The original boot image was restored from the SD1 backup, and its SHA-256 was verified as `66024f1a3061d351d8d3bc21ced511961bde9aa53afeed9bd88c88ba7cc44087` before and after reboot. On the restored kernel, `/sys/power/pm_test` was absent and the boot log reached `plumOS RG280V: READY`.
- The 6.8 Ingenic platform suspend hook in `arch/mips/generic/board-ingenic.c` enters `wait`; the old 6.2 source has the same hook. The failed `platform` test localizes the fault before the actual CPU sleep instruction, but the last in-kernel operation still needs a log channel that survives RESET (for example UART or a deliberately instrumented persistent marker).

## Persistent RTC marker findings

The upstream PM trace facility depends on x86 in this kernel, so temporary diagnostic kernels wrote a small stage marker into the JZ4770 RTC scratchpad. This invalidates the RTC date until `RTC_SET_TIME` is called again. The diagnostic code and trial changes are recorded in `scripts/patch-rg280v-pm-marker.py`, `scripts/patch-rg280v-pm-noirq.py`, `scripts/patch-rg280v-pm-device.py`, and `scripts/patch-rg280v-ost-suspend-test.py`.

- After the hanging `platform` test, RESET preserved `0x504d0004`, placing the stop inside `dpm_suspend_noirq()`.
- A finer trial preserved `0x504d000d`: `device_wakeup_arm_wake_irqs()` and `suspend_device_irqs()` completed, but the noirq device loop did not.
- A per-device trial preserved `0x518c0a0c`. The 24-bit name hash matched only `/sys/devices/platform/10002000.timer/100020e0.timer` in the captured sysfs list. Its driver is `ingenic-ost`; the marker was recorded immediately before its noirq suspend callback.
- A comparison kernel that left the OST clock running in `ingenic_ost_suspend()` and skipped re-enabling it in the matching resume callback returned from the `platform` PM test (`RESULT:0`). This establishes the OST clock gate as the cause of the diagnostic test hang. Timed `rtcwake -m mem -s 20` still did not bring back ping or ADB after the alarm deadline; the subsequent power-key and CPU/core checks are recorded below.

## Accepted Sleep fix

- With the OST clock left running, `pm_test=processors` and `pm_test=core` both returned (`RESULT:0`). The in-game/FE power key then resumed from deep suspend three times on the diagnostic kernel.
- The production kernel was rebuilt from the 6.8 source with only the OST change. The temporary PM markers and `CONFIG_PM_DEBUG` were removed. The deployed `/boot/uzImage.bin` SHA-256 is `7c2563ccd9934a8245b7c6bb2bbc5e590f638307d864d9b2efede638bd4d3c70`; the former image remains on SD1 as `/boot/uzImage.bin.pre-wakepress`. RTC time was restored with `RTC_SET_TIME` after removing the marker code.
- Physical production-kernel checks: FE Sleep/resume passed; NES standalone and PicoArch Sleep/resume passed; Sleep/resume with USB unplugged passed. The kernel log shows five `PM: suspend entry (deep)` and `PM: suspend exit` pairs under one boot ID, `b13baea5-668a-46e1-9127-2c30783fcde7`. This confirms real deep suspend and resume without reboot, across the tested routes.
- `patches/0001-rg280v-keep-ost-clock-running-in-suspend.patch` is listed in `configs/plumos_rg280v_defconfig` for subsequent RG280V builds. `patch --dry-run -p1` against the unmodified 6.8 source passed, and the equivalent production kernel was built and checked on hardware.
- Timed RTC wake was not fixed by this OST change; the user requirement for power-key Sleep/resume passed, while RTC alarm wake remains a separate follow-up. Power-button long-hold shutdown before userspace boot is also separate and was not changed here.

PicoArch FCEUmm showed green color artifacts in Akumajou Densetsu before opening the power menu. This is a separate emulator display issue. It was not used as evidence for power-menu rendering; SuperGrafx was the PicoArch control.
