# Supported systems and ROM folders

[日本語](supported-systems.ja.md) · [User guide](README.md) · [SD card layout](storage.md)

The standard frontend in plumOS JZ47xx_v2 v0.1.0 registers 26 systems and 58 launch profiles. Create the folders below at the root of SD1's `PLUMOS` volume or of the first partition on SD2. [How plumOS chooses a card](storage.md#how-plumos-selects-roms-and-bios)

- Use one recommended folder per system to avoid duplicate entries from copies of the same game under aliases. On ext4, match the capitalization of the folder names shown here.
- The extensions determine which files appear in the frontend. Extension matching is case-insensitive. Launch support depends on the emulator, BIOS and game set.
- `SA` means standalone emulator and `PICO` means a PicoArch core. Bold text marks the default in the system catalog. Use the frontend's **SELECT** menu to see any saved system or game override.

| System | Recommended folder | Other recognized folders | Extensions scanned by the frontend | Launch profiles |
| --- | --- | --- | --- | --- |
| NES | `roms/nes/` | `roms/FC/`, `roms/famicom/` | `.nes`, `.unf`, `.unif`, `.zip`, `.7z` | **`SA: fceux`**, `PICO: fceumm`, `PICO: nestopia`, `PICO: quicknes`, `SA: fceux223` |
| SFC | `roms/sfc/` | `roms/SFC/`, `roms/snes/` | `.sfc`, `.smc`, `.fig`, `.bs`, `.swc`, `.zip`, `.7z` | **`SA: pocketsnes`**, `PICO: snes9x2005`, `PICO: chimerasnes`, `PICO: snes9x2005_plus` |
| GB | `roms/gb/` | `roms/GB/` | `.gb`, `.zip`, `.7z` | **`SA: gambatte`**, `PICO: gambatte`, `PICO: gearboy`, `PICO: vbam`, `SA: gambatte2020`, `SA: ohboy` |
| GBC | `roms/gbc/` | `roms/GBC/`, `roms/GB/` | `.gbc`, `.zip`, `.7z` | **`SA: gambatte`**, `PICO: gambatte`, `PICO: gearboy`, `PICO: vbam`, `SA: gambatte2020`, `SA: ohboy` |
| GBA | `roms/gba/` | `roms/GBA/` | `.gba`, `.zip`, `.7z` | **`SA: regba`**, `PICO: gpsp` |
| Mega Drive | `roms/megadrive/` | `roms/MD/`, `roms/genesis/` | `.gen`, `.md`, `.smd`, `.bin`, `.zip`, `.7z` | **`SA: picodrive`**, `PICO: picodrive`, `SA: genesisgx` |
| Master System | `roms/mastersystem/` | `roms/MS/`, `roms/MD/` | `.sms`, `.bin`, `.zip`, `.7z` | **`SA: picodrive`**, `PICO: genesis_plus_gx`, `PICO: picodrive`, `PICO: gearsystem`, `SA: smsplusms` |
| Game Gear | `roms/gamegear/` | `roms/GG/`, `roms/GameGear/`, `roms/MD/` | `.gg`, `.zip`, `.7z` | **`SA: picodrive`**, `PICO: genesis_plus_gx`, `PICO: picodrive`, `PICO: gearsystem`, `SA: smsplusgg` |
| Sega CD | `roms/segacd/` | `roms/SEGACD/`, `roms/megacd/` | `.cue`, `.chd`, `.iso`, `.m3u`, `.bin` | **`PICO: picodrive`** |
| PC Engine | `roms/pcengine/` | `roms/PCE/`, `roms/tg16/` | `.pce`, `.sgx`, `.zip`, `.7z` | **`PICO: mednafen_pce_fast`**, `PICO: mednafen_supergrafx`, `SA: temper` |
| SuperGrafx | `roms/supergrafx/` | `roms/SGX/`, `roms/PCE/` | `.sgx`, `.pce`, `.zip`, `.7z` | **`PICO: mednafen_supergrafx`** |
| PC Engine CD | `roms/pcenginecd/` | `roms/PCECD/`, `roms/tg16cd/` | `.cue`, `.chd`, `.iso`, `.m3u` | **`PICO: mednafen_pce_fast`** |
| PlayStation | `roms/psx/` | `roms/PS/` | `.cue`, `.chd`, `.iso`, `.pbp`, `.m3u` | **`SA: pcsx4all`** |
| NGPC | `roms/ngpc/` | `roms/NGPC/`, `roms/NGP/` | `.ngc`, `.ngpc`, `.zip`, `.7z` | **`SA: race`** |
| WonderSwan | `roms/wonderswan/` | `roms/WS/`, `roms/WSC/` | `.ws`, `.zip`, `.7z` | **`PICO: mednafen_wswan`**, `SA: oswan` |
| MSX | `roms/msx/` | `roms/MSX/`, `roms/msx2/` | `.rom`, `.mx1`, `.mx2`, `.dsk`, `.cas`, `.zip`, `.7z` | **`PICO: fmsx`**, `PICO: bluemsx` |
| Atari 800 | `roms/atari800/` | `roms/ATARI800/`, `roms/ATARI/800/` | `.car`, `.atr`, `.xex`, `.rom`, `.xfd`, `.bin` | **`SA: atari800`** |
| Atari 2600 | `roms/atari2600/` | `roms/ATARI2600/` | `.a26`, `.bin`, `.rom` | **`SA: stella`** |
| Pokemon Mini | `roms/pokemini/` | `roms/POKEMINI/` | `.min` | **`SA: pokemini`** |
| Atari Lynx | `roms/lynx/` | `roms/LYNX/` | `.lnx`, `.lyx` | **`SA: handy`** |
| Amstrad CPC | `roms/cpc/` | `roms/CPC/`, `roms/amstradcpc/` | `.dsk`, `.sna`, `.bin`, `.cpr` | **`SA: crocods`** |
| ZX Spectrum | `roms/zxspectrum/` | `roms/ZXSPECTRUM/`, `roms/ZX/` | `.tap`, `.tzx`, `.sna`, `.z80`, `.trd`, `.scl` | **`SA: unrealspeccy`** |
| Neo Geo | `roms/neogeo/` | `roms/NEOGEO/` | `.zip` | **`SA: gngeo`** |
| Neo Geo CD | `roms/neogeocd/` | `roms/NEOGEOCD/` | `.m3u`, `.cue`, `.iso` | **`SA: neo4all`** |
| Amiga | `roms/amiga/` | `roms/AMIGA/` | `.adf`, `.adz` | **`SA: uae4all`** |
| Arcade | `roms/arcade/` | `roms/ARCADE/`, `roms/fbneo/`, `roms/FBNEO/` | `.zip` | **`SA: fba44`** |

## Disc images and artwork

- Keep the disc or track files referenced by a `.cue` or `.m3u` together, with the same names and relative paths. A PlayStation `.cue` needs its associated `.bin` or `.img` files. The PlayStation and Neo Geo CD launchers skip blank lines and comments in an `.m3u` and start its first entry.
- Put artwork on the same card as the ROM, in `Images/<system-id>/`. For example, `roms/FC/My Game.nes` uses the system ID `nes`, so its artwork goes in `Images/nes/My Game.png`. The system ID is the last component of the recommended folder.
