# RG350 OPKのROM候補・ソース対策再確認（2026-11-17）

**再試験の更新:** [ROM未指定項目の実行結果](rg280v-rg350-missing-rom-retest-2026-11-18.md) に、全27配布OPKの結果、Stella候補、NEO4ALLのソースビルド・WAV対策を記録した。以下の旧選定に含まれるMSX DISK.ROMとAtariのBIOSはゲーム数へ算入しない。

**重複確認後の更新:** [既存SAとの照合結果](rg280v-rg350-sa-duplicates-2026-11-17.md) に基づき、PocketSNESとGambatte 2021は別候補から除外。FCEUXは既存SA 2.6.6に対する2.2.3の比較として残す。現在の目視確認メニューは27項目。以下の全件一覧・30項目の記述は重複確認前の監査・配置履歴を含む。

検証用ROMセット の28,581ファイルを再走査した。62 OPKを46の比較用ROMグループへ対応付け、同じ機種の別OPKでは同じ3タイトルを使用する。別地域版・別形式・同じディスクの重複はタイトル数へ加えない。候補パスの存在と配置はゲーム互換性の合格を意味しない。

## 用意した比較環境

小容量のROM候補82ファイルをSD1の `/media/data/local/rg350-rom-candidates/` へ配置し、各ファイルのSHA-256をMac側と照合した。ROMのコピー元はNAS、SD2の既存ファイルは変更していない。CDイメージやデータディレクトリ一式はNASに候補を確保し、下表に場所を記載する。単独のCUE/HE0/LDBファイルだけで起動せず、対応するゲームデータ一式を使用する。

目視確認候補10 OPK × 各3タイトルの30項目をFEのSTART → Appsへ追加した。項目名は `TEST 番号 エミュ名 1〜3: タイトル`。既存のAtari800・FBA・Temperの9項目も残す。通常のFEエミュ経路への採用ではなく、比較試験用の入口。

| エミュ | 比較する3タイトル |
| --- | --- |
| FCEUX | Super Mario Bros. / Baseball / rockman |
| Genesis Plus GX | Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World) / jp_etc_Sonic_The_Hedgehog / jp_etc_Sonic_The_Hedgehog_2 |
| PokeMini | Pichu Bros. Mini (Japan) / Pokemon Anime Card Daisakusen (Japan) / Pokemon Party Mini - Baseline Judge (Europe) (GameCube) |
| Race Explorer | Baseball Stars Color (World) (En,Ja) / Metal Slug - 1st Mission (World) (En,Ja) / Bakumatsu Rouman Tokubetsu Hen - Gekka no Kenshi - Tsuki ni Saku Hana, Chiri Yuku Hana (Japan) |
| CrocoDS | 007 - Live and Let Die (1988)(Domark) / Abyssal (2022)(Cabbage Corp) / Disc Power (19xx)(-) |
| Gambatte 2020 | Super Mario Land [V1.1] / Dr. Mario [V1.0] / Dracula Densetsu |
| Gambatte 2021 | Super Mario Land [V1.1] / Dr. Mario [V1.0] / Dracula Densetsu |
| Gambatte GB | Super Mario Land [V1.1] / Dr. Mario [V1.0] / Dracula Densetsu |
| Gambatte GBC | Akumanor Gaiden DX v1.0 / Cross Hunter - X Hunter Version / Dangan GB2 |
| OhBoy | Super Mario Land [V1.1] / Dr. Mario [V1.0] / Dracula Densetsu |

## 「ROMなし」の訂正

前回の「ROMなし」は監査時にROM引数を指定していなかったという意味で、NAS上に存在しないと確認した結果ではなかった。今回、3DO、Amstrad CPC、ColecoVision、Atari ST、DOS、Lynx、Neo Geo CD、OpenBOR、Pokémon mini、Supervision、Atari 7800/2600、Amiga、C64、Intellivision、MSX、N64、ScummVMなどの素材を確認した。

