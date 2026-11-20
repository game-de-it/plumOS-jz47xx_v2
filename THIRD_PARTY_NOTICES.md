# Third-party notices for plumOS JZ47xx_v2 v0.1.0

[日本語](THIRD_PARTY_NOTICES.ja.md)

plumOS and its original frontend code use the [MIT License](LICENSE). Bundled third-party programs, libraries, fonts and artwork retain their own copyright notices and terms. The following inventory covers the four-model v0.1.0 SD image reviewed for release. Its source-review bundle records the image digest, the shipped binary digests, source provenance and remaining gaps.

[Emulator licenses and pinned upstream revisions](docs/developer/emulator-licenses.md)

| Component | Notices and source in the review bundle |
| --- | --- |
| Linux, UBIBoot and OpenDingux/Buildroot | `platform/target-components.csv` lists component versions and declared licenses. See `platform/licenses/`, `platform/archives/`, the Buildroot snapshot, Linux configs and modified files in `platform/kernel-overlay/`, and the project's UBIBoot patch and build scripts. |
| System and compatibility libraries | See the base package manifest and `platform/compatibility-components.tsv`. Legacy ncurses, GNU Readline, OpenSSL and libpng source archives are under `runtime-sources/legacy-libraries/`. The OpenSSL 1.0.x notice and acknowledgment requirements are in its original `LICENSE`. |
| PicoArch and Libretro cores | `runtime-sources/PicoArch/` retains the PicoArch license and third-party libpicofe files. Each `runtime-sources/libretro-*/` directory retains its own notices and records its source revision. The individual cores have separate license terms. |
| PCSX4ALL and source-built standalone emulators | `runtime-provenance.json` links the shipped executables to the retained source directories. Preserve the license and source headers in each directory. |
| Calculator, Commander, Bard, FFPlay, GMU, SDL Terminal and PDF Viewer | `runtime-sources/provided-app-archives/` holds the available app source and notices. The release must also account for any libraries shipped inside each package. FFPlay and its FFmpeg libraries require review against the shipped build configuration. [FFmpeg license and compliance](https://ffmpeg.org/legal.html) |
| Noto Sans JP, WenQuanYi Micro Hei and other assets | `as-shipped-notices/` preserves the font notices from the image. Noto Sans JP carries OFL 1.1. WenQuanYi Micro Hei is dual-licensed under Apache 2.0 or GPLv3 with the font embedding exception. The image includes its Apache notice. Availability of a software source archive does not establish rights for frontend logos, artwork or graphics imported from prebuilt OPKs. [WenQuanYi upstream readme](https://sources.debian.org/src/fonts-wqy-microhei/0.2.0-beta-3.1/README.txt) |

The [release rights audit](docs/validation/jz47xx-v0.1.0-release-rights.md) records the follow-up source and artwork matches. It includes the provenance of all 34 shared objects inside the OPKs.

## Components with additional restrictions

- **fMSX** has a custom non-commercial license. The release candidate retains the unmodified Libretro port with its original attribution. The audit records the remaining questions about the upstream distribution terms. Refer to the shipped version's `runtime-sources/libretro-fmsx/LICENSE`. [fMSX documentation](https://docs.libretro.com/library/fmsx/)
- **PicoDrive** contains non-commercial material. Its `COPYING` requires notices and source for modified redistributions. This applies to the standalone and Libretro builds in this image. [PicoDrive upstream license](https://github.com/irixxxx/picodrive/blob/master/COPYING)
- **Snes9x 2005, Snes9x 2005 Plus and ChimeraSNES** contain Snes9x code with non-commercial conditions. See the respective `copyright` or `LICENSES` files for the per-file terms and the conditions on binary redistribution. [Snes9x 2005 copyright](https://github.com/libretro/snes9x2005/blob/master/copyright)
- **FBA44** is non-commercial and remains in the release candidate. Its license requires the full verbatim license and publication of changes. The retained `runtime-sources/FBA44/src/license.txt` also sets limits on profit, donations, recent game support, ROM distribution and use of dynamic libraries. Review it together with the MAME-derived and other incorporated code notices before release.
- **blueMSX** includes code under multiple terms. Preserve the per-file declarations and inspect the applicable terms alongside the retained `runtime-sources/libretro-bluemsx/license.txt`.

## Checks required before publication

1. Resolve exact source or validate source-built replacements for PocketSNES 2019, FCEUX 2.2.3 and RACE. The follow-up archive includes the matched PokeMini GCW0 source and its minizip dependency. The FCEUX 2.6.6 GCW0 and Gambatte-DMS 2020/2021 executables match official release assets, and the corresponding release tag sources are included. [FCEUX release](https://github.com/plrguez/fceux-for-retrogame/releases/tag/2023-08-30) [Gambatte-DMS releases](https://github.com/bardeci/gambatte-dms/releases) Upstream project links do not establish correspondence with those executables.
2. Resolve the items that are still pending, including the links between retained package builds and working source trees. The follow-up inventory identifies the 34 shared objects inside the OPKs. Where a license requires corresponding source, provide the exact modified source and the scripts and build inputs needed to build and install it. Keep the original license texts and fulfill any additional library obligations, including applicable relinking requirements.
3. Confirm redistribution terms for the restricted components and third-party artwork. Preserve required notices in the rebuilt SD image and alongside its download. Publish the source for the exact build and SHA-256 files alongside the image after verification.

The review bundle records the available evidence. It is incomplete as a corresponding-source distribution for the current image.
