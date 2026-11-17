# OPKソース修正と目視確認候補（2026-11-18）

今回の範囲は7実装・8カタログ項目（Arnold、Handy、Oswan、Potator、jzIntv、Mednafen PC-FX、SMS Plus GXのGG/MS版）。うち3実装・4パッケージを目視確認候補とし、Appsへ8タイトルの入口を追加した。全62項目の修正完了ではない。

## Appsへ追加した候補

| Appsの名称 | ROM | ゲーム中のSDL更新 | 終了 |
| --- | --- | --- | --- |
| TEST 13 Handy 1 | Basketbrawl | 約59〜60 FPS | START＋SELECT → Exit → 子プロセス0、FE復帰 |
| TEST 13 Handy 2 | Malibu Bikini Volleyball | 約59〜60 FPS | 同上 |
| TEST 13 Handy 3 | Scrapyard Dog | 約59〜60 FPS | 同上 |
| TEST 18 Oswan 1 | Puzzle Bobble | 約75更新/秒 | START＋SELECT → Exit → 子プロセス0、FE復帰 |
| TEST 57 SMS Plus GG 1 | Columns | 約59〜60 FPS | START＋SELECT → Quit → 子プロセス0、FE復帰 |
| TEST 57 SMS Plus GG 2 | Puyo Puyo | 約59〜60 FPS | 同上 |
| TEST 57 SMS Plus GG 3 | Pengo | 約59〜60 FPS | 同上 |
| TEST 58 SMS Plus MS 1 | Wonder Boy 3 | 約59〜60 FPS | 同上 |

CPUは既存の996,000 kHz / userspaceのまま。CPU周波数・カーネル・電源処理は変更していない。Oswanの約75はWonderSwanのエミュレーション周期に対応する更新であり、液晶が75 Hzで表示するという意味ではない。

ゲーム中の画像を個別に取得して確認した。起動処理とメニューの高速再描画はゲーム中FPSから除外。HandyとSMS Plus GXはそれぞれ3 ROMで本編画面を取得した。OswanのGUNPEYはモード選択、Armored Unitは導入映像までだったため、この2本を本編合格として追加していない。SMSのFrontier Forceも導入画面のみの試行であり、追加していない。

音声はPCMの形式・サンプル数と時間・波形の変化・DC固定・クリッピング・ALSAエラーを機械的に確認。全追加候補で信号が変化し、固定DCとクリッピングを認めない。Handyはゲーム中のALSA underrunが0、音声生成を停止するメニューへ移行した後に1回発生して復旧する記録。OswanとSMS Plus GXは記録内のALSAエラーが0。これは本体スピーカーを聴取した承認ではない。音の自然さと実機操作の最終確認はユーザーによる目視・聴取待ち。

## ソースの修正

- **Handy**: 静的SDLの`No available video device`を避け、RG280Vの動作中SDLと直接ALSAへ再リンク。不要なhugetlb依存と既成PGOを外す。START＋SELECTでメニューを開き、戻った際の押下状態を清掃。START単独のPauseは離した時だけ処理し、電源キーをエミュへ割り当てない。
- **SMS Plus GX**: GCW0用のSDL版をソフトフロートで再ビルド。旧音声処理は`sample_count`の約4倍まで読み、フレーム数をバイト数として転送していた。範囲内のステレオフレームだけを転送し、リングバッファが一杯なら生成側だけを待たせる。音声コールバックは不足分を無音で埋めて待たない。約220更新/秒の速度異常から約60へ復帰。メニューはSTART＋SELECTへ統一し、ゲームへの復帰時に入力状態を清掃。
- **Oswan**: ABIを合わせて再ビルド。音声コールバック内の`SDL_CondWait`を除き、不足分を無音にする。CPU実行量を3.072 MHzに合わせて1/60秒あたり1600×32サイクルへ変更。12 kHzのHBlank音声を44.8 kHzへ正しい比率で変換する。旧1706サイクルと3/4回交互の複製はCPU過速と音声変換の誤差を組み合わせていた。入力イベントは押下・解放とも処理する。
- **jzIntv**: 実行ファイル名末尾の`$`、設定コピーの`char*`/`int`取り違え、設定番号配列の走査幅、NULLファイル参照を修正。straceで`/media/home/.jzintellivision/.filename`への書込み失敗直後のSIGSEGVを特定し、専用HOME内に設定を保存するよう変更。起動クラッシュは解消したが、今回の画面はタイトルで音声無音。ゲーム中の50 FPS以上は未確認なので追加しない。
- **Potator**: 起動引数で設定したGAMEINITを直後にMAINUIへ戻す不具合と、同じバッファを入力・出力にした設定パスの構築を修正。16ビットステレオ音声の右チャンネルを1バイトずらしていた不具合、サンプル数・ポインタの進め方も修正。描画は既にRGB565なのにRGB555として再変換していたため、正しい色とピッチで転送するよう変更。約60 FPS、灰色の正常なタイトルと非ゼロ音声まで確認。本編開始は未確認なので追加しない。
- **Mednafen PC-FX**: 新しいソースを現行ABIで再ビルドし、元の起動時assertを通過。assert自体は削除していない。握り潰されていた例外メッセージをログへ戻し、SDLのモード設定失敗を特定。320×240の画面と、実際のピッチ・有効領域に従う転送へ変更。起動ロゴが表示されるようになったが、その時点でも約15〜17更新/秒。ゲーム中50 FPS以上・音声正常の条件に未到達なので追加しない。
- **Arnold**: 動的SDLで再ビルドし、DSK/SNA/CPRをそれぞれ対応する起動引数へ渡す。AbyssalのタイトルとPCM出力は出るが約26更新/秒。これを本編の性能限界とは断定せず、候補追加は保留。

