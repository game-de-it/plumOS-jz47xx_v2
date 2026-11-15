# RG280V SFCの極端な描画スキップ（2026-11-16）

## 実機で確認した現象

- FEから `picoarch:snes9x2005` でSD2の `Dragon Ball Z - Super Butouden.sfc` を起動。
- 対戦画面でHUDは `FPS: 2.0 (50〜60)`、CPU約38〜40%。音声は正常だが、画面の動きは実際にぶれる・カクつく。ときどき描画が60 FPSに戻り、そのときのCPU表示は約78%。
- PicoArchの `Core Options > Frameskip` をユーザーが `Disabled` に変更すると、同じ実機で60 FPSになった。変更後のDRM画像にも `FPS: 60.0 (60)`、CPU約72%が表示された。しばらくのプレイによる安定性は確認中。

## 原因

PicoArchのHUDは、左の数字をコアから届いた非NULL映像フレーム数、括弧内を主ループの進行回数として集計する。2 FPSの場面でも内部ループは約50〜60回/秒動き、音声も正常だった。単なるCPU能力不足ではない。

取り込んだPicoArchの `overrides/snes9x2005.h` は、コア本来の `Frameskip=disabled` を `auto` へ上書きしていた。Snes9x 2005はAuto時に音声バッファのunder-run通知で映像生成を省き、最大30フレーム続けてスキップできる。実機でFrameskipをOFFにしたA/B結果と一致する。Snes9x 2002にもAutoの既定値上書きがあるため、同じ危険を避けるために両方のPicoArch上書きを`disabled`へ変更した。Snes9x 2005 Plusは既に`disabled`が既定値だった。

修正は `scripts/patch-rg280v-picoarch.py` に入れて再ビルドした。生成バイナリSHA-256は `97e1688f539829a3f449bdb760b3f6fb5b3319ee66f142e45dbba8055bd670c4`。ユーザーがExitでFEへ戻った後、旧バイナリを端末内 `backups/picoarch-before-sfc-frameskip-20261116` へ保存し、旧SHA-256 `66d4a2154cbc7db786a3880947155f6e19344df3fb4a06dcf13e6b968aad4899` を照合。修正版を一時ファイルへ転送・照合し、原子的に置き換えた。FEプロセスの動作は確認済み。修正版でのFE起動・音・操作・終了、およびSnes9x 2002の物理試験は未確認。