再走査でゲーム用ファイルを特定できなかったのはDaphne、Vectrex、Apple IIgs、TIC-80。VectrexはAnalogue Pocket用の設定JSONと本体ROMらしい `vectrex.bin` はあるが、ゲーム用カートリッジを特定できていない。フォルダ名だけでROMありと数えない。圧縮アーカイブ全体の機種判別を完了した意味ではなく、未特定は素材不存在の断定ではない。

3タイトル未満の機種は下表の実数だけとする。特にAtari STの1本はゲームではなくLattice Cで、操作・表示の素材に限る。CPCのDisc Powerもゲーム本編の判定用かは未確認。

## ソースビルドでどこまで対処したか

今回の62配布OPKの対策として、エミュ本体をソースから作り直し実機確認したのはAtari800、FBA44、Temperの3系統。いずれもビルド自体は成功した。FBAのNinja Spiritは修正後も約38 FPS・音飛びで、ソース対策後にも性能課題が残る例。

それ以外の配布原版に行った主な対処は共有ライブラリの再ビルド・追加、起動環境、ROM引数の修正であり、エミュ本体のソース修正を尽くした結果ではない。OswanのABI不一致、Nestopia/SMS Plusの異常終了、Mednafen PCE/PC-FXのassert、PicoDrive配布版のSDLマウス初期化失敗などはソース対策未完。単純に「対応不能」「ビルドしてもダメ」としない。既存FEのPCSX4ALL、PicoDrive等の別ビルド実績は配布原版の試験と区別する。

## 全62本の再確認表

ROMパスは指定NASルートからの相対パス。`配置N` は小容量候補をSD1へ転送・照合済みの数。CDやデータ一式の転送は未実施。候補数0は未特定。

