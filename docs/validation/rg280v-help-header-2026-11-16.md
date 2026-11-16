# RG280V HELP and header (2026-11-16)

The RG280V HELP text used the fixed-width 18-pixel font and clipped long
instructions at the right edge. The HELP page now uses the same 18-pixel
proportional font as the information page, and the USB line is shortened to
"USB: ADB connection". With the bundled font, its longest remaining line
measures 247 pixels in a 264-pixel content area.

The existing plumOS frontend header source and Bubble screenshots show a
model title on the left and time, Wi-Fi, battery on the right. RG280V has no
Wi-Fi. Its 320-pixel screen keeps the same single-row pixel-font layout and
colors, with `plumOS RG280V` on the left and time plus battery on the right.
Eleven-pixel glyph spacing keeps both labels within the captured 320 x 480
device frame without overlap. The user confirmed the layout is intended.

The device has `/sys/class/rtc/rtc0/since_epoch`, so the local clock is
displayed when the RTC reports a valid epoch. A device without a valid RTC
shows only the battery. The RG280V battery driver exposes voltage but no
capacity; the numeric percentage is a coarse estimate derived from voltage,
and may be inaccurate while charging or under load. The header shows `CHG`
when the battery status reports charging or USB power is online, and `BAT`
otherwise. The displayed value is cached for one second. The original FE
binary was backed up on SD1 before deployment. The user confirmed that the
header and HELP text are readable on the device. The unplugged `BAT` display
was not separately checked on hardware.
