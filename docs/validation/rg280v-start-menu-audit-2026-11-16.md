# RG280V START menu comparison (2026-11-16)

## Reference and deployed state

Compared the checked-in and device-installed `menus.json` with Bubble's
`package/frontend-bubble/plumos/config/frontend/menus.json`, RK2020's common
frontend seed and device menu, and pixel2's common frontend seed and device
menu. The installed RG280V file matches the checked-in five-entry menu.
`plumos-text-ui menu start` also lists the same five entries and actions.

| Entry | RG280V | Other plumOS series | Assessment |
| --- | --- | --- | --- |
| UI Settings | present | present | Opens on device; display fits. |
| System Settings | present | present | Opens on device; display fits. |
| Network Settings | absent | present | Wi-Fi controls are not applicable to RG280V. USB/ADB is configured elsewhere; a dedicated USB network page is not ported. |
| Performance Settings | absent | present on Bubble | FE code contains the page and CPU policy routines, and the text UI command exists on device. START does not expose it; no end-to-end device test of this page. |
| Apps | absent | present | RG280V's installed `apps.json` is empty. The Apps submenu code exists, but no RG280V app catalog or packaged app launchers are ported. |
| HELP | present | present | Opens on device; text fits. |
| Reboot | present | present in common menu | START route was not executed in this audit. The power-menu Reboot route passed earlier physical testing. |
| Shutdown | present | present in common menu | START route was not executed in this audit. The power-menu Shutdown route passed earlier physical testing. |

RK2020 and pixel2 device menus use a single POWER entry in place of separate
Reboot and Shutdown; this is a device policy difference. The RG280V hardware
power menu already supplies Sleep, Reboot, Shutdown and Cancel, and its paths
were physically validated separately.

## Display and navigation

Captured the live 320 x 240 logical DRM frame after opening START. `START`,
`UI SETTINGS`, `SYSTEM SETTINGS`, `HELP`, `REBOOT` and `SHUTDOWN` are all
visible with no text cut off or overlap. The longest entry, `System Settings`,
is 15 pixel-font cells (180 px at scale 2), within the available 276 px text
area. Entered UI Settings, System Settings and HELP with injected controller
events; captured each screen and returned to START, then TOP using B. The HELP
text fits. No visual or navigation defect was found in the five visible START
items. Local screenshots are ignored artifacts under `output/rg280v-fe/`:
`start-menu-audit.png`, `start-menu-ui-settings-audit.png`,
`start-menu-system-settings-audit.png`, `start-menu-help-audit.png`, and
`start-menu-return-top-audit.png`.

## Functional gaps

- Performance Settings is implemented in shared source but remains unreachable
  from RG280V's START menu. Exposing it requires checking that every offered
  CPU policy is supported and that saving/resetting it works on this device.
- Apps is not yet a usable menu on RG280V because its catalog is empty.
  Copying another device's app entries would create dead routes: scraper,
  file manager, music player, RetroArch menu, PortMaster and other launchers
  are not packaged here.
- `confirm: true` is present on Reboot and Shutdown in the RG280V menu JSON,
  but the shared START handler invokes the power action directly and does not
  read that flag. The separate hardware POWER menu offers Cancel. This audit
  did not trigger START Reboot or Shutdown to avoid an unnecessary power cycle.

No START menu configuration or runtime behavior was changed during this audit.
