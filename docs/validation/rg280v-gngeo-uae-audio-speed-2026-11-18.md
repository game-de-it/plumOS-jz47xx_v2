# RG280V GnGeo / UAE4All 音声・速度修正（2026-11-18）

## 判定方法

CPUは996 MHzを維持。ROM/BIOSは既存SD2、設定・ステート・ログはSD1。初期ロードとメニューをゲーム中のfpsから除外する。実速度を上げたり同じ画像を再送して50fpsに見せる方法は採らない。Appsへの追加は画面取得・PCM・速度・入力・通常終了とFE復帰の確認後とし、実機スピーカーの聴取と目視はユーザー確認待ちとして区別する。

## GnGeo

- リンク対象は `src/ym2610/libym2610.a`。この音源は `conf.sample_rate` を読むが、Miyoo側の設定処理は同フィールドを初期化しておらず0だった。
- SDL出力デバイスは44.1 kHzで正常に開いていた。最初のコールバックに入ったまま戻らないことを診断ログで確認。ゼロ周期の音源処理が音声スレッドを占有し、映像も約40〜45fpsに下げていた。
- 設定キャッシュで出力と同じ44.1 kHzを設定。音声仕様構造体のゼロ初期化、割当て・SDL初期化・open失敗の確認、失敗時の無効化を追加。
- Z80/68000の音源アクセスとSDLコールバックをSDL音声ロックで排他。描画やVSync待ちはロック外。
- START＋SELECTでメニュー、Aで決定、Bでゲームへ復帰。メニューがキー解放を消費しても次の同時押しを認識するよう復帰時にキー状態を同期。
- Art of Fightingでメニューを3回開き、2回Bでゲームへ戻って最後にExit。実子プロセス終了0、FE復帰を確認。

## UAE4All

- FAME Cコアによる前回の画面修正を維持。
- NO_THREADSの旧リングはSDLコールバックがエミュレーション側の書込みポインタまで変更し、未完成データを読む構造だった。GCW0経路ではバイト数を管理するFIFOに変更。コールバックは待たず、不足分をゼロで埋め、producerのポインタには触らない。
- PALの音声クロックを282ライン補正から通常312ラインへ修正。長フレーム（LOF）の313ラインも反映し、50Hzでも音声FIFOが徐々に溢れる差を除去する。
- 音声バッファ位置でフレーム目標を増減する旧補正をGCW0経路では使わず、エミュレーションの垂直同期ごとにPAL 50Hz（NTSCは設定された60Hz）の期限でペーシング。Frameskip 0でも無制限の約80fpsにならない。
- RG280VではSTARTによるSuperThrottle切替を無効化。START＋SELECTのメニュー操作で音声停止・高速化を誤発動させない。
- ステート名はROMのフルパスから私有SD1ディレクトリ内のハッシュ名へ変更。旧固定長バッファを1024バイトに拡張し、SD2へステートを書かない。

## 計測用機能

`probe-rg280v-standalone-health.c` に任意の8秒PCM保存とキーイベント記録を追加。専用の `libstandalone-health-sdl1.so` を試験時だけ使用し、通常AppsにLD_PRELOADや保存用環境変数を入れない。PCMは開始秒を指定でき、録音が際限なくSDを埋めない。

## 最終結果

GnGeo最終パッケージ: `4147d4815405d31bc5e48c27a3b668139c86eb279a6828b07df836aadcdc4aaf`。バイナリ: `572aea4da2714bc7d3214c0a4549dbda40a15b260a70832512783d812688a5d8`。

| ROM | ゲーム中の更新 | 表示・PCM | 終了/FE |
| --- | --- | --- | --- |
| Art of Fighting | 約59〜60fps | 対戦画面、音声データ正常 | 子終了0/復帰 |
| Art of Fighting 2 | 約59〜60fps | 対戦画面、音声データ正常 | 子終了0/復帰 |
| Art of Fighting 3 | 約59〜60fps | 対戦中に入力、音声データ正常 | 子終了0/復帰 |

`gngeo-aof-release-final-20261118`、`gngeo-aof2-release-20261118`、`gngeo-aof3-gameplay-final-20261118` の監査を参照。別試行の8秒PCMは352800フレーム、RMS3643.98、DC約48〜50、飽和0。長い試行の累積飽和は0.01%程度の一時的な値で、全体が飽和するPCM形式の誤りはない。スピーカーの聴感確認は未実施。

UAE4All最終パッケージ: `406a6a174de4af5520eb2fb52b6861236128ee7748c0a559aa05bd93daa05f78`。バイナリ: `8b1b241350b1592153e9fee7e9b85d9e6b464079b01777f54219075f96220657`。

