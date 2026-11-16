# RG350 APPREPOSITORYの単体エミュ調査（2026-11-17）

対象: [RafaVico/RG350_APPREPOSITORY の Emulators](https://github.com/RafaVico/RG350_APPREPOSITORY/tree/master/Emulators)。公開一覧を取得し、現行FEで性能・互換性が課題になった機種を優先して4 OPKを調べた。ROMとOPKバイナリはGitへ入れない。

| 候補 | 配布ファイル | ELFと依存 | 現時点の判断 |
| --- | --- | --- | --- |
| 32X | `picodrive_gcw0(32X).opk` | MIPS32r2、静的リンク、Hard float | 現行OSに旧OPKをそのまま起動するとSDLのマウス初期化で失敗。既存Soft float単体PicoDriveを優先 |
| Neo Geo Pocket | `Race(Neogeo Pocket).opk` | 動的リンク、FP ABIタグなし。SDL 1.2とC++などに依存 | 現行ライブラリとのABI・入力・描画を照合してから移植 |
| WonderSwan | `Oswan_2019-10-09.opk` | 動的リンク、Hard float。`libpng14.so.14`にも依存 | 現行Soft float環境向けの再ビルドが必要 |
| Arcade | `fba44.opk` | 動的リンク、FP ABIタグなし。旧`libcrypto.so.1.0.0`、`libao.so.4`などに依存 | 依存物と性能の再評価が必要 |

現行RG280VのCPUにはFPUがあるが、現行sysrootと単体PicoDriveはSoft float ABI。FPUの存在だけでは動的リンク版のABI互換性は保証されない。RaceとFBA44はFP ABIタグがないのでHard floatと断定しない。

32Xの試験では既存のSoft float単体PicoDriveが `After Burner (Japan, USA).32x` を読み込み、ログに `32X startup` とSH2 DRC初期化を出した。DRM取得画像でも起動映像を確認した。25秒でプロセスを終了してFEを復旧し、FEプロセスの稼働を確認。実プレイ中の映像・音・入力・FPS・FEからの終了は未確認。以前PicoArchの32Xが約30 FPSだったため、32XのFE表示は引き続き無効とし、将来の比較用に `standalone:picodrive` 経路だけ登録した。配布版32X OPKは`SDL_Init failed: Unable to open mouse`で終了したため端末から削除した。

次の判定では同一32X ROMのプレイ場面で、既存単体PicoDriveとPicoArchのFPS・音・操作・メニュー終了を比べる。Neo Geo PocketとArcadeは上流ソースが特定できた候補からSoft float再ビルドを検討し、実機で正常動作した経路だけFEに表示する。
