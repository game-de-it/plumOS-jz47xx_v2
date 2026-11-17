# 起動不可OPKの追加ソース修正（2026-11-18）

前回の目視候補8入口を維持し、EasyRPG / OpenBOR / GnGeo / ScummVM / UAE4All / Unreal Speccyの6実装について、固定コミットからSoft-floatでビルド・隔離OPK化して追試した。この文書は全62項目の修正完了を意味しない。今回の追加候補はまだ0件。起動ロゴ・メニュー・イントロのSDL更新回数を本編の合格FPSとして数えない。

## 修正内容と現在の到達点

| 実装 | 修正・構成 | 実機の結果と未解決点 |
| --- | --- | --- |
| OpenBOR #17 | 廃止されたSDパスの走査を避け、`closedir(NULL)`を回避。Paks / Saves / Logsを実際の作業ディレクトリから解決。画面モード変更でtexture→renderer→windowの順に解放し、新windowで作り直す。SDL2_gfxの必要部分も同じABIで再ビルド | Crisis EvilとRushing Beatの開始メニューまで表示。Rushing Beatの有効計測は約18更新/秒で音声無音。この画面の数値をゲーム性能の上限とは断定しない。Apps追加なし |
| GnGeo #39 | 古い汎用Makefileを現行の埋込driver配列へ合わせ、host用コード生成器のSDLヘッダを修正。拡張子なし引数のNULL参照、skinロード失敗時のNULL参照、メモリ読取りのポインタ変数アドレス誤参照を修正。親BIOS zipをSD2の実ROMディレクトリへ配置 | Art of Fighting 1/2のROM・BIOS読込みを通過するが、GEN68kのinvalid instructionで子プロセス1。ローダーGUIのFPSが50を超えた試行も本編の合格としていない。CPUコア互換性の調査が必要 |
| ScummVM #56 | v2.2.0のSCUMM/Skyを再ビルド。旧OPKのpluginを外し、必要なlibmadをOPK内へ同梱。START＋SELECTをmain menuイベントへ変更 | Monkey Island 2の正しいイントロ画面と変化するPCM出力、ALSAエラーなしを確認。約6更新/秒はこのイントロの描画頻度であり、処理能力不足と断定しない。本編・修正後メニューと正常終了は未完了。全エンジン対応ではない |
| UAE4All #30 | GCW0版を現SDKで再ビルドし、private HOMEにSD2上のKickstartを参照させる | 起動処理は進むが画像が崩れ、音声無音。本編50 FPS以上未確認。追加なし |
| Unreal Speccy #61 | ソースが入手できたGCW0版0.0.59を再ビルド。START＋SELECTの即終了をメニュー表示へ変更 | 10th Frameのタイトルからボウリングのデモ画面へ進み、約59〜60更新/秒、PCM変化・クリッピング0・ALSAエラー0。START＋SELECT → メニュー → Quitの実終了0・FE復帰も確認。取得した本編はDEMO表示で、実プレイ入力の確証がないため追加保留。元のカタログ0.0.86.12と同じ版ではない |
| EasyRPG #10 | Player 0.6.2.3 / liblcf、pixman、固定小数点speexdspを再ビルド。SDKのmpg123 / sndfileをOPK内へ同梱。Aを決定、Bをキャンセルへ対応。保存先をSD1のprivate HOMEへ分離 | ゲーム構成を読み込めるがMP3読込みエラー後にSIGSEGV・実終了139。停止命令を採取し、`speex_resampler_skip_zeros(NULL)`と特定。作成失敗の検査、MP3形式取得エラー処理、seek失敗伝播を追加して再試験。音声正常がまだ未確認なのでApps追加なし |

これらは専用試験用OPKであり、通常FEのコアや本体共有ライブラリを置換していない。CPUは996,000 kHzのまま。カーネル、スリープ、電源、既存の受入れ済みエミュは今回の変更対象外。

## 計測と転送の修正

- SDL2でSDL1用`SDL_PeepEvents`のシグネチャを介入させない専用の計測ライブラリを追加した。SDL1とSDL2では引数の数もイベント構造も異なる。SDL2計測では入力イベントへの介入を外し、`SDL_RenderPresent`と`SDL_OpenAudioDevice`経由の画面・PCMを取得する。SDL2専用版より前の試行の入力挙動を合否根拠にしない。
- `audit-rg350-opks-device.py --health-library REMOTE_PATH`で計測ライブラリを明示できる。既定値は従来のSDL1版で、通常Appsには計測ライブラリを入れない。
- Git管理済みの古いhard-float `.o` を含むOpenBORソースは、全対象`.o`を削除してから再コンパイルする。最終ELFのSoft float表示だけで混在ABIがないと判断しない。
- EasyRPGのゲーム全体722ファイルをSD2へ転送し、全ファイルSHA-256を照合。ROMだけを取り出した不完全なデータをゲームとして扱わない。追加ゲーム、BIOSは引き続きSD2。保存・ログ・キャッシュはSD1へ置く。
- 試行中にADBのTCP接続が消えた記録は端末クラッシュと区別する。接続復旧後のuptimeが連続していること、FEの復旧を確認した。foregroundの専用ADBサーバで再試行した。無通信試行の数値は合否に使わない。

## 再現と証拠

ソースと依存関係のrevision / archive SHA-256、ビルド条件、private library一覧は `assets/rg280v-apps/source-repair-profiles.json` に保存。修正は `patches/rg280v-{openbor,gngeo,scummvm,unrealspeccy,easyrpg}-opk-*.patch`。ビルドされたOPKのSHA-256、実行バイナリSHA-256、パッチSHA-256は `output/rg280v-apps/source-repair-opks/NN.json` に記録。

```sh
python3 scripts/build-rg280v-source-repair-opks.py 17 39 56 61 10 30
scripts/build-rg280v-standalone-health.sh
# SDL2 OPKの追試時のみ、SDL2用の.soを専用試験ディレクトリへ転送し、
# audit-rg350-opks-device.py --health-library で指定する。
```

主な生ログとDRM画像（Git管理外）:

- `output/rg280v-apps/rg350-device-audit-openbor-sdl2-rushingbeat-20261118/`
- `output/rg280v-apps/rg350-device-audit-gngeo-fetch-fixed-20261118/`
- `output/rg280v-apps/rg350-device-audit-scumm-source-libs-20261118/`
- `output/rg280v-apps/rg350-device-audit-unreal-late-input-20261118/`
- `output/rg280v-apps/rg350-device-audit-easyrpg-libs-input-20261118/`
- `output/rg280v-apps/rg350-device-audit-easyrpg-crash-location-20261118/`
- `output/rg280v-apps/rg350-device-audit-uae-source-first-20261118/`

openMSXはTclのprivate cross-buildまで進めたが、エミュレータ本体のビルド・動作修正は未完了であり、上の6実装の実機試験件数へ含めない。XMAME、Game & Watch等の残件も修正完了とはしていない。
