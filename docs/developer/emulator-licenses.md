# v0.1.0 emulator licenses and source

[日本語](emulator-licenses.ja.md) · [Third-party notices](../../THIRD_PARTY_NOTICES.md)

This inventory covers the 18 standalone emulators and 17 Libretro cores in the four-model SD image. Revision links identify full commit IDs. License links point to the original text. GPLv2 and GPLv3 identify license versions. File-specific exceptions and “or later” grants follow the original notices.

- **A** is `plumOS-JZ47xx-v0.1.0-source-review.tar.gz`. It contains available source snapshots with the plumOS modifications, Linux and Buildroot sources, and the original audit evidence.
- **B** is `plumOS-JZ47xx-v0.1.0-source-followup.tar.gz`. It contains the PokeMini and minizip sources, the FCEUX 2.2.3 candidate source and build instructions, and OPK library provenance.
- Both archives are being prepared for release. Upstream links identify the original trees. The archives also contain the retained plumOS build inputs. Candidate and reference rows indicate unconfirmed source correspondence for the shipped binary.

**fMSX and FBA44 are non-commercial and stay in the v0.1.0 release candidate.** Attribution is retained for fMSX. FBA44 includes the verbatim license text and its modified source is staged for release. See the [redistribution audit](../validation/jz47xx-v0.1.0-release-rights.md) for open conditions.

## Standalone emulators

