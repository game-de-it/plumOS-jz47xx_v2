# RG350 OPKエミュ一覧とFE追加候補（2026-11-17）

**ROM未指定項目の再試験:** [2026-11-18の結果](rg280v-rg350-missing-rom-retest-2026-11-18.md)。新しい確認候補はStellaの3 ROMと、BGM対応NEO4ALLのWAV試験版。Appsに独立した試験入口を追加。下記27項目という記述は追加前の履歴。

**2026-11-18 実機確認:** FCEUX 2.2.3、PokeMini、Race Explorer、CrocoDS、Gambatteはユーザーが動作正常と確認。Genesis Plus GXはALSA改修版のBare Knuckleを正常確認。OhBoyも最終改修版の音声・スケール・メニューを正常確認。詳細は [実機結果](rg280v-rg350-user-results-2026-11-18.md)。

**重複確認後の更新:** [既存SAとの照合結果](rg280v-rg350-sa-duplicates-2026-11-17.md) に基づき、PocketSNESとGambatte 2021は別候補から除外。FCEUXは既存SA 2.6.6に対する2.2.3の比較として残す。現在の目視確認メニューは27項目。以下の全件一覧・30項目の記述は重複確認前の監査・配置履歴を含む。

## 判定の範囲

対象はRG350 APPREPOSITORYのEmulatorsに含まれる配布OPK **62本** と、その後RG280V向けにソースから作り直したAtari800、FBA44、Temperの試験版。配布原版の8秒起動計測と、改修版の実機確認は別の結果として扱う。全62本の初回測定値は [全件監査](rg280v-rg350-standalone-audit-2026-11-17.md)、環境を合わせた再試験は [対策記録](rg280v-rg350-standalone-remediation-2026-11-17.md)、最新3本は [目視・修正記録](rg280v-rg350-visual-tests-2026-11-17.md) を参照。

判定は「目視確認へ進める候補」と「FEへ正式に追加できるもの」を区別する。約60 FPSで画面・音声が正常と見込めるものは目視確認候補とし、50 FPS以上も確認対象に含める。ゲーム実行が50 FPS未満だったものは性能面から確認優先度を下げる。50 FPSちょうどは候補側に含める。タイトル・メニューのFPSしかないものは、その条件を明記して本編確認へ進める。測定不能、ROM未指定、メニューだけ30 FPSなどの結果はゲーム性能不足とは断定しない。

ROM候補とソース対策の最新状況は [ROM・ソース再確認表](rg280v-rg350-rom-source-review-2026-11-17.md) を参照。以前の「ROMなし」は監査時のROM未指定を含む。本体をソース修正したのはAtari800・FBA44・Temperで、ほかを「再ビルドしても動かなかった」とは判定しない。

## FE経路への選別

| 段階 | エミュ | 対象・結果 | 次の扱い |
| --- | --- | --- | --- |
| 実機確認済み・FE追加候補 | **Atari800 4.1.0 RG280V改修版** | 試験3 ROMが実機で正常。表示比率・入力修正済み | FE統合へ進める |
| 実機確認済み・FE追加候補 | **Temper RG280V改修版** | 約60 FPS、映像・音・操作正常。メニュー復帰後の誤入力も修正確認済み | PC EngineのFE経路へ追加可能 |
| ROMにより実機確認済み | **FBA44 RG280V改修版** | Kung-Fu Masterは60 FPSで正常。Ninja Spiritは約38 FPS・音飛び | Kung-Fu Masterは採用候補。ほかはROMごとの速度で選別 |
| 目視確認候補・優先 | **Race Explorer** | Baseball Stars Colorの選択画面まで約60 FPS、画面とPCM信号を確認 | 本編を目視・聴取確認する |
| 実機確認済み・FE追加候補 | **OhBoy RG280V改修版** | 音声・スケール・メニューをユーザーが正常確認 | 最終修正版をFE統合候補にする |
| 目視確認候補・優先 | **Genesis Plus GX配布OPK** | Bare Knuckleのオープニング約60 FPS、PCM信号あり。クリップを記録 | 本編の速度・音質を確認する。既存PicoArch版とは別判定 |
| 目視確認候補 | **PokeMini** | メニュー約55 FPS | ROMを動かし、本編の映像・音・速度を確認する |
| 目視確認候補 | **CrocoDS** | 起動画面約50 FPS、採取音声はほぼ無音 | 本編の速度と音を確認する |
| 速度面は候補・音声確認が先 | **FCEUX配布OPK、Gambatte配布4版** | タイトル等で約59〜60 FPS。採取した音声は無音またはほぼ無音 | 発音する本編場面で再確認する。音声正常とはまだ記載しない |
| 性能面で低優先 | **Snes9x配布OPK** | SFC ROMで約34〜37 FPS | 目視確認を急がず、性能対策が必要になった時に再検討 |
| 性能面で低優先 | **FBA44のNinja Spirit** | 実機約38 FPS、音飛び | 性能対策を保留 |
| 性能面で低優先 | **単体PicoDriveの32X** | After Burnerの本編約25〜56 FPS、50未満の窓が継続 | 常用候補の優先度を下げる |

