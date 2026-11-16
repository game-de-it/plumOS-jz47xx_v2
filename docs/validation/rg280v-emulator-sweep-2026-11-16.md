# RG280Vの想定エミュ確認完了（2026-11-16）

ユーザーはFE登録順に実機で確認を進め、MSXのfMSXとblueMSXの確認後、「想定しているエミュは全て動作確認した」と報告した。各機種の個別結果と修正は `docs/worklog.ja.md` および同ディレクトリの機種別検証記録に残している。

現行FE設定 `assets/frontend/systems.json` は有効15機種、候補37経路。NES、SFC、GB、GBC、GBA、Mega Drive、Master System、Game Gear、Sega CD、PC Engine、SuperGrafx、PC Engine CD、PSX、WonderSwan、MSXが有効。有効候補に `retroarch:` 経路はなく、単体エミュレータまたはPicoArchを使う。FDS、32X、NGPC、FBNeoは性能または表示の実機結果に基づいて無効化済みで、ROMやコアは残してある。

実機の `systems.json` SHA-256は `8c4f65c763f02a10afe687b1b6e0e699cb1ce80a961a9b5b8d2d356864c938ce`。FEプロセス稼働とSD2の読み取り専用マウントを確認した。この完了記録は現在の想定FE構成に対する実機受け入れを指す。全ROMの網羅試験や、各ゲームでの60 FPS達成を意味しない。例えばTobal 2の対戦中60 FPS目標は別の性能課題として残る。
