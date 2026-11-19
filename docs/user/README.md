# plumOS JZ47xx User Guide

[日本語](README.ja.md) · [Project overview](../../README.md)

## Install on SD1

You need an RG280V, RG300X, RG350 or RG350M, a microSD card of at least 4 GB, and a card reader. Keep your original system card as a backup. Writing an image erases the destination card, including saves and settings.

1. Download `plumOS-JZ47xx-v0.1.0-sd-image.7z` and `SHA256SUMS` from the same release.
2. Verify the checksum before writing. For an individual file, use `shasum -a 256 <image-file>` on macOS, `sha256sum <image-file>` on Linux or `Get-FileHash <image-file> -Algorithm SHA256` in PowerShell. Compare the digest with the one published for that file.
3. Extract `plumOS-JZ47xx-0.1.0.img` from the 7-Zip archive. Select the IMG in a raw disk image writer. Check the destination card's name and capacity, write the image, let the writer finish verification and safely eject the card.
4. With the handheld powered off, insert the card into **SD1**, the system card slot. Hold the direction for your model while turning it on. Release the direction when the plumOS logo appears.

| Handheld | Hold at power-on |
| --- | --- |
| RG280V | Up ↑ |
| RG300X | Right → |
| RG350 | Down ↓ |
| RG350M | Left ← |

Wait for the frontend to appear. On the card's first successful boot, plumOS grows the user partition to the end of SD1 and prepares it as a FAT32 volume named `PLUMOS`. Keep the power on until the frontend appears. If your computer later prompts you to format an unfamiliar partition on SD1, dismiss the prompt and open the `PLUMOS` volume for your files.

## Move the same SD1 to another model

Shut down before removing either card. On the new handheld, hold its direction during power-on. The direction overrides the previous selection. After a successful boot, the system remembers the new model on SD1. For later starts on that same handheld, turn it on normally. Moving SD1 does not run the card's setup again.

A new card has no remembered model and can wait at a black screen until you select one. If you move a card and see a lit but black screen, shut down and retry with the correct direction held **before** pressing Power.

## Add games and artwork

Use the `PLUMOS` volume on SD1, or use a separate FAT32 card in SD2. The frontend uses SD2 as the library source when it finds a `roms` directory there. Otherwise it uses the SD1 user volume. Put games and their artwork on the same card. To edit SD2, shut down and use a card reader.

```text
roms/
  nes/
    My Game.nes
  gamegear/
    My Game.gg
Images/
  nes/
    My Game.png
  gamegear/
    My Game.png
```

Example ROM folders include `roms/snes` for Super Nintendo, `roms/gb`, `roms/gbc`, `roms/gba`, `roms/megadrive`, `roms/pcengine` and `roms/psx`. Keep all files used by a disc game's CUE or playlist together and preserve the names it references.

For artwork, use the ROM's filename without its extension as the image name. Use the same system folder under `Images`. PNG and JPEG work. On the frontend, choose **START → UI Settings → Refresh TOP** after adding games. Open a game list and press **X** to view its Gallery. Some emulators need BIOS or system files. Their required names and locations depend on the selected emulator or core.

## Controls and power

| Action | Control |
| --- | --- |
| Navigate, confirm and go back | D-pad, **A**, **B** |
| Open frontend settings | **START** |
| Open Gallery from a game list | **X** |
| Open available core options on a system | **SELECT** |
| Open the in-game emulator menu | **SELECT + START** on supported profiles |
| Open the plumOS power menu | Briefly press **Power** |
| Adjust brightness | Hold **START** and press left or right where supported |
| Adjust volume | Use the volume buttons where supported, or System Settings |

Use the emulator's **Exit** or **Quit** to return to the frontend. Use **Shutdown** in the plumOS power menu before removing a card. If you use **Sleep**, a short press of Power wakes the handheld. Game compatibility, emulator options and performance vary by title and device.

Back up important files before rewriting SD1. Emulator saves, states and settings may live in the system's managed storage on SD1. Keep a backup of the whole system card if you need to preserve those files together.
