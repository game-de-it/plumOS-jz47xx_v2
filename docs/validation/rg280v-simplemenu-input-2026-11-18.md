# SimpleMenuのカーソル飛びを修正（2026-11-18）

## 再現と原因

実機で、入力処理を短時間停止して「下の押下・解放 → 上の押下」を蓄積し、上を離す前に処理を再開した。これは描画や読み込み中に複数入力がたまる状況を再現するもの。

旧版は`SDL_PollEvent`で取り出したキーではなく、`SDL_GetKeyState`が示す現在の全キー状態を`performAction`へ渡していた。SDLがまとめてイベントをポンプすると、この状態はイベント列の末尾の状態になる。

実際の旧版ログでは、下のイベント`key=274`で`up=1 down=0`となり、設定カーソルが0→8へ逆方向に移動。続く上のイベントで8→7へ動いた。本来は下→上なので0→1→0になるべきだった。

根拠はGit管理外の `output/rg280v-simplemenu/cursor-baseline-trace.log` と `cursor-baseline-queue.png`。

## 修正

`PLUMOS_RG280V`ターゲットだけで、入力をイベント順に管理する。

- 押下・解放を独自の配列へ順番に反映し、そのイベントのキーだけを操作関数へ渡す。
- SimpleMenu本来の組み合わせ操作用に、Bの押下状態は修飾キーとして引き継ぐ。
- SDLの自動リピートを無効化し、重複したkeydownも無視する。十字キーだけを初回250ms、以降80ms間隔で連続移動させる。
- 描画が遅れても、遅れた分のリピートをまとめて実行しない。解放時やフォーカス喪失時はリピートを停止する。
- A等のボタンを長押ししても、決定が繰り返されて次画面の項目を実行しない。

`PLUMOS_SIMPLEMENU_INPUT_TRACE=1`のときだけ、入力イベントと操作後の状態をstderrへ記録する。通常のApps起動では無効。共通SDL、エミュ本体、テーマ素材、物理ボタンの割当は変更していない。

## 実機の回帰試験

`scripts/check-rg280v-simplemenu-cursor.py`で実際のGPIO入力を再生。HOMEは`/tmp/plumos-simplemenu-input-check`へ隔離し、利用者のテーマ選択・お気に入り・一覧位置を試験データで上書きしない。

| 試験 | 修正版の結果 |
|---|---|
| 処理待ちの下→上 | カーソル0→1→0 |
| 処理待ちの下6回 | 1→2→3→4→5→6、取りこぼし・飛び越しなし |
| 下を保持中にX | 下の1回だけ移動、Xのイベントでは移動しない |
| 下を650ms保持 | 6回移動。最初の待ち257ms、以後81/80/80/81ms |
| 解放後250ms待機 | 追加移動なし |
| Xを650ms保持 | keydownの処理は1回だけ |
| B＋下 | ROM一覧のまま次の機種へ1回移動 |
| 機種選択でAを650ms保持 | ROM一覧へ1回だけ入る。ゲームを勝手に起動しない |

上表は、解放後の停止を長押し試験に含めた計7ケース。結果とイベント列は `output/rg280v-simplemenu/input-check/results.json` と `events.log` に保存。

通常のplumOS Appsからも起動し、GnGeoのゲーム起動、SELECT＋STARTからの終了、SimpleMenuへの復帰を確認した。改修前の実行ファイルと利用者のlast_state.savは `/media/data/plumos/backup/simplemenu-input-20261118/` に保存した。

ビルド手順は従来通り `scripts/build-rg280v-simplemenu.sh`。実機試験はSimpleMenuを終了してから次を実行する。

```sh
python3 scripts/check-rg280v-simplemenu-cursor.py
```

修正版を通常のApps経由で起動した状態にして、利用者に実際の操作感の確認を依頼している。
