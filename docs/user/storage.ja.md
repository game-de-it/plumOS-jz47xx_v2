# SDカード構成とフォルダー

[English](storage.md) · [ユーザーガイド](README.ja.md) · [セーブの保存先](save-data.ja.md)

SD1はplumOSの起動と設定を保持するカードです。ゲームはSD1だけでも利用でき、SD2を追加するとゲーム、BIOS、サムネイルの置き場所に使えます。[機種ごとのスロットの位置](README.ja.md#sdカードの差し込み先)

## SD1のパーティション

| パーティション | ボリューム名 | 形式と容量 | 用途 |
| --- | --- | --- | --- |
| p1 | `PLUMOSBOOT` | FAT32、128 MiB | 起動ファイルと前回選択した機種。本体上では `/boot`。 |
| p2 | `PLUMOSDATA` | ext4、1.5 GiB | フロントエンド、エミュレーター、アプリ、設定、セーブ。本体上では `/media/data`。 |
| p3 | `PLUMOS` | FAT32、カードの残り領域 | ゲーム、BIOS、サムネイルなどのユーザー領域。本体上では `/media/user`。 |

初回起動でp3の初期領域（64 MiB）をカード末尾まで拡張し、FAT32の `PLUMOS` を作成します。完了後は、同じSD1を別の対応機種に挿しても拡張や初期化を繰り返しません。

macOSやWindowsでゲームなどを追加するときは `PLUMOS` を開きます。認識できない領域をフォーマットするよう求められた場合はキャンセルしてください。

## SD2の使い方

SD2は任意のデータカードです。先頭パーティションにFAT32を使うと、macOSやWindowsでもファイルをコピーできます。plumOSはFAT32とext4に対応し、先頭パーティションを本体上の `/media/data/sd2` に読み取り専用でマウントします。SD2へのファイルの追加や整理は、本体をシャットダウンしてからカードリーダーで行います。

## ROMとBIOSの参照先

起動時に `roms/` と `bios/` の参照先を個別に選びます。SD2の直下に該当フォルダーがあればSD2を使い、なければSD1の `PLUMOS` を使います。この判定にはフォルダーの有無を使うため、SD2側の空フォルダーも対象になります。サムネイルはROMの参照先と同じカードから読み込みます。

| SD2直下のフォルダー | ゲームとサムネイル | BIOSフォルダー |
| --- | --- | --- |
| `roms/` と `bios/` の両方 | SD2 | SD2 |
| `roms/` のみ | SD2 | SD1 |
| `bios/` のみ | SD1 | SD2 |
| どちらもない、またはSD2を挿していない | SD1 | SD1 |

## エミュレーター別のBIOS配置

上の表で選ばれたカードの `bios/` に、利用できる権利を持つBIOSファイルを置いてください。

| エミュレーター | ファイルと配置先 |
| --- | --- |
| PCSX4ALL | `bios/scph1001.bin`、またはエミュレーターで選んだBIOS名。 |
| fMSX | `MSX.ROM`、`MSX2.ROM`、`MSX2EXT.ROM` など、fMSXが参照するシステムROMを `bios/` 直下に置きます。 |
| blueMSX | 元のMSX機種プロファイルを使うには `Machines/` と `Databases/` の一式を `bios/` に置きます。同梱のC-BIOSはカートリッジゲーム用です。 |
| Atari800 | 標準では内蔵のAltirraファームウェアを使います。オリジナルのROMを使う場合は `bios/opk/atari800/` に `5200.rom`、`ataribas.rom`、`atariosb.rom`、`atarixl.rom` を必要に応じて置きます。 |
| Unreal Speccy | `bios/opk/unrealspeccy/` に `sos128_0.rom`、`sos128_1.rom`、`sos48.rom`、`service.rom`、`dos513f.rom` を置きます。各ファイルは16 KiBです。 |
| PC Engine CD（Beetle PCE Fast） | 通常は `bios/syscard3.pce` を使います。 |
| Sega CD（PicoDrive） | ディスクの地域に合わせて `bios/bios_CD_J.bin`（日本）、`bios/bios_CD_U.bin`（北米）、`bios/bios_CD_E.bin`（欧州）を使います。 |
| CrocoDS（単体版・PicoArch版） | `bios/opk/crocods/` に `cpc6128.rom`（32 KiB）と `amsdos.rom`（16 KiB）を置きます。両方必要です。 |
| RACE | 外部BIOSを使う場合、Neo Geo Pocketは `bios/opk/race/npbiosb.bin`、Neo Geo Pocket Colorは `bios/opk/race/npbiosc.bin` に置きます。 |
| UAE4All、GnGeo、NEO4ALL | それぞれ `bios/opk/uae4all/kick.rom`、`bios/opk/gngeo/neogeo.zip`、`bios/opk/neo4all/neocd.bin` を使用します。 |

## ユーザー領域のフォルダー

| フォルダー | 用途 |
| --- | --- |
| `roms/` | システム別のゲームファイル。[26システムのフォルダー一覧](supported-systems.ja.md) |
| `bios/` | 利用者が用意するBIOSやシステムファイル。例はPCSX4ALLの `bios/scph1001.bin`、UAE4Allの `bios/opk/uae4all/kick.rom`。 |
| `Images/` | `Images/<システムID>/` に置くゲームのサムネイル。 |
| `Screenshots/` | 初回に用意される画面画像用フォルダー。エミュレーター独自の保存機能は別の場所を使うことがあります。 |
| `Music/` | 音楽ファイルの置き場所。 |
| `apps/` | SD1の予約フォルダー。[OPKアプリの扱い](README.ja.md#opkアプリ) |
| `updates/` | SD1に置く署名付きランタイム更新パッケージ。[更新手順](README.ja.md#sd1からランタイムを更新する) |

セーブ・ステート・設定のバックアップには、SD1の `PLUMOSDATA` を含めます。[セーブの保存先とバックアップ](save-data.ja.md)
