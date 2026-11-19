# RG300Xの全FEエミュ経路の確認

RG300Xの実機設定にある26機種・58経路を対象にした。先行検証9経路に加えて、残り49経路をSD2上の代表ROMで起動し、24件を追加で再試験した。機種名をDTで照合し、SD2の読み取り専用マウントを維持した。

各短時間試験ではSD2を検索して機種別キャッシュを更新し、FEが使用する起動処理に対象プロファイルを指定した。起動中の画面を2枚とSELECT＋START後の画面を取得し、SDLの描画更新とPCMを採取した。通常終了が成立しない試験は対象プロセスを停止してFEを再起動した。表の「通常Exit」は計測中のエミュレータの終了を示す。先行検証で同じFEプロセスへの復帰まで確認した経路はその旨を記載した。

FPS欄は短い計測窓の終盤値。「更新」はモード遷移や複数描画によって60を超えた呼び出し数を示す。PCMの信号はソフトウェアで測定した。スピーカーでの音質確認は「本体確認済み」と記載した経路に限る。タイトル・デモ・ロード画面の数字もあるため、表の到達場面と合わせて読む。

先行結果の詳細は [代表経路の記録](rg300x-games-2026-11-19.md) と [FCEUX 2.2.3の記録](rg300x-fceux223-mode-check-2026-11-19.md) にある。計測ログとキャプチャはGit管理外の `output/rg300x-all-games/` に保存した。

