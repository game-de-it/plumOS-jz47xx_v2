# 確認済みOPKのFE正規経路への登録（2026-11-18）

## 対象

ユーザーの採用指示に従い、確認済み17種類と条件付き採用のFBA44を登録する。SMS Plus GG/MSは個別OPKのため、パッケージは19本。FCEUX 2.2.3、Gambatte 2020、NEO4ALL、FBA44も対象。

- 既存機種への追加: NES/FCEUX 2.2.3、GB・GBC/Gambatte 2020とOhBoy、Mega Drive/Genesis Plus GX、GG/MSのSMS Plus、PCE/Temper、WonderSwan/Oswan。
- 無効だったNGPCをRace Explorerで有効化。以前拒否されたRA経路を戻さない。
- 新設: Atari 800、Atari 2600、Pokémon Mini、Lynx、Amstrad CPC、ZX Spectrum、Neo Geo、Neo Geo CD、Amiga、Arcade。
- 有効だった既存機種の既定エミュ・選択肢は保持。ArcadeはFBA44を既定にした新機種とし、無効の旧FBNeo機種は変更しない。

## 実装

`standalone-opk-routes.json` は採用する元OPKの場所とSHA-256、対応機種を定義する。`build-rg280v-opk-routes.py` は元OPKを再展開し、全desktopが正規ラッパーと任意ROMを使うように変更。各実行ELFのSHA-256は変更前後で一致。エミュ本体の再ビルドや共通SDL/ALSAの置換はしていない。

実行は `plumos-standalone-launch` → `plumos-opk-emulator-launch` → `emulators/opk/*.opk`。HOMEはSD1の `home/opk/EMULATOR`、既存の確認済み設定を初回移行する。NEO4ALLのISO/CUE/M3Uは空白やCRLFを含む名前でも引数を分割しない。BIOSはSD2の `bios/opk/EMULATOR` からSD1の正規BIOS参照へ接続する。ROM/BIOSをOPKやGitへ埋め込まない。

NGPCなど新機種の追加は既存device JSONへマージし、リポジトリの古いJSONでユーザー設定を巻き戻さない。SELECTに表示する名前はFCEUX 2.2.3、Gambatte 2020等の識別できる表記を追加。新機種の画像は既存plumOS-RK2020の共通FE seedをそのまま使用し、アイコンごとのSHA-256を記録する。

SD2には確認済みROMを通常フォルダへコピーする。Neo Geo CDの実データは `roms/neogeocd/.discs/Fatal Fury`、一覧は `Fatal Fury.m3u` の1項目。元のApps/TESTのデータと入口は保持する。コピーは既存ファイルが異なれば停止し、照合後にSD2を元のread-onlyへ戻す。

## 検査状況

- 登録マージの冪等性、既存の有効機種の既定維持、有効機種にRAの混入がないことを確認。
- ラッパーは空白名、ISO、CUE、CRLFのM3U→CUE、通常ROM、未許可ID拒否をホスト上で確認。
- FE本体とtext UIはMIPS soft-float向けにビルド済み。
- 実機への転送・通常ROMフォルダの準備・正規経路の起動確認を継続中。完了結果とバックアップ先を追記する。

採用基準の範囲: FBA44はKung-Fu Master等の正常タイトルでの採用であり、Ninja Spiritの約38fps・音飛びを改善済みとはしない。NEO4ALLは確認済みWAV構成を採用し、未検証のMP3や全タイトルの正常を保証する扱いにはしない。
