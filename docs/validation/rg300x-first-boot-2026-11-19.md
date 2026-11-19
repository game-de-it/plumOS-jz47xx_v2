# RG300X initial hardware validation

The user wrote the private test image to a separate 64 GB SD1 and booted the
RG300X. The accepted RG280V SD1 was preserved.

## Confirmed

| Check | Evidence |
| --- | --- |
| Device identity | DT model `Anbernic RG-300X`, boot `model.txt=rg300x` |
| Storage | SD1 p1 128 MiB, p2 1536 MiB, p3 64 MiB; all mounted at the intended paths |
| Display | DRM 640×480, XR24, pitch 2560, 60 Hz; captured FE TOP and START menu |
| Input | gpio-keys on event2; user confirmed physical directions, A/B and START menu |
| Audio | ALSA gcw0-audio card0; user heard the 48 kHz stereo test tone normally |
| Hotkeys | Injected volume down/up changed PCM 45→39→45%; START+left/right changed backlight 8→6→8 |
| CPU | 996 MHz; no overclock changes made |
| Sleep | User selected Sleep and resumed to FE using the power key; FE PID 283 survived, kernel logged `PM: suspend exit` |
| Long power hold | User confirmed power-off after holding at least 10 seconds, then a normal power-on returned to FE; uptime reset, updated FE hash persisted |
| Header | After shared-renderer correction: PLUMOS RG300X, CHG with voltage-derived percentage; Wi-Fi omitted |
| RTC | RTC exists but date/time reads return EINVAL; header omits an uninitialized clock |

Raw logs and screenshots are private, generated files under
`output/rg300x-validation/`. The header-corrected FE binary on SD1 matches
SHA-256 `b8233f0d2cfaa79cbc5bb023dd1bf7d31259a49334a368b43886d241dbc2d852`.
The original binary is retained on that test card under
`plumos/backups/rg300x-firstboot/`.

## Remaining checks and findings

- Reboot/Shutdown menu actions, emulator display/audio/return, and game sleep
  have not yet been verified on this model. There is no SD2 currently inserted,
  so no ROM was copied to SD1 for this test.
- Suspend succeeds, but the kernel logs a warning in `__flush_work` called by
  `drm_kms_helper_poll_disable`. Source inspection shows that the Ingenic
  suspend hook calls `drm_mode_config_helper_suspend`, while the driver has no
  call to `drm_kms_helper_poll_init`. This points to uninitialized connector
  polling work; it is a pending kernel issue, not a verified fix. The kernel
  has not been changed during this hardware session.
- Both initial boot and boot after the long hold reported an unclean FAT user
  volume. An ordinary Shutdown and filesystem check remain necessary; do not
  equate the successful long-hold test with clean filesystem unmounting, and
  do not run repair on the mounted volume.
- The old TCP ADB transport remained offline after device/power transitions.
  Initial connection was refreshed on host server 5041; the subsequent boot
  was verified through a fresh development server on port 5042. This was host
  transport state, not proof of failed USB networking.
- The downloadable initial image predates the header correction; the device
  has the correction, and future image builds use the updated FE binary.
- RG350 and RG350M remain untested on hardware.
