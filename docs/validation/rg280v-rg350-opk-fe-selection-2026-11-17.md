# RG350 OPKエミュ一覧とFE追加候補（2026-11-17）

## 判定の範囲

対象はRG350 APPREPOSITORYのEmulatorsに含まれる配布OPK **62本** と、その後RG280V向けにソースから作り直したAtari800、FBA44、Temperの試験版。配布原版の8秒起動計測と、改修版の実機確認は別の結果として扱う。全62本の初回測定値は [全件監査](rg280v-rg350-standalone-audit-2026-11-17.md)、環境を合わせた再試験は [対策記録](rg280v-rg350-standalone-remediation-2026-11-17.md)、最新3本は [目視・修正記録](rg280v-rg350-visual-tests-2026-11-17.md) を参照。

追加候補はゲーム中の映像・音・操作・メニュー・FEへの復帰を実機で確認した改修版に限る。短時間の画面提示FPS、音声PCMの非ゼロ、タイトルやメニューの表示だけでは合格にしない。

## FE経路への選別

| 判定 | エミュ | 対象 | 根拠・条件 |
| --- | --- | --- | --- |
| 追加候補 | **Atari800 4.1.0 RG280V改修版** | Atari 8-bit | Caverns of Mars、Miner 2049er、Food Fightの3本をユーザーが実機で正常確認。320×240表示と入力を修正済み。FEに機種・ROM起動経路を新設する際は統合後の起動と終了を再確認する。 |
| 追加候補 | **Temper RG280V改修版** | PC Engine HuCard | ゲーム約60 FPSで正常。SELECT＋STARTメニューから戻った後の単独SELECT・START、再度の同時押しをユーザーが実機で正常確認。既存のPC Engine PicoArch経路へ追加する候補。 |
| ROM限定で合格 | **FBA44 RG280V改修版** | Kung-Fu Master | 同ROMはユーザーが60 FPSで正常動作を確認。ただしNinja Spiritは約38 FPSで音飛び。アーケード全体の汎用FE経路には追加しない。個別ROM許可制ならKung-Fu Masterだけ候補。 |
| 追試候補 | Race Explorer | Neo Geo Pocket | Baseball Stars Colorの選択画面まで約60 FPS・PCM有信号。本編の映像・音・入力・メニュー終了が未確認。 |
| 追試候補 | OhBoy | Game Boy | タイトル約59 FPS・PCM有信号。本編と実機スピーカー音、FE復帰が未確認。既存GB経路とは別判定。 |

**現在のFE状態:** `assets/frontend/systems.json` と端末設定のSHA-256は `8c4f65c763f02a10afe687b1b6e0e699cb1ce80a961a9b5b8d2d356864c938ce` で一致。Atari800、Temper、FBA44の3本は現在 `START → Apps` の `TEST` 項目にのみ配置している。正式なFEエミュ経路にはまだ登録していない。既存FEのFCEUX、PocketSNES、Gambatte、ReGBA、PicoDrive、PCSX4ALLなどは別ビルドであり、同名の配布原版OPKの判定を流用しない。

## 配布OPK全62本

「初回8秒の観測」は配布原版の当時の記録で、ライブラリ不足表示などはFE相当環境で再試験すると変わる。後続結果を確認せずに採否の理由として使わない。「追加候補」はその名前の**改修版**を指し、配布原版をそのまま登録できる意味ではない。