既存のSAや受入れ済みOPKを置き換えていない。今回の候補は専用の`/media/data/local/rg350-source-repairs/opk/`へ置き、ROMと追加BIOSはSD2のまま、設定・ログはSD1へ分離した。ROMのコピーをSD1へ戻していない。

## 誤判定の防止と再現

opkrunは子の非ゼロ終了コードをそのままプロセス終了値として返し、OS側で下位8ビットだけが見える場合がある。例えばエミュレータ255でもopkrun側は0になった。修正版ラッパーでは`PLUMOS_EMULATOR_EXIT`を記録し、監査側が実際の子の終了値を読む。時間制限124は正常終了と数えない。

OPKのハッシュは試験終了時ではなく転送前に固定し、端末へ転送したファイルとの一致も検査する。Potatorの中間`potator-audio-fixed`試行では転送後にMac側のOPKを再生成したため旧監査のハッシュ記録がずれた。既知の転送版`af5eda6…`へ明示的に訂正し、採用判定から除外した。最終版は`potator-color-fixed`で再試験した。

ソースのURL・コミット・コンパイル条件は`assets/rg280v-apps/source-repair-profiles.json`、採用した試験パッケージのSHA-256とROM・証拠の対応は`assets/rg280v-apps/source-repair-visual-candidates.json`。原版カタログOPKは保存する。

```sh
python3 scripts/build-rg280v-source-repair-opks.py 13 18 57 58
scripts/build-rg280v-standalone-health.sh
python3 scripts/setup-rg350-source-repair-tests.py
```

ビルドには既存の`plumos-jz47xx-build:bookworm`と`plumos-jz47xx-rg280v-build`内のSDKが必要。パッケージ生成時は実行ファイルをstripし、Soft floatであることをreadelfで確認する。計測用ライブラリは監査時のみLD_PRELOADし、通常のApps起動には挿入しない。

生ログとDRM画像は`output/rg280v-apps/rg350-device-audit-repair-final-*/`、追加診断は`*source-trace*`・`*path-fixed*`・`*video-repaired*`・`*potator-color-fixed*`。`smsplus-wonderboy`の最初の最終試行はパスワード画面だったため、Apps判定には本編を取得した`smsplus-wonderboy-game`を使用した。Apps登録前後のJSONと画面は`output/rg280v-apps/source-repair-apps/`。4パッケージとも実際のApps入口から起動し、START＋SELECT → Exit/Quitで終了コード0とApps画面への復帰も確認した。OswanのPuzzle BobbleはROMのチェックサム警告が出るが、本編表示と正常終了は確認できた。この警告だけでROMを不良と断定していない。

EasyRPG、OpenBOR、UAE4All、GnGeo、ScummVM、openMSX、UnrealSpeccy等は今回の修正済み件数に含めない。ソースを取得しただけのものを「修正・検証済み」としない。残る起動問題は継続調査対象であり、異常終了だけを理由に恒久除外していない。

追加の6実装のソース修正・未解決点は [継続作業ログ](rg280v-opk-source-repairs-continuation-2026-11-18.md) に記録。追加候補と起動修正の到達点を区別する。
