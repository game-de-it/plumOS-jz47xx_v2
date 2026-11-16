# RG280V system information font (2026-11-16)

The RG280V screenshot before the change was 320 x 480 pixels. The fixed-width
18-pixel settings font clipped the "System Settings - INFORMATION" title and
the "Device Model" value at the right edge. The information screen now uses
the existing proportional FreeType font at the same 18-pixel height for its
title and rows; other settings screens retain their current font.

Measured with the bundled font at 18 pixels, the title is 269 pixels wide and
"Device Model: ANBERNIC RG280V" is 274 pixels wide. The available widths are
298 and 276 pixels respectively. The updated FE binary was installed on SD1,
with the previous binary saved under `/media/data/local/backups/`.

The user confirmed that the text fits on the RG280V after the update.