**現在のFE状態:** `assets/frontend/systems.json` と端末設定のSHA-256は `8c4f65c763f02a10afe687b1b6e0e699cb1ce80a961a9b5b8d2d356864c938ce` で一致（前回照合時）。Atari800、Temper、FBA44の3本は現在 `START → Apps` の `TEST` 項目にのみ配置している。正式なFEエミュ経路にはまだ登録していない。既存FEのFCEUX、PocketSNES、Gambatte、ReGBA、PicoDrive、PCSX4ALLなどは別ビルドであり、同名の配布原版OPKの判定を流用しない。

## 配布OPK全62本

「初回8秒の観測」は配布原版の当時の記録で、ライブラリ不足表示などはFE相当環境で再試験すると変わる。後続結果を確認せずに採否の理由として使わない。「実機確認済み」は改修版の結果を指す。目視確認候補は、正式なFE採用前の確認対象を意味する。

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
| 11 | `FCEUX_2019-11-15.opk` | Baseballタイトル（短時間側は本編未確認）（59.9 FPS） | 実機確認済み。ユーザーが動作正常と確認（2026-11-18）。既存SAとは別版2.2.3。 |
| 12 | `GenesisPlusGX_2019-12-23.opk` | SEGAロゴ（短時間側は本編未確認）（60.0 FPS） | 要修正。ユーザーがBare Knuckleで音声異常を確認（2026-11-18）。 |
| 13 | `Handy_2019-12-10.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 14 | `KEGS_2016-05-04.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 15 | `NEO4All_2019-12-16.opk` | NEO4ALLロゴ（24.2 FPS） | 未採用・検証不足 |
| 16 | `Nestopia_2020-01-01.opk` | 異常終了 (11)（FPS未測定） | 未採用・検証不足 |
| 17 | `OpenBOR-2014.06.03.opk` | 起動不可: libvorbisidec.so.1（FPS未測定） | 未採用・検証不足 |
| 18 | `Oswan_2019-10-09.opk` | 起動不可: ABI不一致（別実行でも確認）（FPS未測定） | 未採用・検証不足 |
| 19 | `PicoDrive-gcw0_1.99.opk` | ROM指定後に終了・画面未確定（FPS未測定） | 未採用・検証不足 |
| 20 | `PocketSNES_2019-12-12.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 21 | `PokeMini_2015-07-05.opk` | PokeMiniメニュー（55.4 FPS） | 実機確認済み。ユーザーが動作正常と確認（2026-11-18）。 |
| 22 | `Potator_2013-09-17.opk` | Potatorメニュー（30.0 FPS） | 未採用・検証不足 |
| 23 | `ProSystem_2013-06-16-launcher.opk` | ProSystemメニュー（30.0 FPS） | 未採用・検証不足 |
| 24 | `Race(Explorer)_2019-12-11.opk` | Baseball Starsタイトル（短時間側は本編未確認）（60.0 FPS） | 実機確認済み。ユーザーが動作正常と確認（2026-11-18）。 |
| 25 | `Race(Neogeo Pocket).opk` | Raceメニュー（30.0 FPS） | 未採用・検証不足 |
| 26 | `ReGBA_2019-12-26.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 27 | `Snes9x_2019-11-11.opk` | 起動不可: libintl.so.8（FPS未測定） | 性能面で低優先。後続ROM試験で約34〜37 FPS。 |
| 28 | `Stella_2015-10-06.opk` | 起動不可: libpng14.so.14（FPS未測定） | 未採用・検証不足 |
| 29 | `Temper_2016-10-20.opk` | 起動不可: libbz2.so.1.0（FPS未測定） | 改修版は追加候補。配布原版は不合格。ソース改修版では約60 FPS、メニュー入力修正を実機確認。 |
| 30 | `UAE4All_2019-08-23.opk` | ROMなし／起動後終了（FPS未測定） | 未採用・検証不足 |
| 31 | `VICEx64_2020-02-13.opk` | 起動不可: libjpeg.so.8（FPS未測定） | 未採用・検証不足 |
| 32 | `XMAME_2015-03-15.opk` | XMAMEインストーラ（FPS未測定） | 未採用・検証不足 |
| 33 | `crocods_20200115.opk` | CrocoDS起動（50.0 FPS） | 実機確認済み。ユーザーが動作正常と確認（2026-11-18）。 |
| 34 | `fba44.opk` | 起動不可: libcrypto.so.1.0.0（FPS未測定） | Kung-Fu限定で合格。配布原版は不合格。ソース改修版のKung-Fu Masterは60 FPS。Ninja Spiritは約38 FPS・音飛び。 |
| 35 | `gambatte-dms-multi-r572u4-20200628.opk` | GBタイトル（短時間側は本編未確認）（59.9 FPS） | 速度面は目視確認候補（約59〜60 FPS）。採取音声が無音に近く、発音する本編で確認が必要。 |
| 36 | `gambatte-dms-multi-r572u4-20211021.opk` | GBタイトル（短時間側は本編未確認）（59.5 FPS） | 速度面は目視確認候補（約59〜60 FPS）。採取音声が無音に近く、発音する本編で確認が必要。 |
| 37 | `gambatte-opendingux-r572u3-20191201-204032(GB).opk` | GBタイトル（短時間側は本編未確認）（59.7 FPS） | 速度面は目視確認候補（約59〜60 FPS）。採取音声が無音に近く、発音する本編で確認が必要。 |
| 38 | `gambatte-opendingux-r572u3-20191201-204032(GBC).opk` | GBC注意画面（短時間側は本編未確認）（59.9 FPS） | 速度面は目視確認候補（約59〜60 FPS）。採取音声が無音に近く、発音する本編で確認が必要。 |
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
| 49 | `ohboy.opk` | GBタイトル（短時間側は本編未確認）（59.0 FPS） | 改修版は実機確認済み・FE追加候補。音声・スケール・メニューをユーザーが正常確認（2026-11-18）。 |
| 50 | `openMSX-0.15-remap.opk` | 起動不可: libtheoradec.so.1（FPS未測定） | 未採用・検証不足 |
| 51 | `pcsx4all.opk` | 起動不可: libshake.so.1（FPS未測定） | 配布原版は低優先。後続試験で黒画面・約3 FPS。既存改修版は別判定。 |
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
- 実機確認済み候補をFEへ統合する際は、正式な起動経路からの起動・終了を確認する。

2026-11-18追記: Genesis Plus GXのBare KnuckleはALSA直接出力版でユーザーが正常動作を確認した。SDL版で生じた低速化は撤回し、[音声修正記録](rg280v-opk-audio-fixes-2026-11-18.md)のALSA版を比較候補に使う。
