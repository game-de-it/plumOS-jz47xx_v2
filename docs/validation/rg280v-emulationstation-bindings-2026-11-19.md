# EmulationStationのシステム割り当て確認 — 2026-11-19

PokeMiniにGame Boyのテーマ、PC Engine CDにPC Engineのテーマを共用していたため、正しいROM一覧でも別機種の見た目になっていた。両機種を専用テーマへ分離し、plumOSの既存アイコンと機種名の文字描画を使用する。Game Boy、PC Engineの既存テーマはそのまま保持する。

全26機種について、実機のFE定義とES設定、各起動スクリプト、画像ファイル、実在ROMを使った起動計画（実行なし）を照合した。その他の誤配線は検出しなかった。未対応のメタデータ用platform IDはignoreとし、別機種への分類を避ける。

| ID | テーマの機種表示 | SD2のROMフォルダー | 起動経路 | テーマ |
|---|---|---|---|---|
| nes | Nintendo / Entertainment System | `roms/nes` | `standalone:fceux` | `nes` |
| sfc | Super Nintendo / Entertainment System | `roms/snes` | `standalone:pocketsnes` | `snes` |
| gb | Nintendo / Game Boy | `roms/GB` | `standalone:gambatte` | `gb` |
| gbc | Nintendo / Game Boy Color | `roms/GBC` | `standalone:gambatte` | `gbc` |
| gba | Nintendo / Game Boy Advance | `roms/GBA` | `standalone:regba` | `gba` |
| megadrive | SEGA / Mega Drive | `roms/megadrive` | `standalone:picodrive` | `megadrive` |
| mastersystem | SEGA Master System / Mark III | `roms/mastersystem` | `standalone:picodrive` | `mastersystem` |
| gamegear | SEGA / Game Gear | `roms/GameGear` | `standalone:picodrive` | `gamegear` |
| segacd | SEGA / CD | `roms/SEGACD` | `picoarch:picodrive` | `segacd` |
| pcengine | Nec / PC Engine | `roms/pcengine` | `picoarch:mednafen_pce_fast` | `pcengine` |
| supergrafx | Nec / Supergrafx | `roms/supergrafx` | `picoarch:mednafen_supergrafx` | `supergrafx` |
| pcenginecd | NEC / PC Engine CD | `roms/pcenginecd` | `picoarch:mednafen_pce_fast` | `pcenginecd` |
| psx | Sony / PlayStation | `roms/psx` | `standalone:pcsx4all` | `psx` |
| ngpc | SNK / Neo Geo Pocket Color | `roms/NGPC` | `standalone:race` | `ngpc` |
| wonderswan | Bandai / WonderSwan | `roms/wonderswan` | `picoarch:mednafen_wswan` | `wonderswan` |
| msx | MSX | `roms/msx2` | `picoarch:fmsx` | `msx` |
| atari800 | ATARI / 800 | `roms/atari800` | `standalone:atari800` | `atari800` |
| atari2600 | ATARI / 2600 | `roms/atari2600` | `standalone:stella` | `atari2600` |
| pokemini | Nintendo / Pokemon Mini | `roms/pokemini` | `standalone:pokemini` | `pokemini` |
| lynx | Atari / Lynx | `roms/lynx` | `standalone:handy` | `atarilynx` |
| cpc | AMSTRAD CPC/ / Schneider CPC | `roms/cpc` | `standalone:crocods` | `amstradcpc` |
| zxspectrum | Sinclair / ZX Spectrum | `roms/zxspectrum` | `standalone:unrealspeccy` | `zxspectrum` |
| neogeo | SNK / Neo Geo | `roms/neogeo` | `standalone:gngeo` | `neogeo` |
| neogeocd | SNK / Neo Geo CD | `roms/neogeocd` | `standalone:neo4all` | `neogeocd` |
| amiga | Commodore / Amiga | `roms/amiga` | `standalone:uae4all` | `amiga` |
| arcade | FinalBurn Alpha | `roms/arcade` | `standalone:fba44` | `fba` |

再確認用: `python3 scripts/audit-rg280v-emulationstation.py`。ROMの起動や設定変更は行わない。

実機画面取得: GB、PokeMini、PC Engine CDのTOPとROM一覧。PokeMiniはPokemon Mini表示とMINファイル一覧、PC Engine CDは専用表示とCDタイトル一覧を確認。画面取得ファイルはGit管理外の `output/rg280v-emulationstation/` に保存した。
