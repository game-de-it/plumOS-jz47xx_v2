# RG280V HELP and header (2026-11-16)

The RG280V HELP text used the fixed-width 18-pixel font and clipped long
instructions at the right edge. The HELP page now uses the same 18-pixel
proportional font as the information page, and the USB line is shortened to
"USB: ADB connection". With the bundled font, its longest remaining line
measures 247 pixels in a 264-pixel content area.

The existing plumOS frontend header source and Bubble screenshots show a
model title on the left and time, Wi-Fi, battery on the right. RG280V has no
Wi-Fi. Its 320-pixel screen uses the same pixel font, colors and top-bar
components in two rows: `plumOS RG280V` above the time and battery label.
The captured 320 x 480 device frame shows both rows without overlap.

The device has `/sys/class/rtc/rtc0/since_epoch`, so the local clock is
displayed when the RTC reports a valid epoch. A device without a valid RTC
shows only the battery. The RG280V battery driver exposes voltage but no
capacity; the header therefore marks its voltage-derived percentage as
approximate with `~`. The displayed value is cached for one second, and may
be inaccurate while charging or under load. The original FE binary was
backed up on SD1 before deployment. HELP page physical acceptance is pending.
