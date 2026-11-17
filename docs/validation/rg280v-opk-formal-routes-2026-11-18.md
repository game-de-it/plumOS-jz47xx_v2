# 確認済みOPKのFE正規経路への登録（2026-11-18）

## 対象

ユーザーの採用指示に従い、確認済み17種類と条件付き採用のFBA44を登録する。SMS Plus GG/MSは個別OPKのため、パッケージは19本。FCEUX 2.2.3、Gambatte 2020、NEO4ALL、FBA44も対象。

- 既存機種への追加: NES/FCEUX 2.2.3、GB・GBC/Gambatte 2020とOhBoy、Mega Drive/Genesis Plus GX、GG/MSのSMS Plus、PCE/Temper、WonderSwan/Oswan。
- 無効だったNGPCをRace Explorerで有効化。以前拒否されたRA経路を戻さない。
- 新設: Atari 800、Atari 2600、Pokémon Mini、Lynx、Amstrad CPC、ZX Spectrum、Neo Geo、Neo Geo CD、Amiga、Arcade。
- 有効だった既存機種の既定エミュ・選択肢は保持。ArcadeはFBA44を既定にした新機種とし、無効の旧FBNeo機種は変更しない。

## 実装

`standalone-opk-routes.json` は採用する元OPKの場所とSHA-256、対応機種を定義する。`build-rg280v-opk-routes.py` は元OPKを再展開し、全desktopが正規ラッパーと任意ROMを使うように変更。各実行ELFのSHA-256は変更前後で一致。エミュ本体の再ビルドや共通SDL/ALSAの置換はしていない。

実行は `plumos-standalone-launch` → `plumos-opk-emulator-launch` → `emulators/opk/*.opk`。HOMEはSD1の `home/opk/EMULATOR`、既存の確認済み設定を初回移行する。NEO4ALLのISO/CUE/M3Uは空白やCRLFを含む名前でも引数を分割しない。BIOSはSD2の `bios/opk/EMULATOR` からSD1の正規BIOS参照へ接続する。ROM/BIOSをOPKやGitへ埋め込まない。

NGPCなど新機種の追加は既存device JSONへマージし、リポジトリの古いJSONでユーザー設定を巻き戻さない。SELECTに表示する名前はFCEUX 2.2.3、Gambatte 2020等の識別できる表記を追加。新機種の画像は既存plumOS-RK2020の共通FE seedをそのまま使用し、アイコンごとのSHA-256を記録する。

SD2には確認済みROMを通常フォルダへコピーする。Neo Geo CDの実データは `roms/neogeocd/.discs/Fatal Fury`、一覧は `Fatal Fury.m3u` の1項目。元のApps/TESTのデータと入口は保持する。コピーは既存ファイルが異なれば停止し、照合後にSD2を元のread-onlyへ戻す。

## 検査状況

- 登録マージの冪等性、既存の有効機種の既定維持、有効機種にRAの混入がないことを確認。
- ラッパーは空白名、ISO、CUE、CRLFのM3U→CUE、通常ROM、未許可ID拒否をホスト上で確認。
- FE本体とtext UIはMIPS soft-float向けにビルド済み。
- 実機へ19パッケージを配置し、全SHA-256をマニフェストと照合。通常ROMフォルダの準備、ライブラリ751件の登録、19経路の実行可能な起動計画を確認。
- 実機JSONへのマージ結果・再適用時の冪等性・既存の有効機種の既定値保持を再照合。既存AppsのJSONも変更前と一致。

採用基準の範囲: FBA44はKung-Fu Master等の正常タイトルでの採用であり、Ninja Spiritの約38fps・音飛びを改善済みとはしない。NEO4ALLは確認済みWAV構成を採用し、未検証のMP3や全タイトルの正常を保証する扱いにはしない。


## 正規経路への移行で見つかった問題と対処

