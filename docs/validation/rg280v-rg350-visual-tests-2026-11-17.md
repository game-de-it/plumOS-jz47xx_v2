# RG350 OPK 実機目視比較の準備（2026-11-17）

前回の機械監査で合格にできなかった Atari800、FBA44、Temper について、各3 ROMをRG280Vの `START → Apps` から選べるようにした。通常のFEエミュ登録は変更していない。項目名は `TEST Atari ...`、`TEST FBA ...`、`TEST Temper ...`。

| 候補 | ROM | 前回の問題 |
| --- | --- | --- |
| Atari800 | Caverns of Mars / Miner 2049er / Food Fight | Caverns of Marsは白帯、無音。残り2本は未判定 |
| FBA44 | Kung-Fu Master / Battle Chopper / Ninja Spirit | Kung-Fu Masterは色化け・音声ゼロ。残り2本は未判定 |
| Temper | Air Zonk / Blazing Lazers / Bonk's Revenge | Air Zonkは黒画面。残り2本は未判定 |

AtariとFBAのROMは `<local-path>` から試験用ディレクトリへコピーし、Temperは既存SD2のROMを参照する。旧readline/ncurses/OpenSSL/libaoは `/media/data/local/rg350-visual-tests/lib` だけに隔離し、製品の共通ライブラリには追加しない。FBA44は監査で使った、ROM引数を受ける試験用OPKを使用する。ROM、OPK、旧ライブラリはGitへ含めない。

配置コマンドは `python3 scripts/setup-rg350-visual-tests.py`。各転送後にホストと端末のSHA-256を照合し、Apps設定の9件を読み戻して確認した。FEプロセスが起動中であることも確認した。作業前のApps設定はGit管理外の `output/rg280v-apps/rg350-visual-tests/apps-before.json` に保管する。試験後は `python3 scripts/setup-rg350-visual-tests.py --remove` でこの9項目と試験用ファイルだけを撤去できる。

各項目はFEのAppsから単独起動し、終了時はFEへ戻る。操作不能になった場合はADBから該当プロセスを停止してFEを復旧する。実機目視ではタイトル画面だけでなくゲーム開始後の映像色、音、入力、速度、終了後のFE復帰を記録する。配置時点では9候補の実機目視結果は未取得であり、合格判定はしない。

## Atari800の目視結果

ユーザーが3項目を選んだところ、ボタン操作でいずれも終了した。端末の `runs.tsv` ではCavernsが3秒、Minerが3秒、Food Fightが1秒で終了し、全て終了コード10。各 `atari_*.log` は0バイトで、標準出力・標準エラーに説明はない。直後のカーネルログにAtari800のページフォルトやOOMは見当たらなかった。OPKのdesktopは `Exec=atari800 %f` であり、ROM引数の指定はある。OPK付属の説明書ではSELECTがメニュー、Aが発射、十字キーが移動となっているが、このRG280V試験ではその動作まで進めていない。3 ROMで同じ終了コードのため、ROM個別の合否を判断せず、起動・入力経路を調べる。

## FBA44の目視結果と後続ビルド

ユーザーはKung-Fu Masterで音声は正常だが、入力が効かず画面が二重に崩れると報告。DRM画像でも320×240の全面に走査線・色化け・重複表示を確認した。試験用ROMはOPKに読み込まれていた。旧FBA44の問題なので他の2 ROMだけで合格判定しない。TERMに応答しなかったため該当 `fbasdl.dge` にKILLを送り、FEのApps画面へ正常復帰した。キャプチャはGit管理外の `output/rg280v-apps/rg350-visual-tests/fba-kungfum-user-view.png`。

配布元 `plrguez/fba-sdl` の `r19_2021-10-18-.44_od_beta-fix-06` はRG280Vを対象にし、先行修正にKung-Fu Masterの256×246解像度と表示面の扱いが含まれる。ただし配布バイナリのELF属性はMIPS hard floatで、このplumOS環境のsoft float ABIに一致しない。13.5 MBのOPKは比較用に隔離して保存し、通常のFEには登録しない。ソースは取得済みで、soft float再ビルドと入力割当の確認が必要。

旧FBA44の `FBA_HWSCALING` を0から1にした短時間試験でもKung-Fu Masterの崩れは残った。設定は元に戻した。`scripts/probe-rg280v-fba-frame.c` でSDL_Flipの直前に320×240、RGB565、pitch 640の画素を保存したところ、既に画面が崩れていた。したがってこの画面の崩れはDRM転送後ではなく旧FBA44側の描画経路で発生する。

