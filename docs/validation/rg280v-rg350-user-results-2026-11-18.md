# OPK候補の実機確認結果（2026-11-18）

ユーザーがAppsの比較候補を実機で確認した結果。今回の報告には個別FPS値はなく、以前の機械測定値を今回の実機測定値として流用しない。

| 候補 | 実機結果 | 扱い |
| --- | --- | --- |
| FCEUX 2.2.3 | 動作OK | 実機確認済み・FE追加候補。既存SA 2.6.6とは別版 |
| Genesis Plus GX | Bare Knuckleで音声異常 | 音声修正が必要。他ROMで正常でも同ROMの問題は残る |
| PokeMini | 動作OK | 実機確認済み・FE追加候補 |
| Race Explorer | 動作OK | 実機確認済み・FE追加候補 |
| CrocoDS | 動作OK | 実機確認済み・FE追加候補 |
| Gambatte | 動作OK | 報告された候補は正常。版を特定せず全配布版へ合格を広げない |
| OhBoy | 音飛びすることがあり、メニューが表示できず終了できない | 音声・メニュー修正が必要 |

端末の比較ログにはFCEUXの3タイトル、Genesis Plus GXの3タイトル、PokeMiniの3タイトル、Race Explorerの3タイトル、CrocoDSの3タイトル、Gambatte 2020の1タイトル、OhBoyの1タイトルが存在した。Gambatte r572u3のGB/GBCは今回のログ一覧では起動を確認していない。ログの存在だけでは各タイトルの合格とはしない。

OhBoyの残存プロセス `ohboy.gcw0` を確認した時点では、カーネルの `drm_atomic_helper_wait_for_vblanks.part.0` で画面更新同期を待っていた。標準ログは `Default Settings restored` とSDL Joystick初期化成功のみで、音声エラーやメニュー操作の記録はなかった。TERMを送り、その後残存していないことを確認してFEを再起動した。最終的にFEプロセスの稼働とOhBoyプロセスの不在を確認した。この時点ではOhBoy本体・Genesis Plus GX本体のソース修正・再ビルドは未実施で、両問題を解決済みとはしない。

後続のソース修正・試験・端末反映は [音声・メニュー修正記録](rg280v-opk-audio-fixes-2026-11-18.md) を参照。両方を再ビルドして比較Appsへ反映し、機械試験を通過。実機聴取での解消は確認待ち。
