# OPK試験ROMのSD2移行

ユーザーの指示に従い、今回のOPK試験でSD1へ配置したROM・ゲームデータと追加BIOSをSD2へ移した。エミュレータのOPK、設定、ログ、セーブ領域はSD1へ残した。

- 通常の比較ROM: `/media/data/sd2/.plumos-rg350-tests-20261118/relocated/rom-candidates/`
- Atari800/FBA等の比較ROM: 同 `relocated/visual-roms/`
- 追加ゲーム素材: 同 `relocated/extra-roms/`
- 試験用BIOS: 同 `relocated/bios/`
- NEO4ALLのISO/WAV: 既存の専用フォルダ `/media/data/sd2/.plumos-rg350-tests-20261118/Fatal Fury WAV/` を継続使用

移行前にSD2が `/dev/mmcblk1p1` であること、読み取り専用の状態、空き容量、実行中エミュレータがないことを確認した。FEを一時停止し、専用の所有マーカーを付けた新しい保存先へコピー。全対象のSHA-256一致を確認してから、SD1側を互換シンボリックリンクへ置き換えた。既存のSD2 ROMコレクションは変更していない。

主要移行では47個のツリー／ファイル対応を処理し、ツリー内137ファイルと個別BIOSを照合した。さらにDOSの試験設定を含むフォルダもSD2へ移し、今後のDOSゲーム配置がSD1へ戻らないようにした。移行の生の対応・ハッシュは `output/rg280v-apps/rom-sd2-migration-20261118.json` に記録。

NEO4ALLはISOの実体と同名CUEが同居する必要があるため、SD1にあったISOコピーを削除して、元からSD2にある照合済みの実体ISOを使用した。SD2の専用フォルダ内へ同名の `Fatal Fury.cue` を配置。旧 `home-15/cd` はそのフォルダへの互換リンクとした。WAVファイルへのFAT非対応なリンクを作成していない。

Stella・NEO4ALL・既存のOPK比較起動スクリプトは、ゲームデータのSD2パスを直接参照するよう更新。ROM候補の生成・追加転送もSD2へ向け、一時的な書き込み後は元の読み取り専用状態へ戻す。

移行前のSD1空き49,900 KiBに対し、移行後は161,828 KiB（約158 MiB）。先行して未使用FBA比較OPK4本もMacへ退避・ハッシュ照合後にSD1から除き、退避記録は `output/rg280v-apps/retired-device-opks/archive-record.json` に保存した。使用中のFBA改修版は残している。

## 起動確認

- Stella: SD2のAsteroidsから起動し、約60 FPS・非ゼロPCMを確認。START＋SELECTのメニューからExit Gameを選び、終了コード0でFEへ復帰。
- NEO4ALL: SD2の実体ISOから起動し、約58.8 FPS・非ゼロPCMを確認。CUEと音楽トラックを同じSD2フォルダから参照。既に受けた実機承認を新しいユーザー確認で水増ししていない。
- 移行後、SD2を読み取り専用へ戻し、FEを再起動した。

移行スクリプトは `scripts/migrate-rg350-test-roms-to-sd2.py`。転送ヘルパーは `scripts/rg350_test_rom_storage.py`。履歴の試験ログに残る旧SD1パスは、当時の記録として変更していない。
