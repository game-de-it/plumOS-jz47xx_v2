# Unreal Speccy実プレイとOPK修正の追試（2026-11-18）

前回からの継続。Unreal Speccyの10th Frameでプレイヤー操作、投球、ピン・スコアの変化、ステート保存／読込み、メニュー復帰・終了を実機入力イベント経由で確認した。デモ画面だけを合格とはしていない。Appsの目視確認候補へ1入口を追加する。スピーカー聴取の最終承認はユーザー確認待ち。

## Unreal Speccyの修正

- START＋SELECTのメニュー操作と、STARTを離した時の仮想キーボード操作に解放通知を対で渡す。UIのautorepeatに押下状態が残り、ダイアログが繰返し開閉する問題を避ける。
- キーボード操作専用ゲームのため`qaop caps`を選択肢に追加。十字キーをQAOP、AをCaps Shiftへ割当てる。ゲーム側のキー入力処理ではShift状態が別途上書きされるため、A押下時は`KF_SHIFT`も設定する。UI内のA決定は従来のfireイベントを使う。
- 設定XMLは専用HOMEへ保存。ステートはROM実体の隣ではなく、専用HOMEの`states/<ROMフルパスのFNV-1a32>.sna`へ保存する。ステートを保存・読み込んでも現在ROMの識別パスを変更しない。SD2を読み取り専用にして両方の操作が可能。
- 作業ディレクトリをHOMEへ変える中間版は、相対参照の`res/rom`が見つからずassertで終了した。最終版はOPKを作業ディレクトリに保ち、設定だけを絶対パスでHOMEへ分離して解消。
- 通常は無効の`PLUMOS_UNREAL_CORE_LOG`を追加。指定時だけZ80フレーム実行数を記録し、SDL描画数と区別する。

## 実機結果

| 項目 | 結果 |
| --- | --- |
| ゲーム本体 | PALの約50フレーム/秒。実プレイ測定の定常区間を加重平均すると49.91 FPS。短い計測窓は約49.5〜50.2等に揺れるため、50.000以上固定との意味ではない |
| SDL画面更新 | 実プレイで約57〜60回/秒。これをZ80の60 FPS実行と混同しない |
| 画面 | DEMO表示でないスコア表、投球モーション、ピン配置・スコア変化、方向操作による変化をDRM取得画像で確認 |
| 音声 | S16 / 44.1 kHz / stereo。PCMが変化し固定DCではない。測定内のクリッピング率0、ALSA書込みエラー0、underrun 0。実スピーカーの聴取承認とは区別する |
| ステート | L保存・R読込みを実機入力経由で確認。生成されたSNAは131,103 bytes。設定XMLのlast_fileはSD2の元TAPのまま |
| メニュー | START＋SELECTで表示、同操作でゲームへ戻る。Quitで子プロセス0・FE復帰 |
| 設定永続化 | 終了後に`joystick=qaop caps`をXMLで確認。再起動した通常版でも投球と終了を再試験 |

最終OPK SHA-256は`d4c0a6649580a4db670a8f80c0c24686879240f796760a35804681ffa5b8bbd0`、実行バイナリは`fe2e114806487b0a38bb822260d3794735ae6c25a165481270c1fc8013e87c5a`。行末形式だけを整理した再パック後もバイナリが同一であることを確認し、再パック版自体を`unreal-release-final-20261118`で再試験した。

最終試験はRで実プレイのステートを読込み、方向キー・Aで操作、L保存、START＋SELECT→Quit。監査の子終了0、ALSAエラーなし、FE復帰を確認。通常Appsの起動に計測用ライブラリと診断環境変数は入れない。

## 目視確認の操作

- Apps: `TEST 61 Unreal Speccy: 10th Frame`
- 起動後にRで確認に使った実プレイステートを読込み可能。Aで投球、十字キーで位置・狙いを調整する。Lでステート保存。
- 最初から始める場合、イントロ画面はY（Space）で進める。STARTで仮想キーボードを開き、OでOpen bowlingを選ぶ。画面に従い操作変更の選択、人数、名前（BはEnter）、K/A/Pの難易度、ゲーム数を入力する。単にSTARTや数字1を繰り返しても途中の英字選択を通過できない。
- START＋SELECTでエミュレータメニュー、QuitでFEへ戻る。電源キーはplumOS専用のまま。

設定とSNAはSD1、元TAPはSD2。試験ROMは元のNASセットと既存SD2の検索では10th Frameのみ確認できたため、3本を確認したとはしていない。ソースはGCW0版0.0.59であり、元カタログ0.0.86.12と同じ版ではない。

開始手順は実機表示に加え、[US Goldの説明書](https://worldofspectrum.org/pub/sinclair/games-info/123/10thFrame.txt)のO/L、難易度K/A/P、投球手順とも照合した。

## 他のOPK

- **GnGeo**: BIOSのreset vectorが誤って`c0000204`になっていた。既にホストの16bit単位で並ぶデータを再度swapする処理を除去し、`00c00402`へ修正。GEN68k側の命令語・即値・分岐／index拡張バイトの読取りも同じ並びへ統一。再試験中であり、Appsへは未追加。
- **UAE4All**: FAME Cコアとstrict-aliasing回避でBaby Joのゲーム画面が正常に出るようになった。旧CPUコアの青色ノイズ表示を解消。STARTはゲーム開始でなくSuperThrottle切替にも使われ、音声停止・大量frameskipを伴うため、START連打の試行を音声・性能の根拠にしない。Frameskip 0でSTARTを押さない比較は約78〜85更新/秒とPCM変化を得たが、速度が正常と認められない。Autoに戻すと約45更新/秒・PCM無音。表示の修正を音声・速度の合格と混同せず、Appsへは未追加。

## 証拠と再現

- `output/rg280v-apps/rg350-device-audit-unreal-qaop-real-play-20261118/`
- `output/rg280v-apps/rg350-device-audit-unreal-release-final-20261118/`
- `output/rg280v-apps/unreal-real-core-fps.log`
- `output/rg280v-apps/unreal-manual-events.jsonl`（手動の実機イベントも時刻・キー・押下時間を記録）
- `output/rg280v-apps/unreal-verified-{right,fire}.png`、`unreal-real-score-after.png`、`unreal-real-menu-after-play.png`
- `output/rg280v-apps/rg350-device-audit-uae-fame-native-20261118/`

`audit-rg350-opks-device.py`は`--environment PLUMOS_UNREAL_CORE_LOG=/tmp/...`でフレーム計測を有効化できる。装置watchdogの上限と揃え、`--seconds`は1〜300に制限した。以前の420秒指定はwatchdogが実行前に2で拒否した無効試行であり、エミュレータの起動不具合に数えない。

UAE4All追試: `uae-fame-sound-no-turbo-20261118`（Frameskip 0）、`uae-fame-auto-normal-20261118`（Auto）。Autoの約45は未達。NO_THREADS音声経路にはPALの312ラインと異なる282ラインのサンプル周期補正と、旧式のバッファ位置補正があり、音声／速度制御を継続調査する。
