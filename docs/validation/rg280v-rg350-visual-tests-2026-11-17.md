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