| No. | OPK | ROM候補数 / SD1配置 | 候補パス | 本体のソース対策 |
| ---: | --- | --- | --- | --- |
| 01 | `3DOh_2018-05-23.opk` | 候補1 / 配置0 | `_etc/3do/biofury.iso` | この配布原版の本体再ビルドは未実施 |
| 02 | `Arnold_2019-12-03.opk` | 候補3 / 配置3 | `_etc/amstradcpc/007 - Live and Let Die (1988)(Domark).dsk`<br>`_etc/amstradcpc/Abyssal (2022)(Cabbage Corp).sna`<br>`_etc/amstradcpc/Disc Power (19xx)(-).bin` | この配布原版の本体再ビルドは未実施 |
| 03 | `Atari 800 v1.1.opk` | 候補3 / 配置3 | `ATARI/800/ATARIBAS.ROM`<br>`ATARI/800/ATARIOSB.ROM`<br>`ATARI/800/ATARIXL.ROM` | 旧版は未実施。代替Atari800 4.1.0をソース改修済み |
| 04 | `Atari800_2020-02-14.opk` | 候補3 / 配置3 | `ATARI/800/ATARIBAS.ROM`<br>`ATARI/800/ATARIOSB.ROM`<br>`ATARI/800/ATARIXL.ROM` | 代替Atari800 4.1.0をソース改修、実機正常 |
| 05 | `ColecoD_2013-06-15-launcher.opk` | 候補1 / 配置1 | `_etc/coleco/Dam Busters, The (USA).col` | この配布原版の本体再ビルドは未実施 |
| 06 | `DCaSTaway_2014-11-09.opk` | 候補1 / 配置1 | `_etc/atarist/Lattice C (19xx)(Hisoft).st` | この配布原版の本体再ビルドは未実施 |
| 07 | `DOSBox_2019-11-11-launcher.opk` | 候補3 / 配置3 | `pc/DOSBOX_ALIENBREED.ZIP`<br>`pc/DOSBOX_DOOM.ZIP`<br>`pc/DOSBOX_TV.ZIP` | この配布原版の本体再ビルドは未実施 |
| 08 | `Daphne_2015-05-07.opk` | 候補0 / 配置0 | 未特定 | この配布原版の本体再ビルドは未実施 |
| 09 | `DinguxVectrex_2014-05-25.opk` | 候補0 / 配置0 | 未特定 | この配布原版の本体再ビルドは未実施 |
| 10 | `EasyRPG_2017-12-13.opk` | 候補1 / 配置0 | `_etc/EASYRPG/TurnedIntoAGirl/RPG_RT.ldb` | この配布原版の本体再ビルドは未実施 |
| 11 | `FCEUX_2019-11-15.opk` | 候補3 / 配置3 | `nes/Super Mario Bros..nes`<br>`nes/Baseball.nes`<br>`nes/rockman.nes` | この配布原版の本体再ビルドは未実施 |
| 12 | `GenesisPlusGX_2019-12-23.opk` | 候補3 / 配置3 | `megadrive/Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md`<br>`megadrive/md/jp_etc_Sonic_The_Hedgehog.bin`<br>`megadrive/md/jp_etc_Sonic_The_Hedgehog_2.bin` | この配布原版の本体再ビルドは未実施 |
| 13 | `Handy_2019-12-10.opk` | 候補3 / 配置3 | `ATARI/Lynx/Basketbrawl (1992).lnx`<br>`ATARI/Lynx/Malibu Bikini Volleyball (1993).lnx`<br>`ATARI/Lynx/Scrapyard Dog (1991).lnx` | この配布原版の本体再ビルドは未実施 |
| 14 | `KEGS_2016-05-04.opk` | 候補0 / 配置0 | 未特定 | この配布原版の本体再ビルドは未実施 |
| 15 | `NEO4All_2019-12-16.opk` | 候補1 / 配置0 | `_etc/neogeocd/Fatal Fury WAV/Fatal Fury WAV.cue` | この配布原版の本体再ビルドは未実施 |
| 16 | `Nestopia_2020-01-01.opk` | 候補3 / 配置3 | `nes/Super Mario Bros..nes`<br>`nes/Baseball.nes`<br>`nes/rockman.nes` | この配布原版の本体再ビルドは未実施 |
| 17 | `OpenBOR-2014.06.03.opk` | 候補3 / 配置0 | `openbor/Crisis Evil 1.pak`<br>`openbor/Crisis Evil III - Santiago Infected [v.3.0 Build 4086].PAK`<br>`openbor/DemonSluga.pak` | この配布原版の本体再ビルドは未実施 |
| 18 | `Oswan_2019-10-09.opk` | 候補1 / 配置1 | `wonderswan/Puzzle Bobble.ws` | この配布原版の本体再ビルドは未実施 |
| 19 | `PicoDrive-gcw0_1.99.opk` | 候補3 / 配置3 | `megadrive/Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md`<br>`megadrive/md/jp_etc_Sonic_The_Hedgehog.bin`<br>`megadrive/md/jp_etc_Sonic_The_Hedgehog_2.bin` | この配布原版の本体再ビルドは未実施 |
| 20 | `PocketSNES_2019-12-12.opk` | 候補3 / 配置3 | `snes/Adventures of the Rocketeer.sfc`<br>`snes/AkumajouDraculaXX_0408.SFC`<br>`snes/Albert Odyssey [V1.0].sfc` | この配布原版の本体再ビルドは未実施 |
| 21 | `PokeMini_2015-07-05.opk` | 候補3 / 配置3 | `_etc/pokemini/Pichu Bros. Mini (Japan).zip`<br>`_etc/pokemini/Pokemon Anime Card Daisakusen (Japan).zip`<br>`_etc/pokemini/Pokemon Party Mini - Baseline Judge (Europe) (GameCube).zip` | この配布原版の本体再ビルドは未実施 |
| 22 | `Potator_2013-09-17.opk` | 候補1 / 配置1 | `_etc/supervision/assembloids_supervision_2022.bin` | この配布原版の本体再ビルドは未実施 |
| 23 | `ProSystem_2013-06-16-launcher.opk` | 候補3 / 配置3 | `ATARI/7800/Asteroids (1987) (Atari).a78`<br>`ATARI/7800/Basketbrawl (1990) (Atari).a78`<br>`ATARI/7800/Centipede (1987) (Atari).a78` | この配布原版の本体再ビルドは未実施 |
| 24 | `Race(Explorer)_2019-12-11.opk` | 候補3 / 配置3 | `ngpc/Baseball Stars Color (World) (En,Ja).ngc`<br>`ngpc/Metal Slug - 1st Mission (World) (En,Ja).ngc`<br>`ngpc/Bakumatsu Rouman Tokubetsu Hen - Gekka no Kenshi - Tsuki ni Saku Hana, Chiri Yuku Hana (Japan).ngc` | この配布原版の本体再ビルドは未実施 |
| 25 | `Race(Neogeo Pocket).opk` | 候補3 / 配置3 | `ngpc/Baseball Stars Color (World) (En,Ja).ngc`<br>`ngpc/Metal Slug - 1st Mission (World) (En,Ja).ngc`<br>`ngpc/Bakumatsu Rouman Tokubetsu Hen - Gekka no Kenshi - Tsuki ni Saku Hana, Chiri Yuku Hana (Japan).ngc` | この配布原版の本体再ビルドは未実施 |
| 26 | `ReGBA_2019-12-26.opk` | 候補3 / 配置3 | `gba/Castlevania - Aria of Sorrow (European Version - Restored Audio).gba`<br>`gba/Castlevania - Circle of the Moon (European Version - Restored Audio).gba`<br>`gba/Castlevania - Harmony of Dissonance (European Version - Restored Audio).gba` | この配布原版の本体再ビルドは未実施 |
| 27 | `Snes9x_2019-11-11.opk` | 候補3 / 配置3 | `snes/Adventures of the Rocketeer.sfc`<br>`snes/AkumajouDraculaXX_0408.SFC`<br>`snes/Albert Odyssey [V1.0].sfc` | この配布原版の本体再ビルドは未実施 |
| 28 | `Stella_2015-10-06.opk` | 候補3 / 配置3 | `ATARI/2600/3DTicTacToe.bin`<br>`ATARI/2600/Adventure.bin`<br>`ATARI/2600/adventureii.bin` | この配布原版の本体再ビルドは未実施 |
| 29 | `Temper_2016-10-20.opk` | 候補3 / 配置3 | `pcengine/AirZonk_U.pce`<br>`pcengine/BlazingLazers_U.pce`<br>`pcengine/BONKs_REVENGE.PCE` | ソース改修済み、約60 FPS・メニュー正常 |
| 30 | `UAE4All_2019-08-23.opk` | 候補2 / 配置2 | `_etc/amiga/3rd Day - The Ripper (19xx)(Action Force).adf`<br>`_etc/amiga/Baby Jo in 'Going Home' (1991)(Loriciel)(M4)[cr].adf` | この配布原版の本体再ビルドは未実施 |
| 31 | `VICEx64_2020-02-13.opk` | 候補2 / 配置2 | `_etc/c64/Pacmania.zip`<br>`_etc/c64/inbread_c64_disk_2022/c64mini/inbread.d64` | この配布原版の本体再ビルドは未実施 |
| 32 | `XMAME_2015-03-15.opk` | 候補3 / 配置3 | `mame/1942a.zip`<br>`mame/ajaxj.zip`<br>`mame/akumajoun.zip` | この配布原版の本体再ビルドは未実施 |
| 33 | `crocods_20200115.opk` | 候補3 / 配置3 | `_etc/amstradcpc/007 - Live and Let Die (1988)(Domark).dsk`<br>`_etc/amstradcpc/Abyssal (2022)(Cabbage Corp).sna`<br>`_etc/amstradcpc/Disc Power (19xx)(-).bin` | この配布原版の本体再ビルドは未実施 |
| 34 | `fba44.opk` | 候補3 / 配置3 | `fbneo/kungfum.zip`<br>`fbneo/bchopper.zip`<br>`fbneo/nspirit.zip` | ソース改修済み。Kung-Fu 60 FPS、Ninja Spirit約38 FPS |
| 35 | `gambatte-dms-multi-r572u4-20200628.opk` | 候補3 / 配置3 | `gb/Super Mario Land [V1.1].gb`<br>`gb/Dr. Mario [V1.0].gb`<br>`gb/Dracula Densetsu.gb` | この配布原版の本体再ビルドは未実施 |
| 36 | `gambatte-dms-multi-r572u4-20211021.opk` | 候補3 / 配置3 | `gb/Super Mario Land [V1.1].gb`<br>`gb/Dr. Mario [V1.0].gb`<br>`gb/Dracula Densetsu.gb` | この配布原版の本体再ビルドは未実施 |
| 37 | `gambatte-opendingux-r572u3-20191201-204032(GB).opk` | 候補3 / 配置3 | `gb/Super Mario Land [V1.1].gb`<br>`gb/Dr. Mario [V1.0].gb`<br>`gb/Dracula Densetsu.gb` | この配布原版の本体再ビルドは未実施 |
| 38 | `gambatte-opendingux-r572u3-20191201-204032(GBC).opk` | 候補3 / 配置3 | `gbc/Akumanor Gaiden DX v1.0.gbc`<br>`gbc/Cross Hunter - X Hunter Version.gbc`<br>`gbc/Dangan GB2.gbc` | この配布原版の本体再ビルドは未実施 |
| 39 | `gngeo.opk` | 候補3 / 配置0 | `_etc/neogeo/ART OF FIGHTING/aof.zip`<br>`_etc/neogeo/ART OF FIGHTING/aof2.zip`<br>`_etc/neogeo/ART OF FIGHTING/aof3.zip` | この配布原版の本体再ビルドは未実施 |
| 40 | `gpsp-2019-11-15.opk` | 候補3 / 配置3 | `gba/Castlevania - Aria of Sorrow (European Version - Restored Audio).gba`<br>`gba/Castlevania - Circle of the Moon (European Version - Restored Audio).gba`<br>`gba/Castlevania - Harmony of Dissonance (European Version - Restored Audio).gba` | この配布原版の本体再ビルドは未実施 |
| 41 | `gw-rg350_2020-03-18.opk` | 候補2 / 配置2 | `_etc/gameandwatch/Snoopy (Nintendo, Table Top).zip`<br>`_etc/gameandwatch/Tennis Menace.zip` | この配布原版の本体再ビルドは未実施 |
| 42 | `jzIntv_2015-03-28.opk` | 候補1 / 配置1 | `_etc/intellivision/Lock 'N' Chase (USA, Europe) (v1.1)/Lock 'N' Chase (USA, Europe) (v1.1).bin` | この配布原版の本体再ビルドは未実施 |
| 43 | `mame4all-params-5.opk` | 候補3 / 配置3 | `mame/1942a.zip`<br>`mame/ajaxj.zip`<br>`mame/akumajoun.zip` | この配布原版の本体再ビルドは未実施 |
| 44 | `mame4all.opk` | 候補3 / 配置3 | `mame/1942a.zip`<br>`mame/ajaxj.zip`<br>`mame/akumajoun.zip` | この配布原版の本体再ビルドは未実施 |
| 45 | `mednafen.opk` | 候補3 / 配置3 | `pcengine/AirZonk_U.pce`<br>`pcengine/Aldynes.PCE`<br>`pcengine/AlienCrush_J.pce` | この配布原版の本体再ビルドは未実施 |
| 46 | `mednafen_pce.opk` | 候補3 / 配置3 | `pcengine/AirZonk_U.pce`<br>`pcengine/BlazingLazers_U.pce`<br>`pcengine/BONKs_REVENGE.PCE` | この配布原版の本体再ビルドは未実施 |
| 47 | `mednafen_pcfx.opk` | 候補1 / 配置0 | `_etc/pcfx/SimpleBattle_FX/simplebattle.cue` | この配布原版の本体再ビルドは未実施 |
| 48 | `mupen64plus.opk` | 候補3 / 配置3 | `n64/AeroGauge [V1.1].z64`<br>`n64/Blastdozer.z64`<br>`n64/Chou Kuukan Nighter Pro Yakyuu King.z64` | この配布原版の本体再ビルドは未実施 |
| 49 | `ohboy.opk` | 候補3 / 配置3 | `gb/Super Mario Land [V1.1].gb`<br>`gb/Dr. Mario [V1.0].gb`<br>`gb/Dracula Densetsu.gb` | この配布原版の本体再ビルドは未実施 |
| 50 | `openMSX-0.15-remap.opk` | 候補3 / 配置3 | `msx2/usas.rom`<br>`msx2/XGR1Trial.rom`<br>`msx2/bios/DISK.ROM` | この配布原版の本体再ビルドは未実施 |
| 51 | `pcsx4all.opk` | 候補3 / 配置0 | `psx/Ape_Escape ( SARU_GETTYU).cue`<br>`psx/DESCENT.cue`<br>`psx/FINALIST.cue` | この配布原版の本体再ビルドは未実施 |
| 52 | `picodrive_gcw0(32X).opk` | 候補1 / 配置1 | `_etc/sega32x/BC Racers (USA).32x` | この配布原版の本体再ビルドは未実施 |
| 53 | `picodrive_gcw0(CD).opk` | 候補2 / 配置0 | `_etc/segacd/Fatal Fury Special (Europe) (Demo)/Fatal Fury Special (Europe) (Demo).cue`<br>`_etc/segacd/Night Striker (Japan)/Night Striker (Japan).chd` | この配布原版の本体再ビルドは未実施 |
| 54 | `picodrive_gcw0(MD).opk` | 候補3 / 配置3 | `megadrive/Bare Knuckle - Ikari no Tekken ~ Streets of Rage (World).md`<br>`megadrive/md/jp_etc_Sonic_The_Hedgehog.bin`<br>`megadrive/md/jp_etc_Sonic_The_Hedgehog_2.bin` | この配布原版の本体再ビルドは未実施 |
| 55 | `retro8_v1b_20200108.opk` | 候補3 / 配置3 | `pico-8/51752.p8`<br>`pico-8/Breakout_Hero.p8`<br>`pico-8/Cave_Runners.p8` | この配布原版の本体再ビルドは未実施 |
| 56 | `scummvm-rg350-01132020.opk` | 候補3 / 配置0 | `scummvm/BASS-Floppy-1.3/sky.dsk`<br>`scummvm/Monkey Island 2 LeChuck's Revenge (Floppy DOS VGA)/MONKEY2.000`<br>`scummvm/Backyard Baseball (CD Windows)/BASEBALL.HE0` | この配布原版の本体再ビルドは未実施 |
| 57 | `smsplus_gcw0(GG).opk` | 候補3 / 配置3 | `gamegear/Columns [V1.0].gg`<br>`gamegear/Eternal Legend (Japan).gg`<br>`gamegear/g-loc air battle (j) [!].gg` | この配布原版の本体再ビルドは未実施 |
| 58 | `smsplus_gcw0(MS).opk` | 候補3 / 配置3 | `mastersystem/Frontier Force (V1.1).sms`<br>`mastersystem/MS_Operation_Wolf_mod_2025_0318_1147.SMS`<br>`mastersystem/MS_Operation_Wolf_mod_NoPad_2025_0331_1606.SMS` | この配布原版の本体再ビルドは未実施 |
| 59 | `tic-80_rg350_20200321_steward.opk` | 候補0 / 配置0 | 未特定 | この配布原版の本体再ビルドは未実施 |
| 60 | `uae4all-params-20200430.opk` | 候補2 / 配置2 | `_etc/amiga/3rd Day - The Ripper (19xx)(Action Force).adf`<br>`_etc/amiga/Baby Jo in 'Going Home' (1991)(Loriciel)(M4)[cr].adf` | この配布原版の本体再ビルドは未実施 |
| 61 | `unreal_speccy_portable-0.0.86.12_rg350_r1.opk` | 候補1 / 配置1 | `_etc/zxspectrum/10th Frame (1987)(U.S. Gold).tap` | この配布原版の本体再ビルドは未実施 |
| 62 | `unreal_speccy_portable0.0.59.opk` | 候補1 / 配置1 | `_etc/zxspectrum/10th Frame (1987)(U.S. Gold).tap` | この配布原版の本体再ビルドは未実施 |

再現用: `python3 scripts/prepare-rg350-rom-candidates.py --refresh-inventory --deploy`、続けて `python3 scripts/setup-rg350-rom-candidate-menu.py`。ROM・OPK・生成manifestはGit管理外。ソース対策未実施の候補は、適切なROMで起動経路を確認した後にソース移植の優先度を決める。
