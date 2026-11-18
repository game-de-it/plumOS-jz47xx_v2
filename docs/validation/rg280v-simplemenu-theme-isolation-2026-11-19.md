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