| Emulator | Original license | Upstream revision | Corresponding source and evidence |
| --- | --- | --- | --- |
| FBA44 | [Non-commercial (FB Alpha); additional conditions](https://github.com/plrguez/fba-sdl/blob/9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8/src/license.txt) | [`9448a9c6f104`](https://github.com/plrguez/fba-sdl/tree/9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8) | Build matched<br>A `runtime-sources/FBA44` |
| FCEUX 2.2.3-interim | [GPLv2 in candidate source](https://github.com/soarqin/fceux-for-retrogame/blob/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03/COPYING) | [`bf89b7fd8b87`](https://github.com/soarqin/fceux-for-retrogame/tree/bf89b7fd8b879cae6390bb1bbf41e71a88d53b03) | Legacy correspondence unconfirmed<br>Rebuilt replacement verified on RG350M. See the [replacement source and test record](../validation/jz47xx-v0.1.0-release-rights.md#fceux-223-interim-replacement-candidate). |
| FCEUX 2.6.6 GCW0 | [GPLv2](https://github.com/plrguez/fceux-for-retrogame/blob/fbeaad2ddcdae3563c1093b08668f8b8f4bd4e2e/COPYING) | [`fbeaad2ddcda`](https://github.com/plrguez/fceux-for-retrogame/tree/fbeaad2ddcdae3563c1093b08668f8b8f4bd4e2e) | Upstream release matched<br>A `runtime-sources/fceux-2.6.6` |
| Gambatte-DMS 2020 | [GPLv2](https://github.com/bardeci/gambatte-dms/blob/f78a4c3131bb02cd1001a1f4502ce514607388f5/COPYING) | [`f78a4c3131bb`](https://github.com/bardeci/gambatte-dms/tree/f78a4c3131bb02cd1001a1f4502ce514607388f5) | Upstream release matched<br>A `runtime-sources/gambatte-dms-2020` |
| Gambatte-DMS 2021 | [GPLv2](https://github.com/bardeci/gambatte-dms/blob/b333155c05d32bd0960c51dd5026942493093d81/COPYING) | [`b333155c05d3`](https://github.com/bardeci/gambatte-dms/tree/b333155c05d32bd0960c51dd5026942493093d81) | Upstream release matched<br>A `runtime-sources/gambatte-dms-2021` |
| Handy | [GPLv2](https://github.com/gameblabla/handy-rs97/blob/6fc52aebdb65865144ed01b7478bcbf7b3a2edaa/LICENSE%20) | [`6fc52aebdb65`](https://github.com/gameblabla/handy-rs97/tree/6fc52aebdb65865144ed01b7478bcbf7b3a2edaa) | Package matched; source link pending<br>A `runtime-sources/Handy` |
| OhBoy | [GPLv2](https://github.com/hi-ban/ohboy/blob/4720bcf5fbb4d80d85d6f623847d29cefea2cd94/COPYING) | [`4720bcf5fbb4`](https://github.com/hi-ban/ohboy/tree/4720bcf5fbb4d80d85d6f623847d29cefea2cd94) | Build matched<br>A `runtime-sources/OhBoy` |
| Oswan | [GPLv2](https://github.com/gameblabla/oswan/blob/efea1326dc4f0477a6a7b704f7f7f6f5a1cc6f33/COPYING) | [`efea1326dc4f`](https://github.com/gameblabla/oswan/tree/efea1326dc4f0477a6a7b704f7f7f6f5a1cc6f33) | Package matched; source link pending<br>A `runtime-sources/Oswan` |
| PCSX4ALL | [GPLv2 or later in core source headers](https://github.com/jdgleaver/RG350_pcsx4all/blob/ab17108051d2178465da58ce377225575d680e5e/src/cdrom.h) | [`ab17108051d2`](https://github.com/jdgleaver/RG350_pcsx4all/tree/ab17108051d2178465da58ce377225575d680e5e) | Build output matched<br>A `runtime-sources/PCSX4ALL` |
| PicoDrive | [Non-commercial (PicoDrive)](https://github.com/irixxxx/picodrive/blob/9f46ee4e9680d108e548fb427e7c7e1aa1bb9d5a/COPYING) | [`9f46ee4e9680`](https://github.com/irixxxx/picodrive/tree/9f46ee4e9680d108e548fb427e7c7e1aa1bb9d5a) | Build matched<br>A `runtime-sources/PicoDrive` |
| PokeMini GCW0 | [GPLv3 or later](https://github.com/gameblabla/pokemini/blob/37e3324ebf481a5f6ece725ae5c052332e3b84d1/LICENSE) | [`37e3324ebf48`](https://github.com/gameblabla/pokemini/tree/37e3324ebf481a5f6ece725ae5c052332e3b84d1) | Upstream executable matched; see both PokeMini archives<br>B `sources/PokeMini-GCW0-37e3324-source.tar.gz` + `sources/PokeMini-0.60-minizip-source.tar.gz` |
| PocketSNES 2019-12-12 | [Snes9x non-commercial terms for replacement](https://github.com/soarqin/PocketSNES/blob/1a627d83288721fba1eb14d08eefa22860a05e0e/dist/PocketSNES.man.txt) | [`1a627d832887` replacement](https://github.com/soarqin/PocketSNES/tree/1a627d83288721fba1eb14d08eefa22860a05e0e) | Legacy correspondence unconfirmed<br>[Replacement source and test record](../validation/jz47xx-v0.1.0-release-rights.md#pocketsnes-replacement-candidate) |
| RACE GCW-ZERO V1.2 | [GPLv2 text for replacement](https://github.com/retrofw/race-od/blob/7fe3dacba61a14da76d1cc1c6b7fb12b6f912870/License.txt) | [`7fe3dacba61a`](https://github.com/retrofw/race-od/tree/7fe3dacba61a14da76d1cc1c6b7fb12b6f912870) | Legacy correspondence unconfirmed<br>[Replacement source and trial](../validation/jz47xx-v0.1.0-release-rights.md#race-replacement-candidate) |
| SMS Plus GG | [GPLv2](https://github.com/gameblabla/sms_sdl/blob/5554715689a41f58715f11cecfb885b7f5c29b51/docs/license) | [`5554715689a4`](https://github.com/gameblabla/sms_sdl/tree/5554715689a41f58715f11cecfb885b7f5c29b51) | Package matched; source link pending<br>A `runtime-sources/SMS-Plus` |
| SMS Plus MS | [GPLv2](https://github.com/gameblabla/sms_sdl/blob/5554715689a41f58715f11cecfb885b7f5c29b51/docs/license) | [`5554715689a4`](https://github.com/gameblabla/sms_sdl/tree/5554715689a41f58715f11cecfb885b7f5c29b51) | Package matched; source link pending<br>A `runtime-sources/SMS-Plus` |
| Stella | [GPLv2](https://github.com/DavidKnight247/Stella-3.9.3/blob/4c309195f666909e7c0a185bcc46da836fc234dd/LICENSE) | [`4c309195f666`](https://github.com/DavidKnight247/Stella-3.9.3/tree/4c309195f666909e7c0a185bcc46da836fc234dd) | Package matched; source link pending<br>A `runtime-sources/Stella` |
| Temper (earlier candidate only) | [Whole-program redistribution terms unconfirmed](https://github.com/gameblabla/temper/blob/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae/win32/readme.txt) | [`a6c9ef2c5d1a`](https://github.com/gameblabla/temper/tree/a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae) | Retained build matched. Source held for audit.<br>[Redistribution evidence and scope](../validation/jz47xx-v0.1.0-release-rights.md#temper-redistribution) |
| UAE4All | [GPLv2](https://github.com/goldmojo/uae4all/blob/9988f9924a5da4d21fde414b8d531301f8b1076c/docs/COPYING) | [`9988f9924a5d`](https://github.com/goldmojo/uae4all/tree/9988f9924a5da4d21fde414b8d531301f8b1076c) | Package matched; source link pending<br>A `runtime-sources/UAE4All` |

## Libretro cores

| Emulator | Original license | Upstream revision | Corresponding source and evidence |
| --- | --- | --- | --- |
| blueMSX (`bluemsx`) | [BSD-style / GPL / freeware](https://github.com/libretro/blueMSX-libretro/blob/acf358be18644a9df0ed9602d63c2f73d4fe605a/license.txt) | [`acf358be1864`](https://github.com/libretro/blueMSX-libretro/tree/acf358be18644a9df0ed9602d63c2f73d4fe605a) | Build matched<br>A `runtime-sources/libretro-bluemsx` |
| ChimeraSNES (`chimerasnes`) | [Non-commercial (Snes9x); mixed terms](https://github.com/jamsilva/chimerasnes/blob/0542329f32ab524ce8606c2c859bcd49905a3c98/LICENSES) | [`0542329f32ab`](https://github.com/jamsilva/chimerasnes/tree/0542329f32ab524ce8606c2c859bcd49905a3c98) | Build matched<br>A `runtime-sources/libretro-chimerasnes` |
| FCEUmm (`fceumm`) | [GPLv2](https://github.com/libretro/libretro-fceumm/blob/3f23e2b98f883be9c62a3fdb65c015d376dcd135/Copying) | [`3f23e2b98f88`](https://github.com/libretro/libretro-fceumm/tree/3f23e2b98f883be9c62a3fdb65c015d376dcd135) | Build matched<br>A `runtime-sources/libretro-fceumm` |
| fMSX (`fmsx`) | [Non-commercial (fMSX)](https://github.com/libretro/fmsx-libretro/blob/4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4/LICENSE) | Retained build matched and includes Nuked-OPLL. [Redistribution audit](../validation/jz47xx-v0.1.0-release-rights.md#fmsx-redistribution-and-fm-audio) |
| Gambatte (`gambatte`) | [GPLv2](https://github.com/libretro/gambatte-libretro/blob/90701d6e5d68d31ead49f92f222c144c44a2645c/COPYING) | [`90701d6e5d68`](https://github.com/libretro/gambatte-libretro/tree/90701d6e5d68d31ead49f92f222c144c44a2645c) | Build matched<br>A `runtime-sources/libretro-gambatte` |
| Gearboy (`gearboy`) | [GPLv3](https://github.com/drhelius/Gearboy/blob/8762faf754a84891078d4b2597c557a828631c9e/LICENSE) | [`8762faf754a8`](https://github.com/drhelius/Gearboy/tree/8762faf754a84891078d4b2597c557a828631c9e) | Build matched<br>A `runtime-sources/libretro-gearboy` |
| Gearsystem (`gearsystem`) | [GPLv3](https://github.com/drhelius/Gearsystem/blob/5d6fedacb3ef2a9481fa52aac67fefb47aaf72c0/LICENSE) | [`5d6fedacb3ef`](https://github.com/drhelius/Gearsystem/tree/5d6fedacb3ef2a9481fa52aac67fefb47aaf72c0) | Build matched<br>A `runtime-sources/libretro-gearsystem` |
| Beetle NGP (`mednafen_ngp`) | [GPLv2](https://github.com/libretro/beetle-ngp-libretro/blob/00c7cb8ea97ad9a372307405d8abf34e401fec8a/COPYING) | [`00c7cb8ea97a`](https://github.com/libretro/beetle-ngp-libretro/tree/00c7cb8ea97ad9a372307405d8abf34e401fec8a) | Build matched<br>A `runtime-sources/libretro-mednafen_ngp` |
| Beetle PCE Fast (`mednafen_pce_fast`) | [GPLv2](https://github.com/libretro/beetle-pce-fast-libretro/blob/2de1ce1c3f237b161c126c54ba407990bb86d1e9/COPYING) | [`2de1ce1c3f23`](https://github.com/libretro/beetle-pce-fast-libretro/tree/2de1ce1c3f237b161c126c54ba407990bb86d1e9) | Build matched<br>A `runtime-sources/libretro-mednafen_pce_fast` |
| Beetle SuperGrafx (`mednafen_supergrafx`) | [GPLv2](https://github.com/libretro/beetle-supergrafx-libretro/blob/3cfafe8c684a2f4f4532bcf18e25d2f8760ca45d/COPYING) | [`3cfafe8c684a`](https://github.com/libretro/beetle-supergrafx-libretro/tree/3cfafe8c684a2f4f4532bcf18e25d2f8760ca45d) | Build matched<br>A `runtime-sources/libretro-mednafen_supergrafx` |
| Beetle WonderSwan (`mednafen_wswan`) | [GPLv2](https://github.com/libretro/beetle-wswan-libretro/blob/16d96f64a32cbe1fa89c40b142298dbd007f2f4d/COPYING) | [`16d96f64a32c`](https://github.com/libretro/beetle-wswan-libretro/tree/16d96f64a32cbe1fa89c40b142298dbd007f2f4d) | Build matched<br>A `runtime-sources/libretro-mednafen_wswan` |
| Nestopia (`nestopia`) | [GPLv2](https://github.com/libretro/nestopia/blob/a9ee6ca84f04990e209880fe47144e62b14253db/COPYING) | [`a9ee6ca84f04`](https://github.com/libretro/nestopia/tree/a9ee6ca84f04990e209880fe47144e62b14253db) | Build matched<br>A `runtime-sources/libretro-nestopia` |
| PicoDrive (`picodrive`) | [Non-commercial (PicoDrive)](https://github.com/libretro/picodrive/blob/13ceea4ceb5f1b3a7d56baf67ec55247c1dfd154/COPYING) | [`13ceea4ceb5f`](https://github.com/libretro/picodrive/tree/13ceea4ceb5f1b3a7d56baf67ec55247c1dfd154) | Build matched<br>A `runtime-sources/libretro-picodrive` |
| QuickNES (`quicknes`) | [GPLv2](https://github.com/libretro/QuickNES_Core/blob/26bb785c9deddb66a17717b21bb4e328f03ade32/LICENSE) | [`26bb785c9ded`](https://github.com/libretro/QuickNES_Core/tree/26bb785c9deddb66a17717b21bb4e328f03ade32) | Build matched<br>A `runtime-sources/libretro-quicknes` |
| Snes9x 2005 (`snes9x2005`) | [Non-commercial (Snes9x); mixed terms](https://github.com/libretro/snes9x2005/blob/fd45b0e055bce6cff3acde77414558784e93e7d0/copyright) | [`fd45b0e055bc`](https://github.com/libretro/snes9x2005/tree/fd45b0e055bce6cff3acde77414558784e93e7d0) | Build matched<br>A `runtime-sources/libretro-snes9x2005` |
| Snes9x 2005 Plus (`snes9x2005_plus`) | [Non-commercial (Snes9x); mixed terms](https://github.com/libretro/snes9x2005/blob/fd45b0e055bce6cff3acde77414558784e93e7d0/copyright) | [`fd45b0e055bc`](https://github.com/libretro/snes9x2005/tree/fd45b0e055bce6cff3acde77414558784e93e7d0) | Build matched<br>A `runtime-sources/libretro-snes9x2005_plus` |
| VBA-M (`vbam`) | [GPLv2 or later; exceptions by file](https://github.com/libretro/vbam-libretro/blob/254f6effebe882b7d3d29d9e417c6aeeabc08026/doc/License.txt) | [`254f6effebe8`](https://github.com/libretro/vbam-libretro/tree/254f6effebe882b7d3d29d9e417c6aeeabc08026) | Build matched<br>A `runtime-sources/libretro-vbam` |

## Core frontend

PicoArch uses BSD-3-Clause for its original code and retains separate terms for libpicofe and other incorporated components. Each core has its own license listed above. [Original notice](https://github.com/shauninman/picoarch/blob/802047c276a5a931b0bf837c4ea4b8e238bdeabe/LICENSE) · [Pinned source](https://github.com/shauninman/picoarch/tree/802047c276a5a931b0bf837c4ea4b8e238bdeabe) · A `runtime-sources/PicoArch`.

## Source supplement for the cleanup candidate

The following entries apply to the four-device [cleanup test image](../validation/jz47xx-release-candidate-2026-11-20.md#v010-cleanup-test-image). The source supplement is `plumOS-JZ47xx-v0.1.0-cleanup-source.tar.gz`. It contains the listed sources, the retained build changes, and the FBA44 and PokeMini license texts.

| Component | Revision and original terms | Evidence |
| --- | --- | --- |
| Atari800 4.1.0 | [`d9d9ad1`, GPL](https://github.com/atari800/atari800/blob/d9d9ad1b47169d30b41e90b709dfc437844c9b9c/COPYING). [Altirra firmware by Avery Lee](https://github.com/atari800/atari800/blob/d9d9ad1b47169d30b41e90b709dfc437844c9b9c/src/roms/altirraos_xl.c), permissive with notice retention. | The ELF matches the saved build. Four Altirra firmware arrays match the source byte for byte. |
| Unreal Speccy Portable | [`11b0980`, GPLv3 or later](https://github.com/DavidKnight247/Unreal-Speccy-Emulator-GCW0-Edition/blob/11b0980470e7c52cf77095f327085f31957d4818/LICENSE) | The ELF matches the saved build after stripping. System ROMs are supplied separately by the user. |
| ReGBA 1.9.2 | [`4396f9e`, GPLv2 text](https://github.com/jdgleaver/ReGBA/blob/4396f9eca3320b7e2955e2815cfe6332542b91be/doc/gpl-2.0_en.txt) | Upstream release and source tag. The plumOS SDL shim is included in the supplement. |
| Cult of GBA BIOS | DenSinH and fleroviux. [`6cc6bf9`, MIT](https://github.com/Cult-of-GBA/BIOS/blob/6cc6bf9ebab9197baa87d128a8f71062e484f166/LICENSE) | BIOS and license match the pinned upstream files. |
| C-BIOS | BouKiCHi, Reikan, Maarten ter Huurne, Albert Beevendorp, Manuel Bilderbeek, Joost Yervante Damad, Jussi Pitkänen and Eric Boon are credited in the main ROM source. [0.23, BSD 2-Clause](https://sourceforge.net/projects/cbios/files/cbios/0.23/) | Three runtime ROMs and all nine ROM entries in the blueMSX source archive match the original package. Preserve the notices in the individual source files. |

CrocoDS 2020-01-15 was in the cleanup test image. The OpenDingux OPK carries a GPLv2 text. Its embedded CPC 6128 ROM and AMSDOS variant match the copies in the separate [CrocoDS core tree](https://github.com/redbug26/crocods-core/tree/6091e690a000165fba69065f1f07c6ff3d452d20). See the [redistribution audit](../validation/jz47xx-v0.1.0-release-rights.md#crocods-firmware-and-source) for firmware fingerprints, rights-holder statements and the remaining corresponding-source gap.

## Executables replaced in the current candidate

The tables above also record earlier builds. The artifacts below were prepared for the replacements in the candidate that passed the four-model boot check. [Current candidate SHA-256 and validation results](../validation/jz47xx-v0.1.0-update-validation.md)

- CrocoDS — `plumOS-CrocoDS-external-bios-drm-source.tar.gz`
- RACE — `plumOS-RACE-7fe3dac-source.tar.gz`
- FCEUX 2.2.3 — `plumOS-FCEUX-2.2.3-bf89b7fd-source.tar.gz`
- PocketSNES — `plumOS-PocketSNES-1a627d8-source.tar.gz`
- FBA44 — `plumOS-FBA44-v0.1.0-static-source.tar.gz`, `plumOS-FBA44-v0.1.0-static-relink.tar.gz`

## Alternative frontend source

| Frontend | Source revision and code license |
| --- | --- |
| SimpleMenu | [`e70a861`, GPLv3](https://github.com/fgl82/simplemenu/tree/e70a861b1f05fd83cd1b19be53be11c0a0ecd510#code-license). The main project lists artwork under CC BY-NC-SA 3.0. The stock 0A theme declares CC BY-NC-SA 4.0 for its own artwork. See the [theme credits](../../THIRD_PARTY_NOTICES.md#artwork-and-font-credits). |
| 350teric (Esoteric) | [`6e0a1ca`, GPLv2 text](https://github.com/podulator/esoteric/blob/6e0a1ca1aa523ec5dff042c4a220582edc1767e9/COPYING) |
| EmulationStation | [`3ab83b1`, MIT](https://github.com/lualiliu/emulationstation-on-jz4770/blob/3ab83b15b7bf033bd1a02c9e307b4fc4219107b7/LICENSE.md). The [simplegcw theme](https://github.com/ManuelSch81/RG350-EmulationStation_configured/tree/3c8f0473e539ae7a36e8dd5e39180dcdc33cf0f8) has separate artwork. |
| PyMenu | [`68ceb9d`, GPLv3 text](https://github.com/JackD83/PyMenu/blob/68ceb9d17c4016d68abd6cd7c382eea5cbfd2009/LICENSE) |
