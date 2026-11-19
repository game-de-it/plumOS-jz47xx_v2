# RG350Mの全FEエミュ経路の実機確認

2026-11-19。RG350Mの稼働中のFE設定を取得し、26機種・58経路（単体30、PicoArch 28）を登録順に試験した。DTで本体を識別し、SD2は読み取り専用で使用。開始時のCPUは996 MHz。

FEと同じ起動処理へ経路とSD2上の代表ROMを指定した。各試験で入力を送り、起動中2時点とSELECT＋START後をDRMから画像取得し、SDLの描画更新とPCMを採取した。58経路すべてで初期画面と描画計測を取得し、53経路でPCMに信号があった。PicoArchの28経路はメニューから終了、単体29経路は試験用に停止、NEO4ALLはBus errorで途中終了した。各回の後にplumOS FEのプロセスを再起動して確認した。

表示回数は終盤の計測窓の値。起動ロゴ、設定画面への切り替え、ロード中の値も含む。PCMは計測区間の最大振幅で、スピーカーでの聴感やプレイ中の継続的な音質は未確認。0は採取区間の無音。エミュレータの通常終了と、ネイティブFEを経由した起動・同一プロセスへの復帰は別の試験。

| 機種 | FE経路 | 代表ROM | 終盤の更新窓（回/秒） | PCMピーク | 終了 | 特記事項 |
| --- | --- | --- | ---: | ---: | --- | --- |
| nes | standalone:fceux | Super Mario Bros..nes | 59.8 / 60.4 | 17,889 | 試験用停止 |  |
| nes | picoarch:fceumm | Super Mario Bros..nes | 55.4 / 59.0 | 14,384 | メニュー終了 |  |
| nes | picoarch:nestopia | Super Mario Bros..nes | 59.0 / 59.0 | 28,203 | メニュー終了 |  |
| nes | picoarch:quicknes | Super Mario Bros..nes | 60.0 / 60.0 | 13,255 | メニュー終了 |  |
| nes | standalone:fceux223 | Super Mario Bros..nes | 59.9 / 56.1 | 15,782 | 試験用停止 |  |
| sfc | standalone:pocketsnes | Super Mario World - Super Mario Bros. 4.sfc | 60.0 / 56.4 | 5,716 | 試験用停止 |  |
| sfc | picoarch:snes9x2005 | Super Mario World - Super Mario Bros. 4.sfc | 60.2 / 59.9 | 7,895 | メニュー終了 |  |
| sfc | picoarch:chimerasnes | Super Mario World - Super Mario Bros. 4.sfc | 60.1 / 60.0 | 7,336 | メニュー終了 |  |
| sfc | picoarch:snes9x2005_plus | Super Mario World - Super Mario Bros. 4.sfc | 60.0 / 59.0 | 7,461 | メニュー終了 |  |
| gb | standalone:gambatte | Super Mario Land [V1.1].gb | 59.7 / 59.1 | 30,720 | 試験用停止 |  |
| gb | picoarch:gambatte | Super Mario Land [V1.1].gb | 60.0 / 60.0 | 12,834 | メニュー終了 |  |
| gb | picoarch:gearboy | Super Mario Land [V1.1].gb | 60.0 / 57.1 | 20,956 | メニュー終了 |  |
| gb | picoarch:vbam | Super Mario Land [V1.1].gb | 60.0 / 59.3 | 12,205 | メニュー終了 |  |
| gb | standalone:gambatte2020 | Super Mario Land [V1.1].gb | 59.2 / 59.7 | 30,720 | 試験用停止 |  |
| gb | standalone:ohboy | Super Mario Land [V1.1].gb | 60.0 / 57.6 | 20,352 | 試験用停止 |  |
| gbc | standalone:gambatte | Akumanor Gaiden DX v1.0.gbc | 59.7 / 59.7 | 30,720 | 試験用停止 |  |
| gbc | picoarch:gambatte | Akumanor Gaiden DX v1.0.gbc | 60.0 / 59.9 | 10,859 | メニュー終了 |  |
| gbc | picoarch:gearboy | Akumanor Gaiden DX v1.0.gbc | 60.0 / 56.3 | 17,946 | メニュー終了 |  |
| gbc | picoarch:vbam | Akumanor Gaiden DX v1.0.gbc | 60.0 / 55.3 | 16,588 | メニュー終了 |  |
| gbc | standalone:gambatte2020 | Akumanor Gaiden DX v1.0.gbc | 59.9 / 59.8 | 30,720 | 試験用停止 |  |
| gbc | standalone:ohboy | Akumanor Gaiden DX v1.0.gbc | 60.0 / 60.0 | 21,504 | 試験用停止 |  |
| gba | standalone:regba | goodboy.gba | 60.0 / 41.6 | 18,944 | 試験用停止 |  |
| gba | picoarch:gpsp | goodboy.gba | 57.9 / 56.7 | 18,944 | メニュー終了 |  |
| megadrive | standalone:picodrive | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 59.9 / 60.0 | 1,049 | 試験用停止 |  |
| megadrive | picoarch:picodrive | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 59.9 / 60.0 | 695 | メニュー終了 |  |
| megadrive | standalone:genesisgx | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 60.0 / 47.9 | 1,188 | 試験用停止 |  |
| mastersystem | standalone:picodrive | Frontier Force (V1.1).sms | 60.0 / 60.0 | 3,647 | 試験用停止 |  |
| mastersystem | picoarch:genesis_plus_gx | Frontier Force (V1.1).sms | 60.0 / 60.0 | 2,669 | メニュー終了 |  |
| mastersystem | picoarch:picodrive | Frontier Force (V1.1).sms | 60.0 / 60.0 | 3,647 | メニュー終了 |  |
| mastersystem | picoarch:gearsystem | Frontier Force (V1.1).sms | 60.0 / 59.0 | 9,250 | メニュー終了 |  |
| mastersystem | standalone:smsplusms | Frontier Force (V1.1).sms | 60.1 / 66.7 更新 | 3,356 | 試験用停止 |  |
| gamegear | standalone:picodrive | Puyo Puyo.gg | 60.0 / 60.0 | 4,071 | 試験用停止 |  |
| gamegear | picoarch:genesis_plus_gx | Puyo Puyo.gg | 60.0 / 60.0 | 3,710 | メニュー終了 |  |
| gamegear | picoarch:picodrive | Puyo Puyo.gg | 60.0 / 60.0 | 4,071 | メニュー終了 |  |
| gamegear | picoarch:gearsystem | Puyo Puyo.gg | 60.0 / 59.0 | 9,963 | メニュー終了 |  |
| gamegear | standalone:smsplusgg | Puyo Puyo.gg | 60.1 / 66.2 更新 | 2,678 | 試験用停止 |  |
| segacd | picoarch:picodrive | Night Striker (Japan).chd | 59.9 / 59.5 | 9,748 | メニュー終了 | 日本版BIOS起動画面 |
| pcengine | picoarch:mednafen_pce_fast | AirZonk_U.pce | 60.0 / 60.0 | 10,009 | メニュー終了 |  |
| pcengine | picoarch:mednafen_supergrafx | AirZonk_U.pce | 60.0 / 59.0 | 10,323 | メニュー終了 |  |
| pcengine | standalone:temper | AirZonk_U.pce | 60.1 / 59.3 | 14,375 | 試験用停止 |  |
| supergrafx | picoarch:mednafen_supergrafx | 1941 - Counter Attack (Super Grafx) (J).pce | 59.0 / 59.0 | 1,874 | メニュー終了 |  |
| pcenginecd | picoarch:mednafen_pce_fast | ChouAniki.chd | 60.0 / 55.2 | 321 | メニュー終了 | ロードからロゴ・演出へ遷移 |
| psx | standalone:pcsx4all | RUNABOUT-2.cue | 46.4 / 48.0 | 0 | 試験用停止 | 起動ロゴ、走行は未確認 |
| ngpc | standalone:race | Baseball Stars Color (World) (En,Ja).ngc | 60.0 / 51.4 | 14,822 | 試験用停止 |  |
| wonderswan | picoarch:mednafen_wswan | Puzzle Bobble.ws | 60.0 / 59.0 | 13,391 | メニュー終了 |  |
| wonderswan | standalone:oswan | Puzzle Bobble.ws | 75.0 / 75.2 更新 | 3,600 | 試験用停止 |  |
| msx | picoarch:fmsx | usas.rom | 59.5 / 60.0 | 3,150 | メニュー終了 |  |
| msx | picoarch:bluemsx | usas.rom | 56.3 / 58.5 | 32,767 | メニュー終了 |  |
| atari800 | standalone:atari800 | CavernsOfMars.car | 49.3 / 50.0 | 8,207 | 試験用停止 |  |
| atari2600 | standalone:stella | Centipede.bin | 60.0 / 59.9 | 15,360 | 試験用停止 |  |
| pokemini | standalone:pokemini | Pichu Bros. Mini (Japan).min | 76.8 / 76.5 更新 | 0 | 試験用停止 | 名前入力前の案内 |
| lynx | standalone:handy | Basketbrawl (1992).lnx | 59.9 / 54.8 | 5,888 | 試験用停止 |  |
| cpc | standalone:crocods | Abyssal (2022)(Cabbage Corp).sna | 50.0 / 50.0 | 0 | 試験用停止 | BASIC・エミュメニュー |
| zxspectrum | standalone:unrealspeccy | 10th Frame.tap | 59.4 / 59.6 | 9,192 | 試験用停止 |  |
| neogeo | standalone:gngeo | aof2.zip | 16.9 / 39.4 | 0 | 試験用停止 | 起動時の表示とエミュメニュー |
| neogeocd | standalone:neo4all | Fatal Fury.m3u | 58.8 / 58.8 | 5,680 | 途中終了 | Fatal Furyの操作説明後にBus error、終了コード138 |
| amiga | standalone:uae4all | Baby Jo.adf | 50.0 / 50.0 | 0 | 試験用停止 | ディスクロード中、ゲーム映像は未確認 |
| arcade | standalone:fba44 | kungfum.zip | 60.0 / 58.9 | 3,186 | 試験用停止 | タイトル・操作説明 |

