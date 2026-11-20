# plumOS JZ47xx_v2 Developer Guide

[日本語](README.ja.md) · [Project overview](../../README.md) · [User guide](../user/README.md)

[Emulator licenses and upstream revisions](emulator-licenses.md)

## Boot and storage

The boot chain uses a JZ4770 UBIBoot variant, OpenDingux Linux 6.8 and mininit. The shared bootloader checks the four active-low D-pad signals before panel initialization. A held direction overrides the selection stored in `BOOTMOD.CFG` on p1. Each model's kernel file combines the common kernel payload with that model's DTB. Linux applies the device profile from the loaded DT's `compatible` value.

| Area | Filesystem and role |
| --- | --- |
| SD1 sectors before p1 | MBR and UBIBoot. The bootloader starts at sector 1. |
| SD1 p1, 128 MiB | FAT32 `PLUMOSBOOT` mounted at `/boot`. Model-specific kernel files, mininit, the paired rootfs and modules images, and the remembered model. |
| SD1 p2, 1.5 GiB | ext4 `PLUMOSDATA` mounted at `/media/data`. Managed frontend, emulators, apps, settings and setup state. |
| SD1 p3, initially 64 MiB | First boot expands it to the end of the card and creates FAT32 `PLUMOS` at `/media/user`. |
| SD2, optional | ROMs, BIOS files and artwork. The standard SD2 mount is read-only. |

`S00expand-multimodel-user` validates the boot card and seed layout, updates the p3 entry and tells Linux about the new size before formatting and mounting p3. It records completion on p2. `S96remember-boot-model` stores the selection on p1. Changing models therefore cannot reset the p3 setup state. When reviewing changes, preserve the bootloader area and the starts and sizes of p1 and p2.

## Source map

| Path | Responsibility |
| --- | --- |
| [configs/plumos_rg280v_defconfig](../../configs/plumos_rg280v_defconfig) | Buildroot configuration for the common MIPS base. |
| [board/rg280v/overlay](../../board/rg280v/overlay) | System startup, mount and hardware services. |
| [patches](../../patches) | Bootloader, kernel and emulator changes. |
| [src/frontend](../../src/frontend) | Frontend, library scanner, rendering and launch logic. |
| [assets/frontend/systems.json](../../assets/frontend/systems.json) | Source catalog for ROM aliases, extensions and launch profiles. Check the assembled image against it. |
| [assets/frontend/bin](../../assets/frontend/bin) | Hardware profiles and launch wrappers. |

## Add an OPK to a development card

The frontend's **START → Apps** menu scans `/media/data/apps/` on SD1's p2. Use a regular file with a lowercase `.opk` extension. Use letters, digits, hyphens, underscores and dots in the filename, and avoid leading or consecutive dots. The package needs a supported `.desktop` entry with `Name` and `Exec`, a JZ47xx-compatible MIPS executable, and its runtime libraries.

1. Shut down the handheld, then connect the development SD1 to a Linux computer using a card reader. Use `lsblk -f` to identify the card's ext4 `PLUMOSDATA` partition (p2).
2. Mount p2 read-write. If you mounted it at `/mnt/plumos-data`, run `sudo install -m 0644 my-app.opk /mnt/plumos-data/apps/my-app.opk`.
3. Unmount the partition, return SD1 to the handheld, and use **START → Apps** to check that the app appears, starts and returns to the frontend on exit.

To bundle the app in a custom image, place its build artifact at `output/rg280v-apps/<name>-rg280v.opk`, add `<name>` to the [candidate staging `APPLICATIONS` list](../../scripts/stage-jz47xx-validation.py), and rebuild.

## Build the base system

Use Git, Bash and Docker with Linux ARM64 container support. Run the commands from the repository root. The build scripts use a case-sensitive Docker volume for the Buildroot output. Source downloads and generated artifacts go under `work/` and `output/`.

```sh
./scripts/configure-rg280v.sh
./scripts/build-rg280v.sh
./scripts/verify-rg280v-build.sh
```

The configure script checks out the pinned OpenDingux Buildroot revision. Re-run it when changing the defconfig. The shared boot build uses [build-jz47xx-boot-in-container.sh](../../scripts/build-jz47xx-boot-in-container.sh) for the four DTBs and combined kernel files, and [build-jz47xx-multimodel-ubiboot-in-container.sh](../../scripts/build-jz47xx-multimodel-ubiboot-in-container.sh) for the model selector. The latter verifies the upstream UBIBoot archive, checks the D-pad GPIO wiring against all four DTBs and enforces the bootloader size limit.

The shared boot build expects the reference rootfs, modules and mininit in `output/jz47xx-multimodel/reference-boot/`. Keep this set matched to the kernel and verify its provenance before assembly.

[make-jz47xx-test-image-in-container.sh](../../scripts/make-jz47xx-test-image-in-container.sh) restores a private development snapshot. Its historical results remain useful for comparison. The snapshot can contain workstation- or device-specific data.

## Validate and package one SD image

Distribute the original IMG written for final hardware validation. Release packaging preserves every validated feature, bundled file, launch route, setting and service. It compresses the original IMG and generates checksums. Apply version metadata before final hardware validation, even when it is the only change.

1. Start from the latest validated configuration and review the candidate's changes and final test scope. Record source revisions and check the candidate for user data and redistribution requirements before testing. Report any publication concerns to the user. If a change beyond version metadata is needed, agree on it with the user and test a new candidate on hardware.
2. Keep the original IMG written to the test card and record its SHA-256 with the hardware results. Check first boot, card expansion, each model's boot and remembered selection, FE controls, representative emulator and app routes, and user storage.
3. Package the original IMG using the recorded SHA-256. The script checks the input and the decompressed archive against that hash. The source IMG is read only, and the outputs are the 7z archive and `SHA256SUMS`.

```sh
bash scripts/package-jz47xx-release.sh /path/to/plumOS-JZ47xx-0.1.0.img VERIFIED_SHA256
```

The default output directory is `output/release/`. It can also be passed as the third argument. The script requires 7-Zip (`7zz` or `7z`) and a SHA-256 utility. Publish the user and developer guides and required license materials alongside the verified archive. See the [candidate validation record](../validation/jz47xx-release-candidate-2026-11-20.md) for the current results.
