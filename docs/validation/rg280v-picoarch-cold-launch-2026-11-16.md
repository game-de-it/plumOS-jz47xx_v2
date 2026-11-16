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

The delay is specific to the current lazy input setup, not an inherent
PicoArch requirement. A future change can move the setup off the launch path
or avoid the blocking path; it must keep SDL key discovery working on a cold
boot and must not lengthen the accepted FE boot time.