| 機種 | 経路 | 代表ROM | FPS目安 | PCM／聴取 | 到達場面と終了 |
| --- | --- | --- | ---: | --- | --- |
| nes | standalone:fceux | Super Mario Bros. | 58.7 | 信号あり | メニュー表示。試験用停止（先行確認） |
| nes | picoarch:fceumm | Super Mario Bros..nes | 59.0 | 信号あり | World 1-1。通常Exit |
| nes | picoarch:nestopia | Super Mario Bros..nes | 59.0 | 信号あり | World 1-1。通常Exit |
| nes | picoarch:quicknes | Super Mario Bros. / 悪魔城伝説 | 59.5 | 信号あり | 通常Exitと同じFEへの復帰（先行確認） |
| nes | standalone:fceux223 | Super Mario Bros. / Baseball / 悪魔城伝説 | 約60 | 本体確認済み | 通常Exitと同じFEへの復帰（先行確認） |
| sfc | standalone:pocketsnes | Super Mario World - Super Mario Bros. 4.sfc | 60.0 | 信号あり | タイトル→プレイヤー選択。試験用停止 |
| sfc | picoarch:snes9x2005 | Super Mario World - Super Mario Bros. 4.sfc | 59.4 | 信号あり | タイトル→プレイヤー選択。通常Exit |
| sfc | picoarch:chimerasnes | Super Mario World | 59.8 | 信号あり | 通常Exit（先行確認） |
| sfc | picoarch:snes9x2005_plus | Super Mario World - Super Mario Bros. 4.sfc | 59.0 | 信号あり | タイトル→プレイヤー選択。通常Exit |
| gb | standalone:gambatte | Super Mario Land | 59.7 | 信号あり | メニュー表示。試験用停止（先行確認） |
| gb | picoarch:gambatte | Super Mario Land [V1.1].gb | 60.0 | 信号あり | World 1-1。通常Exit |
| gb | picoarch:gearboy | Super Mario Land [V1.1].gb | 57.1 | 信号あり | World 1-1。通常Exit |
| gb | picoarch:vbam | Super Mario Land [V1.1].gb | 59.0 | 信号あり | World 1-1。通常Exit |
| gb | standalone:gambatte2020 | Super Mario Land [V1.1].gb | 59.7 | ほぼ無音 | World 1-1。音量不足とメニュー要確認。試験用停止 |
| gb | standalone:ohboy | Super Mario Land [V1.1].gb | 59.2 | 信号あり | World 1-1。試験用停止 |
| gbc | standalone:gambatte | Akumanor Gaiden DX v1.0.gbc | 59.7 | 信号あり | タイトル。試験用停止 |
| gbc | picoarch:gambatte | Akumanor Gaiden DX v1.0.gbc | 59.8 | 信号あり | タイトル。通常Exit |
| gbc | picoarch:gearboy | Akumanor Gaiden DX v1.0.gbc | 58.1 | 信号あり | タイトル。通常Exit |
| gbc | picoarch:vbam | Akumanor Gaiden DX v1.0.gbc | 55.8 | 信号あり | タイトル。通常Exit |
| gbc | standalone:gambatte2020 | Akumanor Gaiden DX v1.0.gbc | 59.7 | ほぼ無音 | タイトル。音量不足とメニュー要確認。試験用停止 |
| gbc | standalone:ohboy | Akumanor Gaiden DX v1.0.gbc | 60.0 | 信号あり | タイトル。試験用停止 |
| gba | standalone:regba | Goodboy Galaxy | 55–59 | 本体確認済み | 通常Exit（先行確認） |
| gba | picoarch:gpsp | goodboy.gba | 56.3 | 信号あり | イントロ。通常Exit |
| megadrive | standalone:picodrive | Bare Knuckle | 60.0 | 信号あり | メニュー表示。試験用停止（先行確認） |
| megadrive | picoarch:picodrive | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 60.0 | 信号あり | タイトル／選択。通常Exit |
| megadrive | standalone:genesisgx | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 更新 78.0–84.4 | 信号あり | 黒い遷移→表示あり。試験用停止 |
| mastersystem | standalone:picodrive | Wonder Boy 3.sms | 60.0 | 無音区間 | ゲーム選択。試験用停止 |
| mastersystem | picoarch:genesis_plus_gx | Wonder Boy 3.sms | 60.0 | 無音区間 | タイトル。通常Exit |
| mastersystem | picoarch:picodrive | Wonder Boy 3.sms | 60.0 | 無音区間 | ゲーム選択。通常Exit |
| mastersystem | picoarch:gearsystem | Wonder Boy 3.sms | 59.0 | 無音区間 | タイトル。通常Exit |
| mastersystem | standalone:smsplusms | Wonder Boy 3.sms | 更新 60.1–66.2 | 無音区間 | ゲーム選択。試験用停止 |
| gamegear | standalone:picodrive | Puyo Puyo.gg | 60.0 | 信号あり | モード選択。試験用停止 |
| gamegear | picoarch:genesis_plus_gx | Puyo Puyo.gg | 60.0 | 信号あり | モード選択。通常Exit |
| gamegear | picoarch:picodrive | Puyo Puyo.gg | 60.0 | 信号あり | モード選択。通常Exit |
| gamegear | picoarch:gearsystem | Puyo Puyo.gg | 59.0 | 信号あり | モード選択。通常Exit |
| gamegear | standalone:smsplusgg | Puyo Puyo.gg | 更新 60.1–65.9 | 信号あり | モード選択。試験用停止 |
| segacd | picoarch:picodrive | Fatal Fury Special (Europe) (Demo).chd | 50.0 | 信号あり | 欧州版BIOS起動画面。通常Exit |
| pcengine | picoarch:mednafen_pce_fast | Air Zonk | 59.7 | 信号あり | 通常Exit（先行確認） |
| pcengine | picoarch:mednafen_supergrafx | AirZonk_U.pce | 60.0 | 信号あり | 難易度選択。通常Exit |
| pcengine | standalone:temper | AirZonk_U.pce | 59.3 | 信号あり | 難易度選択。試験用停止 |
| supergrafx | picoarch:mednafen_supergrafx | 1941 - Counter Attack (Super Grafx) (J).pce | 59.5 | 信号あり | ゲーム冒頭。通常Exit |
| pcenginecd | picoarch:mednafen_pce_fast | ChouAniki.chd | 56.7 | 無音区間 | ゲームロゴ・演出。通常Exit |
| psx | standalone:pcsx4all | RUNABOUT-2 | 実走未計測 | 実走未計測 | ユーザーが走行・プレイ確認（先行確認） |
| ngpc | standalone:race | Baseball Stars Color (World) (En,Ja).ngc | 60.0 | 信号あり | メンバー選択。試験用停止 |
| wonderswan | picoarch:mednafen_wswan | Puzzle Bobble.ws | 59.0 | 信号あり | ROUND 1。通常Exit |
| wonderswan | standalone:oswan | Puzzle Bobble.ws | 更新 75.4–75.8 | 信号あり | ゲームメニュー。試験用停止 |
| msx | picoarch:fmsx | usas.rom | 60.0 | 無音区間 | ゲームタイトル。通常Exit |
| msx | picoarch:bluemsx | usas.rom | 56.0 | 信号あり・最大振幅到達 | MSX起動画面。通常Exit |
| atari800 | standalone:atari800 | CavernsOfMars.car | 49.8 | 信号あり | タイトル。試験用停止 |
| atari2600 | standalone:stella | Asteroids.bin | 59.8 | 無音区間 | ゲーム画面。試験用停止 |
| pokemini | standalone:pokemini | Pichu Bros. Mini (Japan).min | 更新 76.3–76.4 | 無音区間 | プレイヤー名入力。試験用停止 |
| lynx | standalone:handy | Basketbrawl (1992).lnx | 60.0 | 信号あり | タイトル。試験用停止 |
| cpc | standalone:crocods | Abyssal (2022)(Cabbage Corp).sna | 50.0 | 無音区間 | BASICのSyntax error。試験用停止 |
| zxspectrum | standalone:unrealspeccy | 10th Frame.tap | 59.6 | 信号あり | テープロード→ゲームタイトル。試験用停止 |
| neogeo | standalone:gngeo | aof.zip | 39.4 | 無音区間 | ロゴ・起動画面。試験用停止 |
| neogeocd | standalone:neo4all | Fatal Fury.m3u | 58.9 | 信号あり | レベル選択・操作説明。試験用停止 |
| amiga | standalone:uae4all | Baby Jo.adf | 49.8 | 無音区間 | ディスク起動中。試験用停止 |
| arcade | standalone:fba44 | kungfum.zip | 59.6 | 信号あり | デモ演出。試験用停止 |

