# 対応システムとROMフォルダー

[English](supported-systems.md) · [ユーザーガイド](README.ja.md) · [SDカード構成](storage.ja.md)

plumOS JZ47xx_v2 v0.1.0の標準フロントエンドに登録されている26システムと56起動経路です。表のフォルダーをSD1の `PLUMOS` ボリューム、またはSD2の先頭パーティションの直下に作ります。[どちらのカードが使われるか](storage.ja.md#romとbiosの参照先)

- 1システムにつき推奨フォルダーを1つ使うと、別名のフォルダーに同じゲームを置いて重複表示するのを防げます。SD2をext4で使う場合は、フォルダー名の大文字・小文字を表にそろえてください。
- 拡張子はFEが一覧に載せる条件です。大文字・小文字は区別しません。実際に起動できる形式は、選んだエミュレーター、BIOS、ROMセットなどに依存します。
- `SA` は単体エミュレーター、`PICO` はPicoArchのコアです。太字はシステム定義上の既定の起動先です。システム別・ゲーム別の設定を保存している場合は、FEの **SELECT** メニューで現在の設定を確認できます。

| システム | 推奨フォルダー | ほかに認識するフォルダー | FEが認識する拡張子 | 起動経路 |
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
| PC Engine | `roms/pcengine/` | `roms/PCE/`, `roms/tg16/` | `.pce`, `.sgx`, `.zip`, `.7z` | **`PICO: mednafen_pce_fast`**, `PICO: mednafen_supergrafx` |
| SuperGrafx | `roms/supergrafx/` | `roms/SGX/`, `roms/PCE/` | `.sgx`, `.pce`, `.zip`, `.7z` | **`PICO: mednafen_supergrafx`** |
| PC Engine CD | `roms/pcenginecd/` | `roms/PCECD/`, `roms/tg16cd/` | `.cue`, `.chd`, `.iso`, `.m3u` | **`PICO: mednafen_pce_fast`** |
| PlayStation | `roms/psx/` | `roms/PS/` | `.cue`, `.chd`, `.iso`, `.pbp`, `.m3u` | **`SA: pcsx4all`** |
| NGPC | `roms/ngpc/` | `roms/NGPC/`, `roms/NGP/` | `.ngc`, `.ngpc`, `.zip`, `.7z` | **`SA: race`** |
| WonderSwan | `roms/wonderswan/` | `roms/WS/`, `roms/WSC/` | `.ws`, `.zip`, `.7z` | **`PICO: mednafen_wswan`**, `SA: oswan` |
| MSX | `roms/msx/` | `roms/MSX/`, `roms/msx2/` | `.rom`, `.mx1`, `.mx2`, `.dsk`, `.cas`, `.zip`, `.7z` | **`PICO: bluemsx`** |
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

## ディスクとサムネイル

- CD系では、`.cue` や `.m3u` が参照するディスク・トラックのファイルも一緒に置き、参照先の名前と相対位置を維持します。PlayStationの起動用に `.cue` を使う場合、組になる `.bin` や `.img` も必要です。PlayStationとNeo Geo CDのランチャーは `.m3u` の空行とコメントを飛ばし、最初の項目を起動します。
- サムネイルはROMと同じカードの `Images/<システムID>/` に置きます。たとえば `roms/FC/My Game.nes` のシステムIDは `nes` なので、`Images/nes/My Game.png` に置きます。システムIDは表の推奨フォルダー名の末尾です。

BIOSやシステムカードが必要な経路は、[エミュレーター別のBIOS配置](storage.ja.md#エミュレーター別のbios配置)を参照してください。
