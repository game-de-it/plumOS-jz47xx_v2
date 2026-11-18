# SimpleMenu theme selection order investigation

The user still observed unwanted cursor jumps after input fix a2751ca.
The earlier seven injected-input checks are insufficient to claim the physical
symptom resolved. Keep that input fix; investigate theme selection separately.

## Confirmed configuration mismatch

Simple Quest uses full-screen system PNGs with the system selection marker baked
into each image. The installer had reused plumOS system registration order.
Genesis -> Master System therefore moved the marker upward after a DOWN action
(approximately y116 -> y100). Neo Geo was also placed in arcades although its
supplied image selects consoles. Handheld and computer ordering disagreed too.

`assets/rg280v-simplemenu/system-order.json` now records order matching the original
theme artwork. No theme PNGs were edited or added to Git. Systems without supplied
logos keep SimpleMenu's fallback; NGPC, SuperGrafx, Neo Geo CD and Atari 800 remain
available. Their artwork coverage is separate from this ordering correction.

`install-rg280v-simplemenu.py --refresh-sections` explicitly updates existing INIs
and migrates saved selection by system name. It backs up the installed section
configuration and saved state. Theme, ROM positions and Favorites return target
are retained, including Neo Geo moving between groups. Unsupported saved-state
versions abort migration before deployment.

## Host validation

- Python compilation passed for installer and migration helper.
- `python3 scripts/test_simplemenu_section_layout.py`: six tests passed (category
  move, handheld reorder, Favorites return target, seed state, invalid version,
  invalid group order).
- Original SimpleQuest and SimpleQuest2 PNGs checked with Pillow: all eight
  theme/group combinations advance monotonically within each supplied menu page
  and never revisit a preceding page. Evidence is in ignored
  `output/rg280v-simplemenu/layout-art-check.json`.
- `git diff --check` passed.

## Pending device validation

Device transport stopped responding during investigation. ADB server port5041
has no connected device. USB Ethernet interface remains active, but neither ping
nor TCP5555 responds. This does not establish whether the UI is hung.
The layout correction has **not been installed** and physical input has **not
been rechecked**. Asked user which screen jumps and whether device/UI/USB remain
available. After reconnecting: exit SimpleMenu, run installer with
`--refresh-sections`, verify selected system survives, then check system/category
and ROM-list navigation on hardware. If ROM-list/settings still jump, collect
the actual physical event trace rather than treating artwork order as sufficient.