残り2本を同じ旧FBA44で8秒ずつ機械試験した。Battle Chopperの画面は目視で正常なランキング画面を表示したが、計測時は約30 FPS。Ninja Spiritのタイトル画面も目視では色・配置とも正常で、計測時は約19 FPS。どちらもゲームプレイ中の速度、音、操作は未確認。Battle Chopper試験後にFE自動復帰が一度失敗したため `S95frontend restart` で復旧し、FE稼働を確認した。両スクリーンショットはGit管理外の `output/rg280v-apps/rg350-device-audit-fba-{bchopper,nspirit}-visual/34.png` に保存した。

## ソースからの修正試験

試験用Appsだけをソース版へ切り替えた。通常のFEエミュ経路は変更していない。ROM、OPK、スクリーンショット、ビルドツリーは引き続きGit管理外。各OPKはMac側とRG280V側のSHA-256一致を確認した。

| 候補 | ソース・コミット | RG280V向け処理 | 実機で確認できたこと | 残る確認 |
| --- | --- | --- | --- | --- |
| FBA .44 | [plrguez/fba-sdl](https://github.com/plrguez/fba-sdl) `9448a9c6f1040ad8ec204b5e9cb83e25574ac0c8` | MIPS soft floatで再ビルド。配布OPKの`fbasdl.dge`のみ交換 | Kung-Fu Masterのタイトルとゲーム中の画面が正常。旧版でSDL画素の時点から出ていた重複・色化けが消失。ゲーム中画面まで進み、プロセスは45秒の計測時間内で動作 | 実機で音声・操作・終了、他2 ROM、FPS |
| Atari800 4.1.0 | [atari800/atari800](https://github.com/atari800/atari800) `d9d9ad1b47169d30b41e90b709dfc437844c9b9c` | `patches/rg280v-atari800-input.patch` で十字キー・A・START・メニュー入力をRG280Vに割当。生16 KB ROMを標準16 KB型のCART形式へ変換 | Caverns of Marsがタイトルからゲーム中へ進み、START・A・右入力後も終了せず動作。旧OPKはボタン押下後に終了コード10だった | 実機で音声・メニュー・終了、他2 ROM |
| Temper | [gameblabla/temper](https://github.com/gameblabla/temper) `a6c9ef2c5d1a086c22eb51980e07f3c38d0b42ae` | soft floatで再ビルドし、GCW専用IPU経路を外した比較版を作成 | Blazing Lazersのタイトル、Air Zonkの約25秒後のタイトルが表示。Air Zonkの初期黒画面は同じROMのPicoArchでも再現し、導入演出の途中だった | ゲーム中の映像・音声・操作・終了、IPUあり版との比較 |

FBAの配布バイナリはhard float ABIだったため、そのまま使用しない。ビルドスクリプトは `scripts/build-rg280v-fba-softfloat.sh`。ソースと依存ヘッダーは `output/rg280v-apps/rg350-visual-tests` 内に隔離し、ソースタグに含まれるKung-Fu Masterの256×246描画処理を取り込んだ。ビルド時のpng++は0.2.9、AVIRは2.5、JSONは3.9.1、BoostヘッダーはDebian bookwormの1.74を利用した。`Tag_GNU_MIPS_ABI_FP: Soft float`をELFで確認した。

Atari800の生ROMはカートリッジ種別が不明なため選択画面を出す。Caverns of MarsとMiner 2049erの16 KB試験ROMは、標準16 KB型を示す16バイトのCARTヘッダーを付けた。元ROMは変更していない。Food Fightの32 KB ROMには型を推測で指定していない。変換と試験用OPKの転送は `scripts/setup-rg350-visual-tests.py` で再現できる。

Temperの比較ビルドは `patches/rg280v-temper-noipu.patch` を使用した。Air Zonkの黒い導入場面はPicoArchとTemperの両方で数秒続き、約25秒後にタイトルが表示された。黒画面の単一キャプチャだけで不具合判定しない。IPU設定を外すこと自体の有効性は、この時点では未判定。

Atari800とTemperのパッチは上流ソースとの差分をゼロ行コンテキストで保存した。適用時は各ソースツリーで `git apply --unidiff-zero` を使う。元のソースツリーへ実際に戻せることを `git apply --unidiff-zero --reverse --check` で確認した。

試験OPKのSHA-256はFBA `f4222aad3205054eb777fa3a4a932a3a4eeba45808faa0a5e30f521377f65a49b3d`、Atari800 `2eeb984c95cb4c57fc0096f4d571a95a9e8ceb26a2d199a167a9a930793020bc`、Temper `ca599af6011ef011ea1b41a17c4d7f8941f93007d9e7ab222bdc01ecf851d7b9`。試験用Appsの9件を再照合し、FEプロセス稼働を確認した。
