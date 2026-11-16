# RG280V FE settings compared with V90S source (2026-11-16)

## Reference and cause

Reference: V90S public repository at `f797ed4`, `src/frontend/plumos_controller_ui.c`, `package/frontend-v90s/plumos/config/frontend/menus.json`, `apps.json`, and `share/frontend/lang/*.lang`. The RG280V FE was forked from the same controller source, but device-specific early returns in `add_ui_settings_entries` and `add_system_settings_entries` hid working shared settings. The earlier START-menu audit inspected only the top-level menu, so its conclusion did not cover these nested pages.

## Source comparison and disposition

| Page | V90S | RG280V after this change | Reason / evidence |
| --- | --- | --- | --- |
| START | UI Settings, System Settings, Network Settings, Apps, HELP, Reboot, Shutdown | UI Settings, System Settings, HELP, Reboot, Shutdown | No RG280V Wi-Fi; Apps launchers and thumbnail scraper are not packaged. The common FE code alone does not make those routes functional. |
| UI Settings | Refresh TOP, UI Mode, Show Empty Systems, Favorites On TOP, Recent On TOP, ROM Cursor Wrap, Open Last ROM At Boot, Sort Systems, Sort ROMs, Scan On Enter, Theme Settings | Same 11 entries | All have common FE read/write or navigation handlers. The RG280V theme package and Graphic renderer are present. |
| Theme Settings | Theme, Name, Status, Layout, TOP Layout, Transition, Time, Axis, Easing, Font | Same shared page | Available through the restored UI entry. Only the installed `default` theme can be selected. |
| System Settings | Volume, Brightness, Lumination, Display Color, Time Settings, Language, System Update, Factory Reset, INFORMATION | Volume, Brightness, Time Settings, Language, INFORMATION | RG280V has working volume/backlight and RTC. No RG280V display enhancement/color backend, signed update helper, or factory defaults are installed. |
| Time Settings | Current Time, Automatic Time, Sync Now, RTC Status, Timezone, Manual Time | Current Time, RTC Status, Timezone, Manual Time | Wi-Fi/NTP options are omitted. Manual time uses `settimeofday` and `RTC_SET_TIME`; timezone is saved to FE config and `/etc/TZ`. |
| Manual Time | Current Time, Timezone, Year, Month, Day, Hour, Minute, Apply Manual Time | Same shared page | The Apply action is connected to RG280V RTC. |
| Language | English, Japanese, Chinese, Portuguese, French, German | Same six V90S language files | Original V90S files are packaged into the RG280V image and deployed with the FE. |
| INFORMATION | Model, plumOS, Vendor, Kernel, GPU, Display, Audio, Storage, Memory, Base OS | Model, plumOS, Kernel, Display, Audio, Storage, Memory | Vendor/Base OS are V90S stock-OS concepts. RG280V has no independently reported GPU backend; display backend is shown. |

The common FE also contains Performance Settings, but V90S does not register it in START. No performance item was added as part of this V90S parity change.

## Device verification

- Built the MIPS/uClibc FE and installed the binary with matching SHA-256 `4b7bbe89e0fe7d52321792a8ba8197ef9930c27bb5a70e79f42b4f7dce3cc5bd`. The previous binary and both settings files were backed up on SD1 before the update.
- Captured UI Settings at the first and last entries. The restored labels and values fit at one proportional font size. Entered Theme Settings and returned.
- Changed `Favorites On TOP` from true to false and back through the FE; both values appeared in the saved JSON. Restored the original settings file afterward and confirmed its SHA-256 matches the backup.
- Opened System Settings, Time Settings, and Manual Time. Applied the current minute and verified that `date +%s` and `/sys/class/rtc/rtc0/since_epoch` matched. Restored the original system settings JSON after the test.
- The minute-granularity test left the device clock about 106 seconds behind the Mac. A temporary MIPS diagnostic set both system time and RTC to the Mac epoch; all three epoch readings then matched. The temporary binary was removed from SD1.
- Switched FE language to Japanese through the menu, saw the translated System Settings screen and `ja.lang` in saved config, then switched back to English. The original JSON was restored.
- Restarted the FE and verified `/etc/TZ` contains `JST-9`; the shell displays JST. FE remained running. No reboot, shutdown, emulator launch, or full six-language visual sweep was performed in this change.

Local DRM captures are under ignored `output/rg280v-fe/`; no ROM or BIOS data was added to Git.