最初の49経路はすべて表示を取得できた。25経路はメニュー操作で通常終了し、24経路は計測後に対象を停止した。各試験後のFE再起動を確認した。

- **Gambatte 2020** はGB・GBCとも約59.7fpsで表示された。再試験でも16-bit PCMの最大絶対値が4とほぼ無音で、SELECT＋START後のエミュレータメニューも判別できなかった。
- **Master Systemの5経路** はWonder Boy 3の一部画面で無音だったが、Frontier Forceのタイトル／イントロでは5経路すべてのPCMに信号を確認した。
- **Neo Geo CD** のFatal Furyは操作説明とPCMを採取。以前の異常終了139は今回の短時間再試験では再現しなかった。通常メニュー終了と長時間の安定性は追加確認が必要。
- **CrocoDS** はSNAでBASIC、DSKでディスク一覧まで到達した。RG300Xで本編へ入る操作と音声は確認できていない。
- **表示範囲** は単体PicoDriveのMaster System／Game Gearで小さな中央表示、Stellaの試験では左上寄りの小さな表示を確認した。いずれも640×480の出力に対する描画範囲で、映像出力そのものは継続していた。
- **Sega CD** の欧州版では約50fps、日本版では約60fpsの起動画面を記録した。

## 再試験

| 機種 | 経路 | ROM | FPS目安 | PCM | 到達場面と終了 |
| --- | --- | --- | ---: | --- | --- |
| gb | standalone:gambatte2020 | Super Mario Land [V1.1].gb | 59.7 | ほぼ無音 | World 1-1まで進む。ピーク4が再現し、メニュー表示も判別できず。試験用停止 |
| gbc | standalone:gambatte2020 | Akumanor Gaiden DX v1.0.gbc | 59.7 | ほぼ無音 | タイトル。ピーク4が再現し、メニュー表示も判別できず。試験用停止 |
| megadrive | standalone:genesisgx | jp_jp_Sonic_The_Hedgehog.bin | 更新 60.0–68.6 | 信号あり | タイトル。終盤の窓は60.0。試験用停止 |
| mastersystem | standalone:picodrive | Frontier Force (V1.1).sms | 60.0 | 信号あり | タイトルまたはイントロ。音声を取得。試験用停止 |
| mastersystem | picoarch:genesis_plus_gx | Frontier Force (V1.1).sms | 60.0 | 信号あり | タイトルまたはイントロ。音声を取得。試験用停止 |
| mastersystem | picoarch:picodrive | Frontier Force (V1.1).sms | 60.0 | 信号あり | タイトルまたはイントロ。音声を取得。試験用停止 |
| mastersystem | picoarch:gearsystem | Frontier Force (V1.1).sms | 59.0 | 信号あり | タイトルまたはイントロ。音声を取得。試験用停止 |
| mastersystem | standalone:smsplusms | Frontier Force (V1.1).sms | 更新 60.1–80.0 | 信号あり | タイトルまたはイントロ。音声を取得。試験用停止 |
| segacd | picoarch:picodrive | Night Striker (Japan).chd | 59.5 | 信号あり | 日本版の起動画面。60Hzと音声を確認。試験用停止 |
| pcenginecd | picoarch:mednafen_pce_fast | TwinbeeReturns.chd | 58.2 | ほぼ無音 | ディスクとBIOS読込。黒画面からのゲーム操作は未確認。試験用停止 |
| msx | picoarch:fmsx | usas.rom | 59.1 | 無音区間 | USASタイトルとキーボード入力待ち。試験用停止 |
| msx | picoarch:bluemsx | usas.rom | 59.0 | 信号あり・最大振幅到達 | USASタイトルとキーボード入力待ち。試験用停止 |
| atari2600 | standalone:stella | Centipede.bin | 60.0 | 信号あり | ゲーム画面。SELECTでリセットして発射入力を送信。試験用停止 |
| pokemini | standalone:pokemini | Pokemon Party Mini - Baseline Judge (Europe) (GameCube).min | 更新 76.0–76.3 | 信号あり | ゲーム画面とメニュー。音声を取得。試験用停止 |
| cpc | standalone:crocods | 007 - Live and Let Die (1988)(Domark).dsk | 50.0 | 無音区間 | BASICとディスクファイル一覧。本編未確認。試験用停止 |
| zxspectrum | standalone:unrealspeccy | 10th Frame.tap | 59.1 | 信号あり | ボウリング画面。入力で投球したことは未確認。試験用停止 |
| neogeo | standalone:gngeo | aof2.zip | 60.0 | 信号あり | 冒頭デモ。終盤は約60更新/秒。試験用停止 |
| neogeocd | standalone:neo4all | Fatal Fury.m3u | 58.8 | 信号あり | 操作説明とエミュメニュー。以前の終了139はこの試験時間内に再現せず。試験用停止 |
| amiga | standalone:uae4all | Baby Jo.adf | 50.0 | 無音区間 | ディスク読込。プレイ画面とBGMは未確認。試験用停止 |
| pcenginecd | picoarch:mednafen_pce_fast | GingaFukeiDensetsuSapphire.chd | 57.6 | 無音区間 | SapphireのNOW LOADING。約35秒のPCMが無音。試験用停止 |
| msx | picoarch:fmsx | usas.rom | 59.9 | 信号あり | Yの入力でPEGUのプレイ画面まで進み、音声も取得。試験用停止 |
| msx | picoarch:bluemsx | usas.rom | 58.8 | 信号あり | USASの入力待ち。PCMに信号あり。操作中の音声は未確認。試験用停止 |
| arcade | standalone:fba44 | kungfum.zip | 60.0 | 信号あり | クレジットを入れ、1 PLAYER 1 FLOOR READYへ到達。試験用停止 |
| amiga | standalone:uae4all | Baby Jo.adf | 46.5 | 無音区間 | STARTを押さず約1分待機。ディスク読込から本編へ進まず。試験用停止 |

