# RG280V PicoArch cold launch investigation (2026-11-16)

The user reported that a NES PicoArch game takes longer to open immediately
after boot, while opening it again is quick. The device was connected by ADB;
no game was running during the following measurements.

`plumos-picoarch-launch` calls `plumos-prepare-opk-input` before executing
PicoArch. After a reboot, the input preparation took 5,610 ms on the first
invocation and 40 ms on the second. The first invocation created the udev
database entry `ID_INPUT_KEY=1` and started `udevd`. The core and ROM were not
launched in this test, so this is a measured part of the launch delay rather
than a full launch-time measurement.

A second reboot isolated the steps: querying the input device took 80 ms,
copying the rule 20 ms, starting `udevd --daemon` 5,830 ms, reloading rules
20 ms, running `udevadm test` 80 ms, and verifying the property 20 ms.
Starting `udevd` was therefore the dominant measured cost. In a separate
boot, running `udevadm test` without the daemon still took 6,040 ms.
Kernel `random: crng init done` appeared at the end of the long wait in both
boots (29.26 s and 27.05 s uptime). This timing strongly suggests a wait for
random initialization inside eudev, but the exact blocked syscall was not
traced.

The delay is specific to the lazy input setup, not an inherent PicoArch
requirement. Starting preparation in the background during boot alone did not
fully solve it: in the first test it started at 3.25 s, but waited for the
kernel random pool until 11.49 s. FE was ready at 4.74 s, leaving a window
where a rapid first launch still waited. The user reported that it still felt
slightly slow. This test also exposed that `udevd --daemon` inherited the
preparation lock; the helper now closes that descriptor in the daemon child.

The final candidate registers the RG280V's fixed `gpio-keys` event in the
libudev runtime database directly. It adds `ID_INPUT=1` and `ID_INPUT_KEY=1`
and marks a new entry initialized, preserving an existing entry if present.
The original udev rule and daemon path remain as a fallback if the direct
registration does not verify. A boot-time helper starts after SD1 data is
mounted, and `flock` serializes it with any unusually early game launch.
This avoids weakening or bypassing kernel random initialization.

On the first reboot with this candidate, `INPUT_PREP_START` was at 3.33 s,
`INPUT_PREP_READY` at 3.92 s, and FE `READY` at 4.55 s. `udevd` was not
running; `udevadm info` reported both input properties for `event2`.
A subsequent helper call took 50 ms. After a comment-only rebuild, the final
boot had `INPUT_PREP_READY` at 3.94 s and FE `READY` at 4.65 s, again without
`udevd`. The deployed rootfs SHA-256 is
`9d9ac8852a7640600684e352c423161ce12f2a685e89417964b5b959789584e3`;
the helper SHA-256 is
`6ae4152305bd4fc6fe20c256a4d6b4ecb84f64f83d8dc82f88fbda20856bc134`.
The prior rootfs and helper were backed up on SD1 under
`/media/data/local/backups/` before deployment. The user confirmed that the
first NES PicoArch launch became faster, D-pad and A/B worked, SELECT+START
opened its menu, and Exit returned to FE. A standalone SA FCEUX game also
passed input, menu, and FE-return checks. These are physical observations;
only the input-preparation part of launch time was measured numerically.
The direct database entry depends on the eudev format in this pinned rootfs;
an eudev update should repeat the cold-boot input check.
