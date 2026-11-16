# RG280V system settings layout correction (2026-11-16)

After the V90S settings restoration, the RG280V System Settings screen showed the fifth item (`INFORMATION`) under the footer panel. The live DRM capture confirmed that the panel covered the selected row and clipped long help text. RG280V maps the 320x480 output to a 320x240 logical FE screen with vertical scale 2. The FE's UI Settings page already used a five-row layout without the footer; other settings pages still used the footer layout.

The same RG280V five-row layout now applies to System Settings and its nested settings pages. The renderer and FE window calculation use one marker and the same 34 logical-pixel row spacing. The footer is omitted on RG280V settings pages, leaving room for five complete rows. V90S and other device layouts are unchanged; the brightness test page keeps its separate layout.

Built and installed the MIPS FE after backing up the previous binary on SD1. Local and installed SHA-256 matched: `e213355bfd24b46511f9c9020c271b758c8d1de1692b071cec7d1bdeb0e843a4`. Live DRM captures show all five System Settings items, the last selected item, and the first and last Information rows without panel overlap. The Time Settings page shows all four items without clipping. The FE remains running, and the temporary key injector was removed. Captures are in ignored `output/rg280v-fe/`.