- FCEUX 2.2.3: 既存SA 2.6.6のROM別設定を流用するとvideo初期化でSIGSEGV。straceで設定読み込み直後を特定し、確認済み2.2.3のネイティブ設定を使って正常描画を確認した。移行対象をセーブ・チート等へ限定し、新版の描画設定はコピーしない。既にコピーされた設定は `home/opk/fceux223/.fceux/cfg.inherited-backup` に退避。元SAの設定は保持した。
- GnGeo: BIOS用パスだけでは `neogeo.zip` を発見できず終了。SD1の私有ROM検索ディレクトリへBIOSと選択ROMのシンボリックリンクを作る。実体はSD2に保持し、FEのROM一覧にBIOSを出さない。再パッケージ後も実行ELFは元の確認済みSHAと一致。
- PokeMini: SD2をread-onlyに保つため、EEPROMとステートをSD1の私有 `home/opk/pokemini/saves` へROM別に指定。外部 `bios.min` がなくても同梱FreeBIOSを使う旨をネイティブログで確認。STARTはエミュレートした電源なので起動試験で連打しない。ゲーム画面の表示とSD1上のEEPROM 8,192 bytes・ステート44,142 bytesの作成、正常終了コード0を確認。
- FCEUX 2.2.3・NEO4ALL: 既存の `libfceux-menu.so` をこの2経路だけに適用し、OS用の電源キーを使わずSELECT→STARTの同時押しをSDL HOMEへ変換する。
- FE起動サービス: ADBセッションの終了後にFEが消える場合があり、`nohup setsid` でセッションを分離した。複数の独立ADBコマンドをまたいで同一FEプロセスの生存とゲーム終了後の復帰を確認。
- 画面取得: atomic page flipでは旧CRTCのbuffer_idが古い画像を指す場合があった。表示中planeのfb_idを優先するよう取得ツールを修正。初回のNeo Geo CD取得にKOFの古い画像が写ったため、その画像は成功根拠に使用せず、アクティブplaneでFatal Furyの実画面を取り直した。

## 実機確認の根拠と範囲

正規実行はFEのtext UIと同じ起動計画を使う `verify-rg280v-opk-routes.py` で確認する。これは起動・生存・画面・終了コードの確認であり、短時間の描画回数を新しい全コア60fps判定へ流用しない。画面・音・入力・速度の採用判定は、ユーザーが確認した同一実行ELFの結果を継承する。自動メニュー操作で終了できない場合はアプリPIDだけを停止し、`terminated-after-capture` と記録して通常のメニュー終了と区別する。

- FE実操作でNeo Geo CDの通常一覧→Fatal Furyを起動。ログで新しいSD2ディレクトリ内のISOとWAVを参照し、アクティブ画面でタイトルを確認。
- NEO4ALLは読み込み完了後のSELECT＋STARTでメニューを表示し、Exitで子プロセス・正規ラッパーとも終了コード0を確認。短時間の自動試験ではロード途中で終了させていたため、その137はゲームの自然なクラッシュではない。
- FE実操作でAmigaの通常一覧→Baby Joを起動し、ディスク読込後に実プレイまで進めた。移動入力、SELECT＋STARTメニュー、Exit UAE4ALLから元のFE ROM一覧へ復帰を確認。アプリ終了コード0、音声キューunderflows=0 / overflows=0。読み込み中の黒画面をハングと誤認しない。

詳細なパッケージSHA、ROMコピー照合、起動計画、実機ログ・画像はGit管理外 `output/rg280v-opk-integration/` に保存。

## 復旧先と最終状態

実機の変更前バックアップ: `/media/data/plumos/backup/opk-integration-20261118-075507`。systems/core-overrides/library-index、旧UI、旧起動スクリプト、FEサービスを保存。

ROM/BIOSはSD2、設定・セーブ・ログはSD1。CPUの上限996MHzを維持し、SD2は読み取り専用へ復元。新しいSDカードイメージは作成していない。FBA44の遅いタイトルやNEO4ALLの未検証フォーマットは既知の制約として残す。


全19経路の短時間再試験で起動直後の異常終了は0件。14経路は自動メニュー操作で終了コード0、残る5経路はその操作では終了できなかったためアプリだけを停止した。NEO4ALLは上記の別試験で正常メニュー終了を確認。CrocoDSのAbyssal SNAはこの短時間・追加試験ではBASIC画面までで、本編の再合格には数えない。元のユーザーによるCrocoDS採用確認と区別して記録する。

CrocoDSの007 DSKでは内部ファイル一覧が表示され、選択後にLive and Let Dieのロード画面へ進むことを確認。SNA版の結果を他形式全体の失敗としない。
