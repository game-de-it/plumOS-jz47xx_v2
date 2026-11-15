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

FEのPSX既定候補は現行PCSX ReARMedのまま。実用候補にするには、LightrecのMIPS生成コードのクラッシュ解消、またはPCSX4ALLをSoft float ABIでビルドし、実機で映像・音声・FPS・入力・SELECT＋STARTメニュー・FE復帰を確認する必要がある。今回の試験ではユーザーによる実機の音声と操作の確認は行っていない。
