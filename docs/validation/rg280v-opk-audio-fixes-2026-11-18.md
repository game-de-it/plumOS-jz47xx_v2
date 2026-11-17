# Genesis Plus GX / OhBoyの修正（2026-11-18）

ユーザーの実機試験で、配布Genesis Plus GXはBare Knuckleの音に異常、OhBoyは時々音が飛び、SELECT＋STARTでメニューを開けず終了できなかった。既存SAではなく、Appsの比較用OPK 12・49だけを修正した。

## ソースと変更

| 対象 | ソース | 変更 |
| --- | --- | --- |
| OhBoy | https://github.com/hi-ban/ohboy `4720bcf5fbb4d80d85d6f623847d29cefea2cd94` | バッファの生産側をSDL音声ロックで保護。コールバックが要求した長さだけ消費し、不足部分はゼロで埋める。バッファ拡大、ビジーループを待ち時間上限のある1ms待機へ変更、16ビット音声の範囲を超える値をクランプ。SELECT＋STARTを常時有効化し、電源キーのメニュー利用を外す。メニュー案内も同時押しへ変更。メニュー移行時の不要な160×120モード変更を除去 |
| Genesis Plus GX | https://github.com/ekeeke/Genesis-Plus-GX `2499cd3e3d1d8b7d0130d8b2825adb4cc608b2c0` | コールバックでの音声の塊の間引きを除き、要求バイト数だけ順に消費。不足部分をゼロで埋め、残りの移動に重複領域対応のmemmoveを使う。生産側にバッファ容量と待ち時間の上限を追加。SDL音声指定構造体を初期化。保存パス関数がローカル配列への無効なポインタを返す不具合とgzFileのポインタ型も修正。MD背景画像の大文字小文字の不一致によるメニュー終了を修正 |

上記はソースで確認した問題と対策であり、ユーザーが聞いた異常の原因を全て特定したという意味ではない。GCW0用コードを現在のsoft floatユーザーランド向けにビルドした。ビルドスクリプトは `scripts/build-rg280v-opk-audio-fixes.sh`、差分は `patches/rg280v-ohboy-audio-menu.patch` と `patches/rg280v-genesis-gx-audio.patch`。スクリプトはソースコミットを照合してパッチ適用を検査する。

## 機械試験と端末反映

OhBoyのSuper Mario Landは音声コールバックに非ゼロPCMがあり、採取区間のクリップ率は0%。ゲーム中の画面提示は約58〜60回/秒で、メニューに移ると計測値が下がる。SELECT＋STARTメニューの取得画像を確認した後、Aでゲームへ戻り、再度SELECT＋STARTでメニューを開けた。最後に上入力でQuitを選びAで終了し、OhBoyプロセスがなくなったことを確認してFEを起動した。画像・ログはGit管理外の `output/rg280v-apps/ohboy-fixed-menu-reopen.png` と `rg350-device-audit-ohboy-audio-fixed/` に保存。

Genesis Plus GXのBare Knuckleは、30秒のキャラクター選択までの試験で画面提示が約59.9〜60.1回/秒、採取PCMのクリップ率0%、音声信号あり。画面取得ではキャラクター選択画面が正常に表示された。続いて45秒の試験では本編へ進め、約59.9〜60.0回/秒、音声信号の継続を確認した。画面取得はステージ1の正常な本編画像だった。最後にSELECT＋STARTメニューを表示し、Aで復帰、再度メニューを開いてQuitを選ぶとプロセスが終了した。FEを再起動し稼働を確認。取得画像は `output/rg280v-apps/rg350-device-audit-genesis-audio-fixed-game/12.png` と `genesis-fixed-menu2.png`。これはゲーム本編の全場面や実機の音質の合格を意味しない。

修正版を端末の `/media/data/local/rg350-rom-candidates/opk/{12,49}.opk` に転送し、ハッシュを照合。旧版は同じディレクトリの `12-original.opk`、`49-original.opk` に保存した。Appsの同じ3 ROMを修正版で試せる。再配置スクリプトも修正版を使うよう更新した。

| OPK | ホスト・端末で一致したSHA-256 |
| --- | --- |
| OhBoy | `507b2c23c4890424a0850ec1d35a1af8a2509d99366eb33f2e2b431c718a1e88` |
| Genesis Plus GX | `5ab02f0968008351c01123ec932474fa9246bd76c8a4892a47729e445511884b` |

実機スピーカーでの音飛び・異音の解消はユーザー確認待ち。ソースから再ビルドしたため、他のROMの映像・音・入力・終了も同じAppsから確認する。

## Genesis Plus GXの低速化とALSA直接出力への変更

最初のSDLバッファ修正版で、ユーザーがGenesis Plus GXの動作が異常に遅いと報告した。実行中のCPUは996 MHzで、ログに `ALSA write failed (unrecoverable): Input/output error` が記録されていた。SDL音声出力が停止し、生産側のバッファが満杯になった後も追加した待機処理が各フレームで最大200 ms待つため、低速化を起こした。短い画面提示FPS測定だけでこの後発の不具合を検出できていなかった。

Genesis Plus GXのSDLコールバック方式を撤去し、ALSA PCMを非ブロックで開いて44.1 kHz・16ビット・ステレオで直接書き込む方式へ変更した。メニュー前後はPCMをdrop/prepareし、出力エラーはrecoverを試し、回復できなければ閉じて最大1秒間隔で再接続する。バッファ空き待ちをエミュレーションループに入れない。OhBoyはこの変更の対象ではない。

Bare Knuckleの診断版を実機で起動し、継続区間では300エミュレーションフレームが約4999〜5010 msで進んだ。ALSA recover発生は0回。非ブロック書き込みで一部サンプルを受け付けない区間があり、サンプル欠落ゼロとはしない。診断版を見たユーザーが「正常動作になりました」と確認したため、同じ版を比較Appsへ反映した。メニューの開閉とQuitによる終了コード0を再確認し、FEへ復帰した。反映後のホスト・端末SHA-256も一致した。

Genesis Plus GXの採用版OPK SHA-256: `75b5ebe30ef1ca858fcd881fadd45430b11def38c97dbc253591ff22bf37e23a`。上表のGenesis Plus GXのSHA-256は撤回したSDL版の履歴であり、現在の採用版ではない。初期の異音・低速化に対する実機確認結果は、このALSA版の結果で更新する。
