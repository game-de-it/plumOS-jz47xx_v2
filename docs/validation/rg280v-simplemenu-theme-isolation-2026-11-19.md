# SimpleMenu / Simple Quest navigation isolation

## New physical evidence from the user

0A works normally. Simple Quest has apparent jumps throughout system selection.
First-level categories work except Apps and Games; second-level system selection
is problematic. Do not edit the author's theme files or assume a universal input
fault. The previous layout commit f9d26f8 remains undeployed.

## Source findings (pinned local upstream checkout)

- `screen.c:showCurrentGroup` displays the selected group's background PNG.
  `showConsole` displays the selected section's `systemLogoSurface`. Neither
  function computes a Simple Quest cursor position from a dynamic menu list.
- Simple Quest's supplied 320x240 images contain category names, system names,
  and selection arrows. `theme.ini` sets `display_section_group_name = 0`.
  Its visual menus therefore describe an artwork-specific fixed layout.
- `control.c:advanceSection` / `rewindSection` traverse the configured sections
  and skip systems whose ROM count is zero. Missing ROMs can thus cause additional
  legitimate selection skips even after ordering is corrected.
- Installer generates four group INIs (arcades, consoles, handhelds, computers),
  with no Apps and Games group. Original theme includes `apps and games.png`.
  That visible entry has no logical target in this installation. This is an
  integration omission, not evidence of a key event being lost.
- Existing INI order disagrees with the image order (documented in the Nov18
  layout report). A generic dynamic theme such as 0A does not have that same
  fixed-image-list constraint.

## Scope and decision

Evidence supports a theme/layout integration problem, but does not yet rule out
an additional input fault. Do not add SimpleQuest-name conditionals to the input
handler or edit PNGs. Do not claim the Nov18 ordering change alone fixes all
reported jumps. A general theme metadata/runtime compatibility mechanism may be
appropriate for image-based menus, but deciding it requires the A/B evidence.
Ordinary theme behavior and registered system routes must remain intact.

## Prepared A/B procedure

The existing isolated-HOME cursor regression runner now accepts `--theme-index`
0/1/2 for sorted installed themes 0A/SimpleQuest/SimpleQuest2. Same executable,
same section INIs, same initial selection and injected inputs. In addition to
queued/held input checks, it records 13 system-selection positions and screenshots
for each theme. Compare logical group/section sequences separately from the
visible arrows. User HOME and theme artwork are untouched; FE is restored after
the diagnostic run.

- Identical logical sequences + different apparent jumps: artwork/layout issue.
- Different logical sequences: investigate common runtime/input/timing path.
- Matching system IDs but incorrect game launched: investigate section/resource
  association rather than treating it as a cursor rendering issue.

`--help` and Python syntax checked; Git whitespace check passed. **The new A/B
procedure has not run on hardware.** ADB port5041 currently lists no device.
Asked user to reconnect; no additional runtime or theme changes were deployed.

## Real-device A/B result after USB reconnect

Ran the same isolated-HOME procedure on the same installed binary with theme0
(0A) and theme1 (SimpleQuest). Both completed all nine checks. Initial group was
consoles, with installed section INIs unchanged. Input trace after each DOWN
release and a settled screenshot were recorded. The runner now waits for release
processing rather than sampling during slow ROM counting. One capture attempt
returned `Text file busy`; the failed run restored FE, and subsequent complete
runs passed with bounded capture retry. Do not use that failed run as evidence.

| Check | 0A | SimpleQuest |
| --- | --- | --- |
| System indices, initial + twelve DOWN taps | 1,2,3,4,5,6,7,8,9,10,0,1,2 | identical |
| ROM positions, five DOWN + five UP | 1,2,3,4,5,4,3,2,1,0 | identical |
| Queued/opposite keys, repeat, other button while held | passed | passed |
| B+DOWN and held A (no accidental game launch) | passed | passed |

SimpleQuest's actual screenshots for section2 (Genesis) then section3 (Master
System) show the embedded arrow moving UP despite one DOWN event advancing the
logical section once. Their menu pixel crops match the corresponding original
theme PNGs within RGB565 quantization: max channel error 7/3/7, mean error below
0.015/255. This excludes scrambled/wrongly positioned rendering for those samples:
SimpleMenu is displaying the original images associated with the selected IDs.

Conclusion: the reproduced system-selection jumps are an image-menu/layout
integration mismatch, not a theme-dependent input-index jump. Ordinary ROM-list
navigation and the tested common input cases agree between themes. This does not
claim every physical input pattern or every system/group has been exhaustively
tested. Fixed artwork menus in other themes could share the same layout constraint;
this is not a reason to change generic input timing again or edit author PNGs.

The missing Apps/Games logical group is a separate integration omission. The
Nov18 order-only correction was not deployed during this A/B test. A complete fix
should keep original assets and reconcile actual registered items and image-menu
layout in the SimpleMenu integration/runtime, with ordinary themes unaffected.

Evidence (ignored host output):

- `output/rg280v-simplemenu/input-check-theme-{0,1}/results.json`
- same directories: `events.log` and `section-00.png` through `section-12.png`
- `output/rg280v-simplemenu/ab-comparison.json`
- `output/rg280v-simplemenu/ab-user-state-{before,after}.sha256`

Executable, user saved selection, config and favorites hashes remained identical
across the final A/B runs. FE was restored, with no remaining SimpleMenu process.
No theme assets, system INIs, emulator routes or kernel were changed.
