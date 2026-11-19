# RG350の全FEエミュ経路の実機検証

RG350の実機FE設定に登録された26機種・58経路（単体30、PicoArch 28）を、SD2上の代表ROMで短時間ずつ検証した。全58経路で画面と更新回数を取得し、再試験も含め55経路でPCM信号を取得。全58経路でエミュレータのメニューから通常終了し、同じFEプロセスの画面へ戻る手順を少なくとも1回確認した。SD2は読み取り専用で使用した。

FPS欄はSDL更新の終盤2窓。ロゴ、タイトル、ロード、ゲーム中のいずれかを測った値で、実プレイ中の継続FPSとは区別する。60を超える更新数はゲーム固有のFPSとして扱わない。PCMは内蔵スピーカーの聴感ではなく、採取した音声データの最大振幅。

全経路をplumOS FEのRecentに置いた一時的な試験項目から起動し、メニュー終了後に同一FEプロセスの画面を取得した。表の映像・更新・PCMは代表計測回の記録で、通常復帰には追加試験の結果を含む。PicoArchの計測は同じ起動ディスパッチャーを直接使い、FEとの往復は別に実行した。作業後は試験用のRecentと起動設定を退避前の内容に戻し、SHA-256の一致とFEのTOPを確認した。

## 問題と計測範囲

- **NEO4ALL / Fatal Fury** は操作説明から対戦へ進む前に、音声・描画計測を入れた2回で途中終了した。1回目は`Segmentation fault`（139）、2回目は`Bus error`（138）。計測用ライブラリを外した追加試験では操作説明を表示し、メニューのExitでFEへ戻った。計測の有無と異常終了の因果関係は未確定。PCM信号と対戦中の安定性は未確認。
- **CrocoDS** は007のタイトルまで到達した。メニューは初期位置のDiskから上2回でQuitを選ぶとFEへ戻れた。約50更新/秒。採取区間でPCM信号は得られなかった。
- **UAE4All** はBaby Joのディスク読み込み表示とメニューを取得。約70秒の試験で本編に達せず、PCM信号なし。メニューのExitではFEへ戻った。
- **Temper** はAir Zonkの起動区間ではPCMピーク0だった。Blazing Lazersで再試験すると59.5／60.0更新/秒、PCMピーク6,944で、メニューから同じFEへ戻った。
- **Atari800** はメニューの先頭から下へ移動してExit Emulatorを選ぶとFEへ戻った。**blueMSX** は起動待ちを約7秒に延ばして通常復帰を確認した。
- **Sega CD** は日本版Night Strikerの起動画面まで、**PCSX4ALL** はRUNABOUT-2の起動演出・メニューまで採取。両方でPCM信号と通常復帰を確認したが、本編の継続FPSは未計測。

## 経路別結果