試験終了時はRG300XのFEが稼働し、確認対象のエミュレータが残っていないことを確認した。SD2は読み取り専用、CPUは996 MHzだった。

## 本体での追加確認と修正

ユーザーはUAE4All、PC Engine CD、CrocoDS、NEO4ALL、FBA44のゲームが正常に動作することを確認した。UAE4Allはロードに時間がかかる。PC Engine CDはSTART、CrocoDSはAを押すとゲームが進む。自動試験の到達場面は上の表に残す。

Gambatte 2020ではユーザーがゲーム中の無音とメニュー操作音を確認した。Gambatte 2020のOPKの起動時に `--resampler 0` を渡した。既存Gambatteと同じ線形リサンプラーで、ゲーム中のPCMの最大絶対値はGB・GBCとも4から30,720に増えた。Super Mario LandとAkumanor Gaiden DXで59.7／59.9fps、96kHzの音声データに信号があり、計測上のクリップ・ALSA書き込みエラーは0だった。修正後、ユーザーが実機でGambatte 2020のゲームが正常に動作することを確認した。

| 経路 | 試験ROM | 640×480出力上の非黒描画範囲（修正前 → 修正後） | 修正後 |
| --- | --- | --- | --- |
| 単体PicoDrive / Master System | Frontier Force | 214×135 → 428×270 | 約60fps、音声データとメニューあり |
| 単体PicoDrive / Game Gear | Puyo Puyo | 160×144 → 320×288 | 約60fps、音声データとメニューあり |
| Stella / Atari 2600 | Centipede | 262×178 → 524×356 | 約60fps、音声データとメニューあり |

同じ場面の取得画像を黒背景と比較した。修正後はいずれも320×240の描画面を640×480に拡大し、ゲームの縦横比を維持する。PicoDriveはSega 8-bit経路で640×480を検出した場合の論理寸法を調整。Stellaは640幅のフレームバッファで内部描画を320×240に制限する起動オプションを渡す。RG300Xへ配置した三つのOPKとPicoDrive起動スクリプトはSHA-256を照合した。元ファイルは試験SDの `plumos/backups/rg300x-emulator-fixes/` に保存した。追加試験後は対象プロセスを停止し、FEを復帰した。

ユーザーは単体PicoDriveのDisplay optionsでHorizontal scalingとVertical scalingを個別に調整し、意図した画面サイズにできることを確認した。
