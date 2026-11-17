# ROM未指定だったRG350 OPKの再試験

指定NASのROMセットを使用し、以前ROMを指定していなかった項目を再試験した。今回の新しい目視・聴取確認候補は **Stella**。さらに、NEO4ALLはBGM対応のある2020年ソースから試験版を作り、WAV音楽トラックの読み込みと連続PCMを確認した。後者は本体での聴取確認が残る。

## 対象と判定

旧「ROMなし」35項目の内訳は、今回実行した配布OPK27項目、以前確認したAtari800の代替改修版に対応する2項目、確認済みPokeMini 1項目、Race Explorerと本体が完全一致したRace 1項目、ゲーム素材未特定4項目。

今回の証拠ディレクトリには82回の試行がある。再試行、メニュー表示、誤ったROM形式、BIOSをゲームとして選んだ旧試行を含み、82タイトル合格という意味ではない。配布OPK27項目に加え、NEO4ALLの別ソースビルドを比較した。

- 判定基準はゲーム中50 FPS以上、画面の色に明確な異常なし、音声出力に明確な異常なし。最終的な聴取・操作の実機承認とは分ける。
- `fps_window` はSDL画面更新回数。エミュレーション速度そのものとは限らず、メニューや黒画面の更新回数をゲームの合格へ流用しない。
- STARTがメニューを開くStella・ScummVM・Retro8では、単純なSTART連打を取りやめた。StellaはSELECTでReset、AでFireを入力した。
- PCMの形式をS16/U16、S8/U8、両エンディアンへ対応。無符号PCMの0埋めは無音の中心値ではない。非ゼロのpeakだけで音声正常としない。
- `RC=124` は時間制限による試験終了。共有ライブラリ不整合、assert、異常終了、ROM未読込、性能不足を分ける。
- 停止・クラッシュは調査保留であり、恒久的なFE除外を意味しない。

## 新しい確認候補

| エミュ | ゲーム | ゲーム画面更新 | 画面・PCM | 状態 |
| --- | --- | --- | --- | --- |
| Stella 2015 | Asteroids | 約59.9～60.0 FPS | 正常なゲーム画面。非ゼロPCM、clip 0% | 目視・聴取候補 |
| 同上 | Centipede | 約59.7～60.0 FPS | 色付きの本編を確認。非ゼロPCM、clip 0% | 目視・聴取候補 |
| 同上 | Breakout | 約60.0 FPS | 色帯・ボール・得点を確認。非ゼロPCM、clip 0% | 目視・聴取候補 |
| NEO4ALL BGM試験版 | Fatal Fury WAV | 約58.8～58.9 FPS | ゲーム画面、CUE認識、複数WAVトラック切替、連続PCM、clip 0% | 本体聴取待ち |

Stellaは3D Tic-Tac-Toe、Adventure、Adventure IIも約60 FPS。後二者の採取区間は無音だったので、音声確認用にはアクションゲーム3本を追加した。FEのSTART → Appsへ `TEST 28 Stella 1～3` を追加した。正式な機種別エミュ経路は変更していない。

## NEO4ALLの無音対策

ユーザーからMP3版で音が出ないとの報告があった。WAVに変えるだけで解決したとはせず、以下を切り分けた。

1. 配布原版は2019年12月ビルド。参照した派生ソースでは2020年5月にBGM対応が追加されている。原版のメニュー効果音やメニュー70 FPSは、ゲームの音楽・性能合格へ数えない。
2. BGM対応版を `nicodanyan/neo4all` の `407dcb3a46ca326d74f4bde4da1eadc8287be2a4` からビルドした。RG280Vのsoft-float ABI、宣言の不一致、隔離HOME内のBIOS参照を調整した。音楽ファイルのロード失敗もログへ出す。
3. NEO4ALLはISOと同名のCUEを探す。元セットの `Fatal Fury WAV.cue` に対し、試験側で `Fatal Fury.cue` を用意した。
4. さらに `opkrun` がROMへのシンボリックリンクを実体パスへ解決していた。ISOだけがSD2の実体へ移り、隣のCUEを見失っていた。ISO約6 MBをSD1の隔離フォルダへ実コピーし、CUEと同居させた。WAVはSD2へのリンクで読める。
5. 修正後は `Loaded CD Image ... [+cue]` と、`CD Play: ... Fatal Fury 13.wav` / `20.wav` / `04.wav` / `07.wav` / `02.wav` 等を確認。PCMが継続し、ピーク約14,741、clip 0%。本体での音楽聴取は別途確認する。