## 追加試験

| 機種 | FE経路 | 代表ROM | 終盤の更新窓（回/秒） | PCMピーク | 終了 | 特記事項 |
| --- | --- | --- | ---: | ---: | --- | --- |
| segacd | picoarch:picodrive | Night Striker (Japan).chd | 59.8 / 59.2 | 11,493 | メニュー終了 | STARTを複数回入力しても取得時点は日本版BIOS、ゲーム本編は未確認 |
| pcenginecd | picoarch:mednafen_pce_fast | ChouAniki.chd | 52.0 / 59.3 | 7,022 | メニュー終了 | Chou Anikiのゲーム画面とPCMを取得 |
| psx | standalone:pcsx4all | RUNABOUT-2.cue | 60.8 / 47.4 | 18,507 | メニュー終了 | RUNABOUT-2のタイトルとPCMを取得、Quitで終了。走行中は未計測 |
| pokemini | standalone:pokemini | Pokemon Party Mini - Baseline Judge (Europe) (GameCube).min | 76.5 / 76.4 更新 | 16,384 | 試験用停止 | 別ROMのミニゲーム画面とPCMを取得。更新回数はゲームFPSと区別 |
| cpc | standalone:crocods | 007 - Live and Let Die (1988)(Domark).dsk | 50.0 / 50.1 | 0 | 試験用停止 | 別ROMでゲームタイトルに到達、プレイ中の音声は未確認 |
| neogeo | standalone:gngeo | aof2.zip | 39.4 / 60.0 | 5,998 | 試験用停止 | 起動ロゴのサンプルで終盤約60更新・PCMあり、対戦中は未確認 |
| neogeocd | standalone:neo4all | Fatal Fury.m3u | 58.8 / 58.7 | 21 | 試験用停止 | 初回のBus errorはこの短時間では再現せず、操作説明とエミュメニューまで |
| amiga | standalone:uae4all | Baby Jo.adf | 50.0 / 45.9 | 0 | 試験用停止 | ロード待ちを延長して再試験 |

