# RG280V FE typography adjustment (2026-11-16)

The RG280V FE uses a 320x240 logical layout on a 320x480 display. The 18px FreeType text and 34px settings row spacing made START and nested pages feel crowded. The one-line plumOS header must retain the model name, time, and battery or charging status.

For RG280V, the FreeType glyph size at scale 2 is now 15px. The START menu uses 28 logical pixels per row; settings pages use 30. HELP uses 23 and shows all six instructions. The FE window calculation uses the same row spacing as the renderer, so the selection and visible page stay aligned. The header keeps the existing 5x7 pixel glyph shapes, resampled to 8x11 with a 9px character pitch. Its model name and status remain on one line. The HELP instructions were shortened so the renderer displays the D-pad and A/B lines. Other device layouts are unchanged.

`scripts/build-rg280v-fe.sh` completed. The previous FE binary was backed up on SD1 at `/media/data/plumos/bin/plumos-controller-ui.before-font-20261116`. The installed binary and local build matched SHA-256 `96d1598bd25b61843e54fbe5907d43d3e1e7780cff03523a80c99b14af7f3f42`. The FE stayed running after installation.

Live DRM captures in ignored `output/rg280v-fe/` checked TOP and START, the first and last UI Settings rows, theme first and last rows, all System Settings items, System Information, all six HELP lines, and all four Time Settings rows. The header retains `PLUMOS RG280V` and the time and `CHG 100` status without overlap. Text is within the screen bounds in these captures. The test key injector was removed and FE navigation returned to TOP. Physical readability can still differ from the captured pixels.