| No. | 配布OPK | 初回8秒の観測 | 現時点のFE判断 |
| ---: | --- | --- | --- |
| 01 | `3DOh_2018-05-23.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 02 | `Arnold_2019-12-03.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 03 | `Atari 800 v1.1.opk` | 起動不可: libreadline.so.6（FPS未測定） | 未採用・検証不足 |
| 04 | `Atari800_2020-02-14.opk` | 起動不可: libreadline.so.6（FPS未測定） | 改修版は追加候補。配布原版は不合格。ソース改修版では3 ROMの映像・音・操作を実機確認。 |
| 05 | `ColecoD_2013-06-15-launcher.opk` | ColecoD設定画面（30.0 FPS） | 未採用・検証不足 |
| 06 | `DCaSTaway_2014-11-09.opk` | DCaSTaway起動画面（26.8 FPS） | 未採用・検証不足 |
| 07 | `DOSBox_2019-11-11-launcher.opk` | 起動不可: libSDL_sound-1.0.so.1（FPS未測定） | 未採用・検証不足 |
| 08 | `Daphne_2015-05-07.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 09 | `DinguxVectrex_2014-05-25.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 10 | `EasyRPG_2017-12-13.opk` | 起動不可: libvorbisidec.so.1（FPS未測定） | 未採用・検証不足 |
| 11 | `FCEUX_2019-11-15.opk` | Baseballタイトル（短時間側は本編未確認）（59.9 FPS） | 未採用・検証不足 |
| 12 | `GenesisPlusGX_2019-12-23.opk` | SEGAロゴ（短時間側は本編未確認）（60.0 FPS） | 未採用・検証不足 |
| 13 | `Handy_2019-12-10.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 14 | `KEGS_2016-05-04.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 15 | `NEO4All_2019-12-16.opk` | NEO4ALLロゴ（24.2 FPS） | 未採用・検証不足 |
| 16 | `Nestopia_2020-01-01.opk` | 異常終了 (11)（FPS未測定） | 未採用・検証不足 |
| 17 | `OpenBOR-2014.06.03.opk` | 起動不可: libvorbisidec.so.1（FPS未測定） | 未採用・検証不足 |
| 18 | `Oswan_2019-10-09.opk` | 起動不可: ABI不一致（別実行でも確認）（FPS未測定） | 未採用・検証不足 |
| 19 | `PicoDrive-gcw0_1.99.opk` | ROM指定後に終了・画面未確定（FPS未測定） | 未採用・検証不足 |
| 20 | `PocketSNES_2019-12-12.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 21 | `PokeMini_2015-07-05.opk` | PokeMiniメニュー（55.4 FPS） | 未採用・検証不足 |
| 22 | `Potator_2013-09-17.opk` | Potatorメニュー（30.0 FPS） | 未採用・検証不足 |
| 23 | `ProSystem_2013-06-16-launcher.opk` | ProSystemメニュー（30.0 FPS） | 未採用・検証不足 |
| 24 | `Race(Explorer)_2019-12-11.opk` | Baseball Starsタイトル（短時間側は本編未確認）（60.0 FPS） | 有望・ゲーム本編未確認。選択画面までは約60 FPS。対戦中の音・入力・終了は未確認。 |
| 25 | `Race(Neogeo Pocket).opk` | Raceメニュー（30.0 FPS） | 未採用・検証不足 |
| 26 | `ReGBA_2019-12-26.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 27 | `Snes9x_2019-11-11.opk` | 起動不可: libintl.so.8（FPS未測定） | 未採用・検証不足 |
| 28 | `Stella_2015-10-06.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 29 | `Temper_2016-10-20.opk` | 起動不可: libbz2.so.1.0（FPS未測定） | 改修版は追加候補。配布原版は不合格。ソース改修版では約60 FPS、メニュー入力修正を実機確認。 |
| 30 | `UAE4All_2019-08-23.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 31 | `VICEx64_2020-02-13.opk` | 起動不可: libjpeg.so.8（FPS未測定） | 未採用・検証不足 |
| 32 | `XMAME_2015-03-15.opk` | XMAMEインストーラ（FPS未測定） | 未採用・検証不足 |
| 33 | `crocods_20200115.opk` | CrocoDS起動（50.0 FPS） | 未採用・検証不足 |
| 34 | `fba44.opk` | 起動不可: libcrypto.so.1.0.0（FPS未測定） | Kung-Fu限定で合格。配布原版は不合格。ソース改修版のKung-Fu Masterは60 FPS。Ninja Spiritは約38 FPS・音飛び。 |
| 35 | `gambatte-dms-multi-r572u4-20200628.opk` | GBタイトル（短時間側は本編未確認）（59.9 FPS） | 未採用・検証不足 |
| 36 | `gambatte-dms-multi-r572u4-20211021.opk` | GBタイトル（短時間側は本編未確認）（59.5 FPS） | 未採用・検証不足 |
| 37 | `gambatte-opendingux-r572u3-20191201-204032(GB).opk` | GBタイトル（短時間側は本編未確認）（59.7 FPS） | 未採用・検証不足 |
| 38 | `gambatte-opendingux-r572u3-20191201-204032(GBC).opk` | GBC注意画面（短時間側は本編未確認）（59.9 FPS） | 未採用・検証不足 |
| 39 | `gngeo.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 40 | `gpsp-2019-11-15.opk` | gpSP言語選択（FPS未測定） | 未採用・検証不足 |
| 41 | `gw-rg350_2020-03-18.opk` | 起動不可: libshake.so.1（FPS未測定） | 未採用・検証不足 |
| 42 | `jzIntv_2015-03-28.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 43 | `mame4all-params-5.opk` | ROM指定後に終了・画面未確定（FPS未測定） | 未採用・検証不足 |
| 44 | `mame4all.opk` | MAME4ALLロゴ（FPS未測定） | 未採用・検証不足 |
| 45 | `mednafen.opk` | 起動不可: libintl.so.8（FPS未測定） | 未採用・検証不足 |
| 46 | `mednafen_pce.opk` | 起動不可: libintl.so.8（FPS未測定） | 未採用・検証不足 |
| 47 | `mednafen_pcfx.opk` | 起動不可: libintl.so.8（FPS未測定） | 未採用・検証不足 |
| 48 | `mupen64plus.opk` | 起動不可: libSDL2-2.0.so.0（FPS未測定） | 未採用・検証不足 |
| 49 | `ohboy.opk` | GBタイトル（短時間側は本編未確認）（59.0 FPS） | 有望・ゲーム本編未確認。タイトル約59 FPSとPCM信号を確認。ゲーム中と実機音は未確認。 |
| 50 | `openMSX-0.15-remap.opk` | 起動不可: libtheoradec.so.1（FPS未測定） | 未採用・検証不足 |
| 51 | `pcsx4all.opk` | 起動不可: libshake.so.1（FPS未測定） | 未採用・検証不足 |
| 52 | `picodrive_gcw0(32X).opk` | 起動不可: SDLマウス初期化（FPS未測定） | 未採用・検証不足 |
| 53 | `picodrive_gcw0(CD).opk` | 起動不可: SDLマウス初期化（FPS未測定） | 未採用・検証不足 |
| 54 | `picodrive_gcw0(MD).opk` | 起動不可: SDLマウス初期化（FPS未測定） | 未採用・検証不足 |
| 55 | `retro8_v1b_20200108.opk` | 起動不可: libSDL2-2.0.so.0（FPS未測定） | 未採用・検証不足 |
| 56 | `scummvm-rg350-01132020.opk` | 起動不可: libSDL_net-1.2.so.0（FPS未測定） | 未採用・検証不足 |
| 57 | `smsplus_gcw0(GG).opk` | 異常終了 (11)（FPS未測定） | 未採用・検証不足 |
| 58 | `smsplus_gcw0(MS).opk` | 異常終了 (11)（FPS未測定） | 未採用・検証不足 |
| 59 | `tic-80_rg350_20200321_steward.opk` | 起動不可: libshake.so.1（FPS未測定） | 未採用・検証不足 |
| 60 | `uae4all-params-20200430.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 61 | `unreal_speccy_portable-0.0.86.12_rg350_r1.opk` | 時間制限まで存続、画面未確定（FPS未測定） | 未採用・検証不足 |
| 62 | `unreal_speccy_portable0.0.59.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |

## 未了の確認

- Atari800とTemperは正式なFE経路へ統合した後、ROM選択、設定保存、終了後FE復帰を再確認する。
- FBA44はKung-Fu Master以外を汎用的に合格としない。Battle Chopperは実プレイと音質、Ninja Spiritは性能改善が残る。
- Race ExplorerとOhBoyは本編での実機音・操作・終了を確認してから追加を判断する。