根拠: [BGM対応コミット](https://github.com/nicodanyan/neo4all/commit/94076dc4c210bb43401aafeb71f42ccbc6f07a5a)、[参照リビジョン](https://github.com/nicodanyan/neo4all/tree/407dcb3a46ca326d74f4bde4da1eadc8287be2a4)。この試験では修正版でのMP3再生までは確認していない。

WAVセット35ファイル、664,479,255 bytesをSD2の新規専用フォルダ `/media/data/sd2/.plumos-rg350-tests-20261118/Fatal Fury WAV` に置き、全ファイルのSHA-256を照合した。既存ROMは変更していない。転送途中のADB切断後は再接続し、読み取り専用へ戻したうえで再開。完了後もSD2は読み取り専用。

最終BGM試験OPKのSHA-256は `79a4ad15f4e76b90216585f18e9ade47902eb1b3927c2ae3d97625a0e7798045`。原版は置換せず、独立した試験版として保持する。

FEのSTART → Appsに `TEST 15 Neo4All BGM: Fatal Fury WAV` を追加。WAV確認はこの入口から繰り返せる。既存のNeo Geo CD経路やその設定は置換していない。

## 配布原版の全再試験結果

以下のFPSは表示地点の値。メニュー・起動中・黒画面は表記しており、性能限界の断定に使用しない。

| No. | エミュ / 素材数 | 結果・保留理由 |
| ---: | --- | --- |
| 01 | 3DOh / BioFury 1 | BIOS・ISOを追加。黒画面、約41～46更新/秒、PCM無音。本編正常未確認 |
| 02 | Arnold / CPC 3 | 内蔵SDL・旧ALSAの初期化エラー。ゲーム開始前。共有ライブラリを追加しても内蔵SDLは置き換わらない |
| 05 | ColecoD / Dam Busters 1 | ゲーム画面約60 FPS。ただしU16 PCMが固定値、正常音声を確認できない |
| 06 | DCaSTaway / ST 1 | Lattice Cはゲームではない。約9.7更新/秒、ゲーム速度評価には使わない |
| 07 | DOSBox / 3 | ZIPを展開しDOS実行ファイルを起動。Alien Breed約23～26、DOOM約4～17、Terminal Velocity約10更新/秒。メニュー・黒画面を含み、全てPCM無音。正常候補にはしない |
| 10 | EasyRPG / 1 | プロジェクト一式を配置。新規ゲーム開始中約50～56 FPS、音声信号あり。その後map0018読み込みでsegfault。修正優先候補だが現状合格ではない |
| 13 | Handy / Lynx 3 | 静的SDLの `No available video device`。本編未到達。ソースからのSDLバックエンド変更は未実施 |
| 15 | NEO4ALL / Fatal Fury 1 | 配布原版はメニュー止まり。BGM対応の別ソース試験版は上記参照 |
| 17 | OpenBOR / 3 | Crisis Evil 1、Dragon Ball、Rushing Beat。PAK一式を渡しても異常終了11。描画・音声正常未確認 |
| 22 | Potator / Supervision 1 | 起動引数・作業ディレクトリを変更してもROMブラウザ止まり、約30更新/秒。ゲーム30 FPSと判定しない |
| 23 | ProSystem / Atari 7800 3 | Asteroids、Basketbrawl、Centipedeで画面約60 FPS。U8 PCMの強い負側オフセットと大きな飽和率があり、音声正常は保留 |
| 28 | Stella / Atari 2600 6 | 上記候補。ゲーム開始操作を修正して約60 FPSを確認 |
| 30 | UAE4All / Amiga 2 | Kickstart・ADFを渡す前段で `Accessing a corrupted shared library`。性能未測定 |
| 31 | VICE / C64 2 | PacmaniaはZIP内の実TAP、InbreadはD64を使用。白帯・黒画面、約27～48 / 約14～15更新/秒、PCM無音。正常な本編FPSとはしない |
| 32 | XMAME / 1942a 1 | インストーラは実行せず、含まれるXMAME 0.69本体を隔離起動。`error invalid value for flicker: 0.0` でゲーム開始前に終了。0.52/0.84は今回未試験 |
| 39 | GnGeo / AOF 1～3 | BIOSとROM ZIPを追加。`Accessing a corrupted shared library` で本編未到達 |
| 41 | Game & Watch / 2 | ZIPからMGWを取り出して再試験。黒画面、描画更新なし、PCM無音 |
| 42 | jzIntv / Lock 'N' Chase 1 | 初回はEXEC BIOS不足。EXEC/GROMを明示して再試験すると異常終了。ROM不足だけが原因ではない |
| 45 | Mednafen multi / 有効ROM 1 | PCE非対応ビルドだったので最初のPCE3件は無効試行。対応するGB ROMでも `pow_test` assertによりゲーム開始前に終了 |
| 47 | Mednafen PC-FX / 1 | SimpleBattleのCUE/BIN一式でも `idii.BitSize == bit_size` assert。性能未測定 |
| 48 | Mupen64Plus / N64 3 | AeroGauge約30、Blastdozer約59、野球約30更新/秒。音声信号はあるが黒画面・描画欠落があり、60に近い値だけで合格にしない |
| 50 | openMSX / 実ゲーム2 | USAS、XGR1Trial。C-BIOS MSX2を指定しても `/dev/snd/seq` がなく終了。旧3本目のDISK.ROMはBIOSでありゲーム数から除外 |
| 55 | Retro8 / PICO-8 3 | 30更新/秒、黒画面、PCM未確認。3本とも `_update60` なし。30という値だけで性能不足とは判定しない |
| 56 | ScummVM / データ一式2 | 当初の約4更新/秒はSTARTで開いたメニューで、ゲーム速度の測定ではない。engine-data・音源・参照先・入力を直した再試験でも異常終了10/11。Baseball 215 MB版は今回未試験 |
| 60 | UAE4All params / Amiga 2 | #30同様に共有ライブラリ不整合。原版の性能は未測定 |
| 61 | UnrealSpeccy / ZX TAP 1 | 黒画面、描画更新なし、PCM無音 |
| 62 | UnrealSpeccy launcher / 同TAP 1 | 同上 |

## 重複・未特定素材

Race #24/#25は本体 `race-gcw0.dge` のSHA-256が双方 `10913c35809fba85edb5ddd8d47df6e6e5e7ff8428b0ad5a6b533f6da245d438` で完全一致。主な差はdesktopの `%f` の有無。#25を別実装の正常候補として水増しせず、既にユーザー確認済みのExplorer経路を使用する。

Daphne、Vectrex、Apple IIgs/KEGS、TIC-80は指定セット内からゲーム素材を未特定。VectrexのシステムBIOSやPocketの設定JSONをゲーム扱いにしない。圧縮アーカイブ全内容まで不存在を証明したものではない。

ROM候補スキャナは `bios/` 以下と既知Atari BIOS名を除外するよう修正した。過去の配置マニフェストは証拠として残し、BIOSをゲームに数えた旧選定結果は今回の合格数へ使用しない。

## 再現・証拠

- `scripts/prepare-rg350-missing-rom-opks.py --pack`: 旧ROM引数・HOME・データ参照の隔離ラッパー。コンテナ内SDKのSquashFSツールを使用。本体ソースの再ビルドではない。
- `scripts/retest-rg350-missing-roms.py`: BIOS・展開済みROM・データ一式を逐次試験し、既存結果から再開する。
- `scripts/retest-rg350-rom-play-inputs.py`: 機種別のゲーム開始操作。Stellaの追加3 ROMも照合して配置。
- `scripts/retest-rg350-scummvm-games.py`: 一式データ、engine-data、シーンスキップでScummVMを再試験。
- `scripts/stage-rg350-neocd-wav-test.py`: SD2への専用WAVセット転送、照合、読み取り専用への復帰。
- `scripts/retest-rg350-neocd-wav.py --prepare-only`: BIOS、同名CUE、実体ISO、音声リンクを用意。
- `scripts/build-rg280v-neo4all-bgm-test.sh`: BGM対応の独立OPKを再現ビルド。
- `scripts/setup-rg350-stella-rom-tests.py`: 既存項目を残してStellaの目視入口3本を追加。
- `scripts/setup-rg350-neocd-wav-test-menu.py`: BGM対応版と同名CUEを使うWAV確認入口を追加。
- 生ログ・DRM画像・JSON: `output/rg280v-apps/rg350-device-audit-rom-retest*/`。集約は `output/rg280v-apps/rom-retest-all-attempts.json`。

今回、新しく本体ソースをビルドしたのはNEO4ALLのみ。他の起動失敗を「ソース対策しても不可」とは扱わない。FE・電源・Sleep・既存エミュのバイナリは変更していない。