## 実機確認の結果

- Gambatte 2020はGB・GBCともに約60更新/秒、PCMピーク30,720。RG300Xで修正した無音は今回再現しなかった。今回のSELECT＋STARTの取得画像では、Gambatte 2020のメニュー表示は確認できなかった。
- PC Engine CDのChou Anikiは追加操作でゲーム画面とPCMを取得。PokeMiniも別ROMでミニゲームの画面とPCMを取得した。Sega CDはBIOS、PCSX4ALLはタイトル、GnGeoは起動ロゴまで計測した。PCSX4ALLはエミュレータのQuitで正常終了した。
- CrocoDSは別ROMでタイトルまで進んだが、プレイ中の音声は確認できていない。UAE4Allは約70秒待ってもディスク読込中で、プレイを確認できていない。
- NEO4ALLはFatal Furyの操作説明後に一度Bus error（終了138）。再試験では操作説明後もエミュレータが動作しメニューを開けた。安定性については継続確認が必要。
- ネイティブFEのGBA一覧からCastlevaniaをReGBAで起動し、SELECT＋STARTメニューからExit。復帰直後の一枚は黒画面だったが、再試験では追加入力なしで3秒後に同じFE PID 15598のGBA一覧を確認した。最後にTOPへ戻し、エミュレータが残っていないこと、SD2の読み取り専用、CPU 996 MHzを確認した。

生ログ・画像はGit管理外の `output/rg350m-validation/emulator-routes/` に保存した。
