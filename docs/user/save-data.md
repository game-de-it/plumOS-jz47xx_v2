# Saves and save states

[日本語](save-data.ja.md) · [User guide](README.md) · [SD card layout](storage.md)

Emulators launched from the standard frontend normally keep saves and states in **p2 `PLUMOSDATA` on SD1**. The paths below still point to SD1 when you launch a game from SD2. They are shown as they appear on the handheld. If you connect SD1 to a Linux computer and mount p2, start from the `plumos/` directory in that partition.

## PicoArch

| Data | Path |
| --- | --- |
| In-game save (save RAM) | `/media/data/plumos/Saves/<system-id>/<game-name>.sav` |
| Save state | `/media/data/plumos/home/picoarch/<system-id>/.picoarch-<core-name>-<system-id>/<game-name>.st0`, where the last digit is the slot number. |

For example, with PicoArch Gambatte on GB, save RAM goes in `Saves/gb/` and states go in `home/picoarch/gb/.picoarch-gambatte-gb/`. [System IDs and core names](supported-systems.md)

## Standalone emulators

FCEUX, Gambatte, PocketSNES, ReGBA, PicoDrive and PCSX4ALL use `/media/data/plumos/home/`. Standalone OPK profiles with a dedicated home directory use `/media/data/plumos/home/opk/<emulator-id>/`. For example, FCEUX 2.2.3 uses the ID `fceux223`. Check the frontend's **SELECT** menu for the profile used by the game.

| Launch profile | Common save paths relative to `/media/data/plumos/` |
| --- | --- |
| PCSX4ALL | Memory cards in `home/.pcsx4all/memcards/` and states in `home/.pcsx4all/sstates/`. |
| FCEUX | In `home/.fceux/`, with in-game saves under `sav/` and states under `fcs/`. |
| FCEUX 2.2.3 | In `home/opk/fceux223/.fceux/`, with in-game saves under `sav/` and states under `fcs/`. |
| Gambatte | `home/.gambatte/saves/`. Gambatte 2020 uses `home/opk/gambatte2020/.gambatte/saves/`. |
| PocketSNES | `home/.pocketsnes/`. |
| ReGBA | `home/.gpsp/`. |
| PicoDrive | `home/.picodrive/`, including `srm/` for SRAM. |
| PokeMini | `home/opk/pokemini/saves/`, with `.eep` files for EEPROM and `.sta` files for states. |
| Other standalone OPKs | Under `home/opk/<emulator-id>/`. The subfolders and formats depend on the emulator. |

## Back up and restore

1. Choose **Exit** or **Quit** in the emulator, then **Shutdown** in the frontend's power menu.
2. Read the entire SD1 card to a disk image to back up saves, states and settings together. To copy individual saves, open SD1's ext4 `PLUMOSDATA` partition under Linux and copy the files from the folders above.
3. When restoring individual files, keep the names and directory layout and use the same system and launch profile. For save states, use the same version of the emulator or core.

Back up SD2 separately if it holds your games or artwork.
