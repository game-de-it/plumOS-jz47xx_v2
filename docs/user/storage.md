# SD cards and folders

[日本語](storage.ja.md) · [User guide](README.md) · [Save data](save-data.md)

SD1 boots plumOS and holds its settings. You can play games from SD1 alone. An optional SD2 can hold games, BIOS files and artwork. [Card slots by model](README.md#sd-card-slots)

## SD1 partitions

| Partition | Volume | Format and size | Contents |
| --- | --- | --- | --- |
| p1 | `PLUMOSBOOT` | FAT32, 128 MiB | Boot files and the remembered model. Mounted at `/boot` on the handheld. |
| p2 | `PLUMOSDATA` | ext4, 1.5 GiB | Frontend, emulators, apps, settings and saves. Mounted at `/media/data`. |
| p3 | `PLUMOS` | FAT32, remainder of the card | User content such as games, BIOS files and artwork. Mounted at `/media/user`. |

On first boot, plumOS expands the 64 MiB seed partition p3 to the end of the card and creates the FAT32 `PLUMOS` volume. The completed setup carries over when you move the same card to another supported model.

On macOS or Windows, open `PLUMOS` to add games and other files. Dismiss any prompt to format an unfamiliar partition.

## Using SD2

SD2 is an optional data card. Make the first partition FAT32 if you want to copy files from macOS or Windows. plumOS supports FAT32 and ext4 and mounts the first partition read-only at `/media/data/sd2`. Shut down the handheld and use a card reader to add or organize files on SD2.

## How plumOS selects ROMs and BIOS

At startup, plumOS chooses the source of `roms/` and `bios/` independently. For each folder it uses SD2 if the folder exists at its root, including when the folder is empty. Otherwise it uses SD1's `PLUMOS` volume. Artwork is read from the card selected for ROMs.

| Folders at the root of SD2 | Games and artwork | BIOS folder |
| --- | --- | --- |
| Both `roms/` and `bios/` | SD2 | SD2 |
| Only `roms/` | SD2 | SD1 |
| Only `bios/` | SD1 | SD2 |
| Neither folder, or no SD2 inserted | SD1 | SD1 |

## BIOS files for specific emulators

Place these files under the `bios/` folder selected above. Use firmware you have permission to use.

| Emulator | Files and location |
| --- | --- |
| PCSX4ALL | `bios/scph1001.bin`, or the BIOS filename selected in the emulator. |
| fMSX | MSX system ROMs at the root of `bios/`, using the filenames expected by fMSX, such as `MSX.ROM`, `MSX2.ROM` and `MSX2EXT.ROM`. |
| blueMSX | Put the complete `Machines/` and `Databases/` directories under `bios/` for the original MSX hardware profiles. The bundled C-BIOS fallback supports cartridge games. |
| Atari800 | Uses the built-in Altirra firmware by default. Optional original ROMs use `bios/opk/atari800/` with the names `5200.rom`, `ataribas.rom`, `atariosb.rom` and `atarixl.rom`. |
| Unreal Speccy | `bios/opk/unrealspeccy/` must contain `sos128_0.rom`, `sos128_1.rom`, `sos48.rom`, `service.rom` and `dos513f.rom`. Each file is 16 KiB. |
| UAE4All, GnGeo, NEO4ALL | `bios/opk/uae4all/kick.rom`, `bios/opk/gngeo/neogeo.zip`, and `bios/opk/neo4all/neocd.bin`, respectively. |

## User folders

| Folder | Contents |
| --- | --- |
| `roms/` | Games organized by system. [Folder list for all 26 systems](supported-systems.md) |
| `bios/` | BIOS and system files you supply. Examples include `bios/scph1001.bin` for PCSX4ALL and `bios/opk/uae4all/kick.rom` for UAE4All. |
| `Images/` | Game artwork under `Images/<system-id>/`. |
| `Screenshots/` | A folder for screenshots created during setup. Emulator-specific capture features may save elsewhere. |
| `Music/` | Music files. |
| `apps/` and `updates/` | Folders created on SD1 during first boot. See the [user guide](README.md#opk-apps) for how OPK apps are installed. |

Include SD1's `PLUMOSDATA` partition when backing up saves, states and settings. [Save paths and backups](save-data.md)
