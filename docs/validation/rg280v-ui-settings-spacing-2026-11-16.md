# RG280V UI Settings spacing (2026-11-16)

The five-entry RG280V UI Settings page reserved the shared renderer's
two-line footer area, yet that area was blank on the device. The resulting
window showed only four entries and left a large empty region at the bottom.

For RG280V UI Settings only, the FE now omits the unused footer reservation
and lays out five entries with 34 logical pixels between rows. The viewport
calculation and framebuffer renderer use the same spacing and bottom limit.
Other settings pages keep their existing layout.

The MIPS FE built without warnings. The previous installed binary was saved
on SD1 as `plumos-controller-ui.before-ui-spacing-20261116`, and the new
binary was transferred and checked against SHA-256
`3521242beeb3469f545536ebe0e3f8e92ca8ab4d6ec3d0785ca89c33fe0fa584`.
The device displayed all five entries at once; moving the cursor to the final
`SCAN ON ENTER` row kept it fully visible. B returned through START to the
normal TOP screen. Local capture artifacts are under `output/rg280v-fe/`:
`ui-settings-spacing-final.png`, `ui-settings-spacing-last-selected.png`, and
`ui-settings-return-top-final.png`.