| 機種 | 経路 | ROM | 更新/秒（終盤2窓） | PCMピーク | 映像 | 終了と復帰 |
| --- | --- | --- | ---: | ---: | --- | --- |
| nes | standalone:fceux | Super Mario Bros..nes | 60.9 / 60.0 | 17,987 | 取得 | 同じFEへ復帰 |
| nes | picoarch:fceumm | Super Mario Bros..nes | 59.1 / 59.5 | 14,376 | 取得 | 同じFEへ復帰 |
| nes | picoarch:nestopia | Super Mario Bros..nes | 59.0 / 59.0 | 27,747 | 取得 | 同じFEへ復帰 |
| nes | picoarch:quicknes | Super Mario Bros..nes | 60.0 / 60.0 | 13,553 | 取得 | 同じFEへ復帰 |
| nes | standalone:fceux223 | Super Mario Bros..nes | 59.8 / 57.4 | 17,444 | 取得 | 同じFEへ復帰 |
| sfc | standalone:pocketsnes | Super Mario World - Super Mario Bros. 4.sfc | 60.0 / 59.7 | 5,716 | 取得 | 同じFEへ復帰 |
| sfc | picoarch:snes9x2005 | Super Mario World - Super Mario Bros. 4.sfc | 60.1 / 59.9 | 7,895 | 取得 | 同じFEへ復帰 |
| sfc | picoarch:chimerasnes | Super Mario World - Super Mario Bros. 4.sfc | 60.3 / 59.9 | 7,336 | 取得 | 同じFEへ復帰 |
| sfc | picoarch:snes9x2005_plus | Super Mario World - Super Mario Bros. 4.sfc | 60.0 / 59.0 | 7,461 | 取得 | 同じFEへ復帰 |
| gb | standalone:gambatte | Super Mario Land [V1.1].gb | 58.5 / 59.7 | 30,720 | 取得 | 同じFEへ復帰 |
| gb | picoarch:gambatte | Super Mario Land [V1.1].gb | 60.0 / 60.0 | 12,834 | 取得 | 同じFEへ復帰 |
| gb | picoarch:gearboy | Super Mario Land [V1.1].gb | 60.0 / 56.7 | 21,020 | 取得 | 同じFEへ復帰 |
| gb | picoarch:vbam | Super Mario Land [V1.1].gb | 60.0 / 59.4 | 12,572 | 取得 | 同じFEへ復帰 |
| gb | standalone:gambatte2020 | Super Mario Land [V1.1].gb | 59.9 / 59.1 | 30,720 | 取得 | 同じFEへ復帰 |
| gb | standalone:ohboy | Super Mario Land [V1.1].gb | 60.0 / 57.6 | 23,808 | 取得 | 同じFEへ復帰 |
| gbc | standalone:gambatte | Akumanor Gaiden DX v1.0.gbc | 59.9 / 59.9 | 30,720 | 取得 | 同じFEへ復帰 |
| gbc | picoarch:gambatte | Akumanor Gaiden DX v1.0.gbc | 60.0 / 59.7 | 10,859 | 取得 | 同じFEへ復帰 |
| gbc | picoarch:gearboy | Akumanor Gaiden DX v1.0.gbc | 58.1 / 56.3 | 17,945 | 取得 | 同じFEへ復帰 |
| gbc | picoarch:vbam | Akumanor Gaiden DX v1.0.gbc | 60.0 / 55.7 | 17,371 | 取得 | 同じFEへ復帰 |
| gbc | standalone:gambatte2020 | Akumanor Gaiden DX v1.0.gbc | 59.8 / 59.8 | 30,720 | 取得 | 同じFEへ復帰 |
| gbc | standalone:ohboy | Akumanor Gaiden DX v1.0.gbc | 60.0 / 60.0 | 21,504 | 取得 | 同じFEへ復帰 |
| gba | standalone:regba | goodboy.gba | 60.0 / 52.8 | 17,504 | 取得 | 同じFEへ復帰 |
| gba | picoarch:gpsp | goodboy.gba | 56.7 / 56.7 | 18,944 | 取得 | 同じFEへ復帰 |
| megadrive | standalone:picodrive | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 60.0 / 59.9 | 1,051 | 取得 | 同じFEへ復帰 |
| megadrive | picoarch:picodrive | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 60.0 / 59.5 | 695 | 取得 | 同じFEへ復帰 |
| megadrive | standalone:genesisgx | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md | 59.8 / 59.9 | 1,253 | 取得 | 同じFEへ復帰 |
| mastersystem | standalone:picodrive | Frontier Force (V1.1).sms | 60.0 / 60.0 | 3,647 | 取得 | 同じFEへ復帰 |
| mastersystem | picoarch:genesis_plus_gx | Frontier Force (V1.1).sms | 60.0 / 60.0 | 2,669 | 取得 | 同じFEへ復帰 |
| mastersystem | picoarch:picodrive | Frontier Force (V1.1).sms | 60.0 / 60.0 | 3,647 | 取得 | 同じFEへ復帰 |
| mastersystem | picoarch:gearsystem | Frontier Force (V1.1).sms | 60.0 / 59.0 | 9,250 | 取得 | 同じFEへ復帰 |
| mastersystem | standalone:smsplusms | Frontier Force (V1.1).sms | 60.1 / 114.9 更新 | 3,356 | 取得 | 同じFEへ復帰 |
| gamegear | standalone:picodrive | Puyo Puyo.gg | 60.1 / 60.0 | 3,644 | 取得 | 同じFEへ復帰 |
| gamegear | picoarch:genesis_plus_gx | Puyo Puyo.gg | 60.0 / 60.0 | 3,665 | 取得 | 同じFEへ復帰 |
| gamegear | picoarch:picodrive | Puyo Puyo.gg | 60.0 / 60.0 | 4,071 | 取得 | 同じFEへ復帰 |
| gamegear | picoarch:gearsystem | Puyo Puyo.gg | 60.0 / 59.0 | 10,658 | 取得 | 同じFEへ復帰 |
| gamegear | standalone:smsplusgg | Puyo Puyo.gg | 60.1 / 115.0 更新 | 2,678 | 取得 | 同じFEへ復帰 |
| segacd | picoarch:picodrive | Night Striker (Japan).chd | 60.0 / 59.8 | 13,140 | 取得 | 同じFEへ復帰 |
| pcengine | picoarch:mednafen_pce_fast | AirZonk_U.pce | 60.0 / 59.5 | 12,445 | 取得 | 同じFEへ復帰 |
| pcengine | picoarch:mednafen_supergrafx | AirZonk_U.pce | 60.0 / 60.0 | 10,531 | 取得 | 同じFEへ復帰 |
| pcengine | standalone:temper | AirZonk_U.pce | 60.1 / 59.1 | 0 | 取得 | 同じFEへ復帰 |
| supergrafx | picoarch:mednafen_supergrafx | 1941 - Counter Attack (Super Grafx) (J).pce | 60.0 / 59.0 | 1,796 | 取得 | 同じFEへ復帰 |
| pcenginecd | picoarch:mednafen_pce_fast | ChouAniki.chd | 58.7 / 57.0 | 4,195 | 取得 | 同じFEへ復帰 |
| psx | standalone:pcsx4all | RUNABOUT-2.cue | 60.1 / 49.0 | 18,507 | 取得 | 同じFEへ復帰 |
| ngpc | standalone:race | Baseball Stars Color (World) (En,Ja).ngc | 60.0 / 58.5 | 12,352 | 取得 | 同じFEへ復帰 |
| wonderswan | picoarch:mednafen_wswan | Puzzle Bobble.ws | 60.0 / 59.0 | 13,516 | 取得 | 同じFEへ復帰 |
| wonderswan | standalone:oswan | Puzzle Bobble.ws | 75.1 / 119.1 更新 | 3,600 | 取得 | 同じFEへ復帰 |
| msx | picoarch:fmsx | usas.rom | 60.0 / 60.0 | 3,150 | 取得 | 同じFEへ復帰 |
| msx | picoarch:bluemsx | usas.rom | 57.0 / 59.0 | 12,330 | 取得 | 同じFEへ復帰 |
| atari800 | standalone:atari800 | CavernsOfMars.car | 49.9 / 49.9 | 6,756 | 取得 | 同じFEへ復帰 |
| atari2600 | standalone:stella | Centipede.bin | 59.9 / 60.0 | 15,360 | 取得 | 同じFEへ復帰 |
| pokemini | standalone:pokemini | Pokemon Party Mini - Baseline Judge (Europe) (GameCube).min | 76.5 / 73.6 更新 | 16,384 | 取得 | 同じFEへ復帰 |
| lynx | standalone:handy | Basketbrawl (1992).lnx | 58.9 / 60.0 | 5,888（出力エラー記録あり） | 取得 | 同じFEへ復帰 |
| cpc | standalone:crocods | 007 - Live and Let Die (1988)(Domark).dsk | 50.0 / 50.1 | 0 | 取得 | 同じFEへ復帰 |
| zxspectrum | standalone:unrealspeccy | 10th Frame.tap | 60.4 / 60.1 | 9,192 | 取得 | 同じFEへ復帰 |
| neogeo | standalone:gngeo | aof2.zip | 39.6 / 60.0 | 5,776 | 取得 | 同じFEへ復帰 |
| neogeocd | standalone:neo4all | Fatal Fury.m3u | 58.8 / 28.6 | 0 | 取得 | 同じFEへ復帰 |
| amiga | standalone:uae4all | Baby Jo.adf | 49.9 / 46.7 | 0 | 取得 | 同じFEへ復帰 |
| arcade | standalone:fba44 | kungfum.zip | 60.0 / 57.7 | 6,550 | 取得 | 同じFEへ復帰 |
