# RG280V PSX実行方式の調査（2026-11-16）

PSXのFE登録は維持したまま、同じ `sin_FortuneQuest.cue` と配置済みBIOSで実行方式を比較した。ROM・BIOS・OPK・コアダンプはGitに含めない。

| 方式 | RG280Vでの結果 | 判断 |
| --- | --- | --- |
| PicoArch PCSX ReARMed、Lightrec（現行） | 通常起動でも画面表示前に `signal 11`。コアダンプのPC `0x10800e90` はLightrecの生成コード領域内。 | MIPS上で現行JIT経路が落ちる。原因となる命令やLightrec側の欠陥箇所は未特定。 |
| Lightrec、`LIGHTREC_CUSTOM_MAP=0` | 同じく画面表示前に `signal 11`。 | カスタムメモリマッピングを切るだけでは解消しない。 |
| PCSX ReARMed、`DYNAREC=0` | 15秒の計測ではクラッシュせず約14.85 FPS。通常起動では55秒時点にゲームのMEDIAWORKSロゴを描画。 | BIOS・CUE/IMGを読みゲームを進められるが、現状では実用速度に達しない。早期の黒画面だけで失敗と判断しない。 |
| [RG350 PCSX4ALL 1.5のOpenDingux Beta OPK](https://github.com/jdgleaver/RG350_pcsx4all/releases/tag/1.5) | OPKを展開した実行ファイルは起動時に `execvp: Accessing a corrupted shared library`、終了127。 | 公開バイナリは現在のrootfsへ直接持ち込めない。 |

PCSX4ALL公開OPKのELFは **Hard float**、現在のrootfsのuClibcと今回ビルドしたPCSX ReARMedは **Soft float** のMIPS ABIだった。この不一致はOPKがロードできない具体的な理由である。RG280VのCPU自体にはFPUがあるため、CPUの有無の問題とは区別する。[PCSX4ALLのソース](https://github.com/jdgleaver/RG350_pcsx4all)にはMIPSからMIPSへの再コンパイラとRG350用Makefileがある。ただし現在のクロスビルドsysrootにはSDL 1.2のヘッダ・ライブラリが見つからず、ソースの再ビルドには依存物の整備と現行ABI向け設定が必要。

取得した比較用OPKのSHA-256は `24d6db4fa80e352b59a0655f264d488db26d176e291d2ab1a9913b358306da7c`、調査したPCSX4ALLソースのHEADは `ab17108051d2178465da58ce377225575d680e5e`。どちらもGit管理外の `output/` に保管した。

Lightrecのコアダンプで生成コード領域まで実行したことは確認できたが、`si_code=0` のためダンプの `si_addr` を通常のメモリアクセス違反位置として断定しない。`strace`付き実行は12秒で時間切れとなり、通常起動とは挙動が異なった。計測器の有無を混ぜて安定性を判定しない。

上の表は初期調査時点の結果。後続のPCSX4ALL移植とLightrec修正の結果を以下に追記する。

## LightrecのMIPS生成コード修正

PCSX4ALLは独自のMIPS→MIPS再コンパイラを使用し、Lightrecは使用していない。PCSX ReARMed側のLightrecクラッシュを再調査した。再生成したコアダンプでは、MIPS JITコード `0x10800e90` の入口に、プロローグより先に `lw v1,612(v1)` が残っていた。呼び出し元は `v1=0` に設定しており、実際の最初のSIGSEGVはアドレス `0x264` への参照だった。

[TreeFrogUI向けPCSX ReARMed移植のコミット `2f0919a`](https://github.com/tzubertowski/TreeFrogUI_pcsx_rearmed/commit/2f0919a) に同じ故障パターンの修正がある。GNU LightningのMIPS生成器が関数生成を再試行するとき、遅延スロットに保留された命令を消していなかった。`_jitc->inst.pend = 0` を再試行前に入れる最小修正を適用した。併せてLightrecの直接アドレス方式で要求アドレス以外にmmapされても続行しないよう、4か所の匿名マッピングに `MAP_FIXED_NOREPLACE` を追加した。RG280Vのstraceでは生成コード領域 `0x10800000` が要求通り確保された。変更は `scripts/patch-rg280v-pcsx-rearmed.py` に置き、コア再ビルド時にも再適用する。

修正コア SHA-256: `6d9f5f40f966706be876f202d37f1e21ea77c0bab2fe8a69e10545041638feb4`。ADBで同一ハッシュを照合してRG280Vへ配置した。FEのPSX既定候補はPCSX4ALLのまま、PCSX ReARMedを第2候補として維持した。

| 自動実機試験 | 結果 |
| --- | --- |
| `sin_FortuneQuest.cue`、70秒 | watchdog timeoutまでSIGSEGVなし。DRM取得画像でタイトル画面から次の街並みシーンへ進むことを確認。起動後の計測区間で約54～59画面更新/秒。 |
| `Tobal 2 (Japan) (v1.1).cue`、45秒 | watchdog timeoutまでSIGSEGVなし。DRM取得画像でSQUARESOFTロゴから次のムービーへ進むことを確認。 |

この自動試験は起動と画面進行を確認した。音声計測は起動直後約10秒で無音を記録しただけなので、ゲーム内の音声品質は判定していない。後続のユーザー試験では十字キー操作ができた。SELECT＋STARTメニューとFE復帰は確認待ち。ログと画像はGit管理外の `output/rg280v-emulators/` と本体の `Logs/picoarch/` に保存した。

## 画面点滅とFPS表示

ユーザーの実機試験で、PCSX ReARMedは操作できたが画面が点滅した。PicoArchの `pa_video_refresh()` はlibretroの `data == NULL`（前フレーム再利用）を描画しない一方、メインループは毎回 `SDL_Flip()` を呼んでいた。RG280VのSDL二重バッファでは、未描画の裏バッファを表示して点滅する。`scripts/patch-rg280v-picoarch.py` に、最後のゲーム画面を保持し、再利用フレーム時に裏バッファへコピーしてからHUDを描画・flipする処理を追加した。メニューから戻る際も保持画面を使用する。

PCSX ReARMedだけHUDを `FPS: <エミュレーション回数/秒> DRAW: <新規描画回数/秒>` と表示する。静止画を多く使う画面ではDRAWが低くてもエミュレーション速度を別に読める。RG280VのRUNABOUT-2タイトル画面取得では `FPS: 53 DRAW: 7`、CPU `51.1%`。これはタイトル画面の一時値であり、ゲーム中の性能値ではない。修正版PicoArchのSHA-256は `b8979b59a01ccd38f3a6935741ba28c0c58160c9d37b59dc1754b0711c2370ff`。ユーザーは同タイトル画面で点滅が止まり、両数値を読めることを確認した。
