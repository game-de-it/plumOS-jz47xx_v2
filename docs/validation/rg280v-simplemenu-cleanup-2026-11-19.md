# Remove unused Simple Quest-specific integration workarounds

The user requested removing unnecessary Simple Quest-specific changes while
retaining proven common SimpleMenu fixes. The image-menu mismatch is documented
in the theme isolation report; original SimUI/ArtBook compatibility is documented
in the external themes report. Those reports remain historical evidence.

## Removed

- Simple Quest image-order metadata `system-order.json` and installer sorting by
  that metadata, including its Neo Geo category reassignment. New seeds again
  follow ordinary FE registration order/category mapping.
- `--refresh-sections`, its saved-state migration helper and six tests dedicated
  to that now-removed ordering migration. This experimental migration was never
  deployed; existing device section INIs therefore need no reverse migration.
- Mandatory SimpleQuest/SimpleQuest2 copying in the base installer. Base install
  now needs only built SimpleMenu resources, not privately downloaded themes.
- Simple Quest as the default for a fresh install/test: seed and cursor runner
  default to standard 0A. Named external theme selection remains supported.
- Obsolete generated Python bytecode for the removed helper/changed installer.

## Retained

- Exact native source patch and binary, including SDL queued-event order fix,
  release/repeat handling (250ms initial/80ms repeat), UTF-8/CJK font fallback,
  launch argument lifetime fix, RG280V display setup, managed CPU behavior and
  ordinary theme loading.
- SimpleMenu launcher/invoker and emulator exit -> SimpleMenu restoration.
- Common cursor regression and A/B screenshot/trace tooling, including selecting
  themes by name rather than assuming a numeric index.
- SimUI/ArtBook original external-theme installer and theme-index preservation.
- Existing user themes, preferences, favorites, ROM positions and routes. The
  optional original Simple Quest downloader remains available as an asset-fetch
  utility; it is not a runtime workaround or base-install dependency. No original
  theme assets were edited or deleted from the user's theme collection.

## Device update and checks

The old generated seed (6.5 MiB) was moved into a timestamped device backup under
`/media/data/plumos/backup/simplemenu-cleanup-*`; this is separate from user HOME.
Re-ran the cleaned base installer. New package/installed seed includes only 0A,
with fresh saved-state theme index0. User HOME is preserved by normal install.

Before/after SHA256 snapshots match for the installed binary, user saved state,
config, favorites, and all four user section-group INIs. Binary hash remains
`a056e7cd7c1c2b202cae1bda1bb28e019643c7f3c4e07bbe8d410b6c453c0153`.
The source patch, launcher and invoker have no diff. Archive checked for no
SimpleQuest payload and for standard 0A/default state.

Re-ran the common nine-case on-device cursor suite with `--theme-name SimUI`
and `--theme-name ArtBook`: **both passed all nine checks**. Results are under ignored
`output/rg280v-simplemenu/cleanup/` and normal per-theme evidence directories.
The checks cover queued/opposite keys, held/released direction, another key while
held, B+DOWN, A hold, full consoles traversal and ROM list down/up. No new emulator
or source changes justify repeating emulator/audio validation already passed in
the external-theme report.

Final hash check after both diagnostic runs still matches the pre-install user
state/binary/section snapshot. Confirmed plumOS FE process running and no remaining
SimpleMenu/emulator process.

Reproduction:

```sh
python3 scripts/install-rg280v-simplemenu.py
python3 scripts/check-rg280v-simplemenu-cursor.py --theme-name SimUI
python3 scripts/check-rg280v-simplemenu-cursor.py --theme-name ArtBook
```

Exit SimpleMenu before install/testing. Each regression run uses temporary HOME
and restores plumOS FE. Install requires an existing compiled runtime; optional
external theme installation is separate.