- `uae-field-clock-babyjo-final-20261118` でBaby Joを実プレイ。130秒の監査取得に加え、`uae-final-late.png` と `uae-final-play-after-input.png` で位置・ジャンプ・スクロールの変化、スコア200、残機表示を確認。
- ゲーム中の5つの計測窓（flips 6000〜6960）は50.00、50.02、50.01、50.00、49.99fps。ロード・メニューを含む最後の窓46〜48fpsをゲーム性能として扱わない。
- 44.1 kHz/16bit/mono。メニューを開く前、開閉後、終了時の全てでFIFO underflows=0 / overflows=0、残量2048バイト。音声周期の313ライン対応前はoverflowが増加していた。
- 実プレイ付近の8秒PCMは352800フレーム、RMS4921.95、飽和0。`uae-babyjo-final.{pcm,wav,json}` に保存。長い監査でもALSAエラー・underrun・PCM飽和0。
- START＋SELECT→Bでゲームへ復帰→再度START＋SELECT→Exit。実子プロセス終了0、FE復帰。ロード中の黒画面は継続ハングと誤認しやすく、今回の実プレイ到達は起動から約2分。Aはジョイスティックfire、Xは左マウスボタン。ロード待ちも含め物理キーで確認する。
- NASの `_etc/amiga` にはBaby Joと3rd Day - The Ripperの2本のみ（後者の同名ディレクトリも存在）。`uae-third-day-disk-check-20261118` では3rd Dayの説明画面・音声・50Hz更新・通常終了まで確認したが、実プレイへの移行は確認していないためAppsへ追加しない。
- ステートの保存先はソース上でSD1へ修正。実際のセーブ/ロード操作は今回の受入れ項目に含めていない。

## Apps反映

`source-repair-visual-candidates.json` にGnGeo 3入口とUAE4All/Baby Jo 1入口を追加。既存9入口を保ち、合計13入口/7パッケージ。ROM/BIOSはSD2の既存ファイルを参照し、通常Appsには計測ライブラリやPCM保存を設定しない。

PALの真の50Hzは短い計測窓で49.99等になるため、導入スクリプトは明示したnative_fps=50の候補のみ0.05fpsまでの計測揺れを許可する。49fps台の性能不足を合格にする例外ではない。生の最小計測値49.99をmanifestに保存する。

通常AppsのGnGeo入口をFE操作で起動し、対戦画面の移動・ジャンプ／攻撃を取得。START＋SELECTからExitし、`PLUMOS_EMULATOR_EXIT=0`、元のFE PID30656へ復帰。証拠: `gngeo-normal-apps-game.png`、`gngeo-normal-apps-result.log`。

UAE4Allも通常Apps起動からSTART＋SELECT→Bで復帰→再度メニューからExitし、終了0/同じFEへ復帰。短い試行ではロード画面までだったため、追加で130秒進めて実プレイ画面と操作を取得。計測ライブラリなしでもFIFO underflows=0 / overflows=0、メニューから終了0、元のFEへ復帰。証拠: `uae-normal-apps-gameplay.png`、`uae-normal-apps-gameplay-result.log`。

既存40個のAppsエントリは最初のバックアップと一致。従来のsource-repair 9入口は前コミット069bd33のmanifestと比較し、名前・ID・起動経路・OPKハッシュが一致。4入口のみ追加された。端末の30/39パッケージもSHA-256一致。SD2は引き続きread-only、CPUは996000 kHz。


## ユーザーによる実機確認（2026-11-18）

ユーザーから以下の7種類すべてについて「動作OK」の報告を受領した。

| OPK番号 | エミュレータ | 実機確認 |
| --- | --- | --- |
| 13 | Handy | OK |
| 18 | Oswan | OK |
| 57 | SMS Plus GG | OK |
| 58 | SMS Plus MS | OK |
| 61 | Unreal Speccy | OK |
| 39 | GnGeo | OK |
| 30 | UAE4All | OK |

manifestの7パッケージ／13入口を `machine-pass-user-confirmed` へ更新し、エミュレータ単位の実機確認結果・日付を記録した。今回の報告では試した個別ROMや操作項目までは列挙されていないため、13入口すべてのROM別試験やステート保存／ロードまで実機確認済みとは扱わない。上記より前の「聴取待ち」などは、機械試験時点の記録である。

導入スクリプトは実機確認待ちと実機確認済みの両方を扱う。既存のハッシュ・fps・画面・音声データ・正常終了・FE復帰の検査は維持。今回は受入れ状態と作業記録のみ更新し、Appsの名称、起動経路、OPKバイナリ、実機で実行中の状態は変更しない。FEの機種別コア経路への組込みは別作業とする。
