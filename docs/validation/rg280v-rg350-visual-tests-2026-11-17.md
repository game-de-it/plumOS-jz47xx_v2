# RG350 OPK 実機目視比較の準備（2026-11-17）

前回の機械監査で合格にできなかった Atari800、FBA44、Temper について、各3 ROMをRG280Vの `START → Apps` から選べるようにした。通常のFEエミュ登録は変更していない。項目名は `TEST Atari ...`、`TEST FBA ...`、`TEST Temper ...`。

| 候補 | ROM | 前回の問題 |
| --- | --- | --- |
| Atari800 | Caverns of Mars / Miner 2049er / Food Fight | Caverns of Marsは白帯、無音。残り2本は未判定 |
| FBA44 | Kung-Fu Master / Battle Chopper / Ninja Spirit | Kung-Fu Masterは色化け・音声ゼロ。残り2本は未判定 |
| Temper | Air Zonk / Blazing Lazers / Bonk's Revenge | Air Zonkは黒画面。残り2本は未判定 |

AtariとFBAのROMは `<local-path>` から試験用ディレクトリへコピーし、Temperは既存SD2のROMを参照する。旧readline/ncurses/OpenSSL/libaoは `/media/data/local/rg350-visual-tests/lib` だけに隔離し、製品の共通ライブラリには追加しない。FBA44は監査で使った、ROM引数を受ける試験用OPKを使用する。ROM、OPK、旧ライブラリはGitへ含めない。

配置コマンドは `python3 scripts/setup-rg350-visual-tests.py`。各転送後にホストと端末のSHA-256を照合し、Apps設定の9件を読み戻して確認した。FEプロセスが起動中であることも確認した。作業前のApps設定はGit管理外の `output/rg280v-apps/rg350-visual-tests/apps-before.json` に保管する。試験後は `python3 scripts/setup-rg350-visual-tests.py --remove` でこの9項目と試験用ファイルだけを撤去できる。

各項目はFEのAppsから単独起動し、終了時はFEへ戻る。操作不能になった場合はADBから該当プロセスを停止してFEを復旧する。実機目視ではタイトル画面だけでなくゲーム開始後の映像色、音、入力、速度、終了後のFE復帰を記録する。現時点では9候補の実機目視結果は未取得であり、合格判定はしない。
