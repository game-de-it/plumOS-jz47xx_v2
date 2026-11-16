# RG350 APPREPOSITORY 単体エミュ全候補のRG280V調査（2026-11-17）

対象は [RafaVico/RG350_APPREPOSITORY の Emulators](https://github.com/RafaVico/RG350_APPREPOSITORY/tree/master/Emulators) にある **62本のOPK全件**。ファイル名・SHA-256・desktop `Exec`・ELF ABI・共有ライブラリ依存を静的監査し、RG280V実機で配布OPKを1本ずつ起動した。ROM/BIOS/OPK実体とスクリーンショットはGitに含めない。

## 試験方法と読み方

- 各候補を元の配布OPKのままSD1上の一時ファイルへ転送し、SD2に該当ROMがある26本にはROMパスを指定した。1本あたり8秒で終了させ、同時にDRMスクリーンショット、SDL画面提示の間隔、SDL音声コールバックのPCM信号量を採取した。終了後はFEを再起動した。
- **FPSはエミュレータがSDLへ画面を渡した頻度**。ゲーム内部の実行速度やLCD表示の品質を単独では証明しない。表中の数値は短時間試験の最後の窓で、タイトル、メニュー、ロゴの値も含む。`—`は測定できず、0 FPSを意味しない。
- 「PCM有信号」は音量データが非ゼロだった意味に限る。実機スピーカーでの音程・歪みを聴取した判定ではない。「PCMほぼ無音」はコールバックがあってもサンプルがほぼゼロだった状態。
- 実機ではFEを最終的に復旧し、`plumos-controller-ui --render`の稼働を確認。試験用OPKの一時ファイルも削除済み。個別生ログと画像はGit管理外の `output/rg280v-apps/rg350-device-audit/`、静的監査は `output/rg280v-apps/rg350-catalog-audit.json` にある。

## 集計

| 指標 | 件数 |
| --- | ---: |
| 静的監査・実機起動を実施 | 62 / 62 |
| SD2の該当ROMを指定 | 26 |
| 8秒試験でSDL画面提示を計測 | 16 |
| SDL音声コールバックを計測 | 13 |
| 8秒試験で非ゼロPCMを確認 | 2 |
| 不足している共有ライブラリ名をローダーが報告 | 25 |

**短時間のタイトル／メニュー測定だけでFEへ追加できると判定した候補はない。** 旧ライブラリを要する候補は依存の再構築、ROMやBIOSが無い候補は起動素材の準備が先に必要。既存FEで動いている改修版OPKの評価は、ここで試した配布原版とは区別する。

## 全62本の結果（配布一覧順）

| No. | OPK | 8秒試験の表示・停止理由 | 直近FPS | 音声 |
| ---: | --- | --- | ---: | --- |
| 01 | `3DOh_2018-05-23.opk` | ROMなし／起動後終了 | — | — |
| 02 | `Arnold_2019-12-03.opk` | ROMなし／起動後終了 | — | — |
| 03 | `Atari 800 v1.1.opk` | 起動不可: libreadline.so.6 | — | — |
| 04 | `Atari800_2020-02-14.opk` | 起動不可: libreadline.so.6 | — | — |
| 05 | `ColecoD_2013-06-15-launcher.opk` | ColecoD設定画面 | 30.0 | — |
| 06 | `DCaSTaway_2014-11-09.opk` | DCaSTaway起動画面 | 26.8 | PCMほぼ無音 |
| 07 | `DOSBox_2019-11-11-launcher.opk` | 起動不可: libSDL_sound-1.0.so.1 | — | — |
| 08 | `Daphne_2015-05-07.opk` | ROMなし／起動後終了 | — | — |
| 09 | `DinguxVectrex_2014-05-25.opk` | 起動不可: libpng14.so.14 | — | — |
| 10 | `EasyRPG_2017-12-13.opk` | 起動不可: libvorbisidec.so.1 | — | — |
| 11 | `FCEUX_2019-11-15.opk` | Baseballタイトル（短時間側は本編未確認） | 59.9 | PCMほぼ無音 |
| 12 | `GenesisPlusGX_2019-12-23.opk` | SEGAロゴ（短時間側は本編未確認） | 60.0 | PCMほぼ無音 |
| 13 | `Handy_2019-12-10.opk` | ROMなし／起動後終了 | — | — |
| 14 | `KEGS_2016-05-04.opk` | ROMなし／起動後終了 | — | — |
| 15 | `NEO4All_2019-12-16.opk` | NEO4ALLロゴ | 24.2 | PCMほぼ無音 |
| 16 | `Nestopia_2020-01-01.opk` | 異常終了 (11) | — | — |
| 17 | `OpenBOR-2014.06.03.opk` | 起動不可: libvorbisidec.so.1 | — | — |
| 18 | `Oswan_2019-10-09.opk` | 起動不可: ABI不一致（別実行でも確認） | — | — |
| 19 | `PicoDrive-gcw0_1.99.opk` | ROM指定後に終了・画面未確定 | — | — |
| 20 | `PocketSNES_2019-12-12.opk` | 起動不可: libpng14.so.14 | — | — |
| 21 | `PokeMini_2015-07-05.opk` | PokeMiniメニュー | 55.4 | — |
| 22 | `Potator_2013-09-17.opk` | Potatorメニュー | 30.0 | — |
| 23 | `ProSystem_2013-06-16-launcher.opk` | ProSystemメニュー | 30.0 | — |
| 24 | `Race(Explorer)_2019-12-11.opk` | Baseball Starsタイトル（短時間側は本編未確認） | 60.0 | PCM有信号 |
| 25 | `Race(Neogeo Pocket).opk` | Raceメニュー | 30.0 | — |
| 26 | `ReGBA_2019-12-26.opk` | 起動不可: libpng14.so.14 | — | — |
| 27 | `Snes9x_2019-11-11.opk` | 起動不可: libintl.so.8 | — | — |
| 28 | `Stella_2015-10-06.opk` | 起動不可: libpng14.so.14 | — | — |
| 29 | `Temper_2016-10-20.opk` | 起動不可: libbz2.so.1.0 | — | — |
| 30 | `UAE4All_2019-08-23.opk` | ROMなし／起動後終了 | — | — |
| 31 | `VICEx64_2020-02-13.opk` | 起動不可: libjpeg.so.8 | — | — |
| 32 | `XMAME_2015-03-15.opk` | XMAMEインストーラ | — | — |
| 33 | `crocods_20200115.opk` | CrocoDS起動 | 50.0 | PCMほぼ無音 |
| 34 | `fba44.opk` | 起動不可: libcrypto.so.1.0.0 | — | — |
| 35 | `gambatte-dms-multi-r572u4-20200628.opk` | GBタイトル（短時間側は本編未確認） | 59.9 | PCMほぼ無音 |
| 36 | `gambatte-dms-multi-r572u4-20211021.opk` | GBタイトル（短時間側は本編未確認） | 59.5 | PCMほぼ無音 |
| 37 | `gambatte-opendingux-r572u3-20191201-204032(GB).opk` | GBタイトル（短時間側は本編未確認） | 59.7 | PCMほぼ無音 |
| 38 | `gambatte-opendingux-r572u3-20191201-204032(GBC).opk` | GBC注意画面（短時間側は本編未確認） | 59.9 | PCMほぼ無音 |
| 39 | `gngeo.opk` | ROMなし／起動後終了 | — | — |
| 40 | `gpsp-2019-11-15.opk` | gpSP言語選択 | — | PCMほぼ無音 |
| 41 | `gw-rg350_2020-03-18.opk` | 起動不可: libshake.so.1 | — | — |
| 42 | `jzIntv_2015-03-28.opk` | 起動不可: libpng14.so.14 | — | — |
| 43 | `mame4all-params-5.opk` | ROM指定後に終了・画面未確定 | — | — |
| 44 | `mame4all.opk` | MAME4ALLロゴ | — | — |
| 45 | `mednafen.opk` | 起動不可: libintl.so.8 | — | — |
| 46 | `mednafen_pce.opk` | 起動不可: libintl.so.8 | — | — |
| 47 | `mednafen_pcfx.opk` | 起動不可: libintl.so.8 | — | — |
| 48 | `mupen64plus.opk` | 起動不可: libSDL2-2.0.so.0 | — | — |
| 49 | `ohboy.opk` | GBタイトル（短時間側は本編未確認） | 59.0 | PCM有信号 |
| 50 | `openMSX-0.15-remap.opk` | 起動不可: libtheoradec.so.1 | — | — |
| 51 | `pcsx4all.opk` | 起動不可: libshake.so.1 | — | — |
| 52 | `picodrive_gcw0(32X).opk` | 起動不可: SDLマウス初期化 | — | — |
| 53 | `picodrive_gcw0(CD).opk` | 起動不可: SDLマウス初期化 | — | — |
| 54 | `picodrive_gcw0(MD).opk` | 起動不可: SDLマウス初期化 | — | — |
| 55 | `retro8_v1b_20200108.opk` | 起動不可: libSDL2-2.0.so.0 | — | — |
| 56 | `scummvm-rg350-01132020.opk` | 起動不可: libSDL_net-1.2.so.0 | — | — |
| 57 | `smsplus_gcw0(GG).opk` | 異常終了 (11) | — | — |
| 58 | `smsplus_gcw0(MS).opk` | 異常終了 (11) | — | — |
| 59 | `tic-80_rg350_20200321_steward.opk` | 起動不可: libshake.so.1 | — | — |
| 60 | `uae4all-params-20200430.opk` | ROMなし／起動後終了 | — | — |
| 61 | `unreal_speccy_portable-0.0.86.12_rg350_r1.opk` | 時間制限まで存続、画面未確定 | — | PCMほぼ無音 |
| 62 | `unreal_speccy_portable0.0.59.opk` | 起動不可: libpng14.so.14 | — | — |

## 長めのROM試験

- **Race Explorer / Neo Geo Pocket**: `Baseball Stars Color`でSTART相当を複数回送ると、タイトルからチーム選択・メンバー選択まで進んだ。約48秒の後半窓は **59.99、59.99、59.50 FPS**。44.1 kHz・モノラル16-bit PCMは非ゼロ、最終ゼロ率約23.3%、クリップ率0%。対戦の実プレイには到達していないので、実プレイ60 FPS判定ではない。元の `Race(Neogeo Pocket).opk` はdesktop `Exec`に `%f` がなくROMパスを受け取らず、Explorer版のほうが検証に適する。
- **FCEUX / NES**: `Baseball` はチーム選択画面まで進み、後半窓は約60 FPS。音声コールバックは動くが、採取区間のPCMは無音。試合中の音は今回未判定。既存FEのSA FCEUXの正常動作実績とは別の測定。
- **Genesis Plus GX / Mega Drive**: `Bare Knuckle` はSEGAロゴ後のオープニング映像へ進んだ。画面提示は約60 FPS、44.1 kHzステレオPCMに有信号あり。ただしピークにクリップが含まれ、実機スピーカーでの音質確認は未実施。以前FEのPicoArch版で30 FPSへ落ちる場面があり、今回のオープニング値ではそれを解消したとは言えない。
- **Gambatte 20211021 / GB**: `Super Mario Land` のゲーム画面まで進み、画面提示は約59.7 FPS。PCMコールバックは48 kHzステレオで続くが、サンプルのほぼ全てがゼロ（ピーク4）。配布原版を音声正常とは判定できない。既存FEの修正版Gambatteとは区別する。
- **単体PicoDrive / 32X（現行のSoft floatビルド、前回の継続試験）**: `After Burner` 本編で後半240フレーム窓が25.64、56.81、28.29、26.33、25.71 FPS。PCM信号は継続したが60 FPS維持できず、FE表示は無効のまま。今回のRG350配布版32X/CD/MD OPKは3本とも `SDL_Init failed: Unable to open mouse` で起動しなかった。

## 次に対策する順番

1. 旧共有ライブラリ25件を依存種類で束ね、現行Soft float環境向けに再ビルド可能なソースを優先する。ABI不一致とSDLマウス初期化も分けて扱う。
2. ROMが読み込めた候補を、同じゲーム場面で継続測定する。タイトル・メニューのFPSは採否に使わず、色・音・操作・ゲーム中FPS・終了後FE復帰を個別に確認する。
3. Race ExplorerはROM起動と選択画面まで有望。対戦中のFPSと実機での音・入力を確認してからFE経路を増やす。
