# RG280V PicoArch コア起動試験（2026-11-15）

## 条件と判定の限界

- RG280V実機、996 MHz、SD1の74コアを使用。SD2とROM2からシステム・拡張子を照合したROMを選定。ROM2のディスク・ZIPは一時的にSD1へ転送し、試験後に削除した。
- 基本は各11秒、追加バンドルは12秒起動。約3.5秒と7秒でDRM画面を取得し、SDL_Flipの時間と48 kHz PCMコールバックのゼロ標本率を記録した。制限時間での `watchdog: timeout` は正常な試験終了。
- `FPS` は最後の計測窓の画面更新回数で、ゲーム固有の目標FPSとは照合していない。起動画面だけのコアや静止画でも更新される。
- `PCM信号あり` は波形の非ゼロ標本を示すだけで、BGMの音程・速度・音量・歪みの正常性は証明しない。`PCM無音` もロゴやタイトル画面の無音区間を含み得る。
- `描画あり` は色数1を超える画像が取得できた意味で、正しい色とは限らない。参照画像と直接比較できたのはNESのBaseballだけ。ゲーム開始、入力、メニュー、長時間安定性はこの試験の対象外。
- BIOSは一括転送していない。BIOS、親ROM、ディスク付属ファイルが要るコアの失敗は、コア本体の欠陥と断定できない。

## 集計

- コアAPI読込: 74/74。ROM起動試験: 73/74。対応データなし: 1。
- 起動試験の画面結果: 描画あり 49, 全黒 10, 起動直後終了 8, 異常終了 6, ROMなし 1。
- NES（FCEUmm、QuickNES、Nestopia）は同一のBaseballで19.8、29.6、19.8 FPS。3者とも枠色が既存FCEUX参照画像と異なる。過去の実機試験でもPicoArch NESの色と音の遅れが報告済み。
- PCE Fast / Blazing Lazers は60.0 FPS、PCM非ゼロ。SFCはSnes9x 2002/2005系が概ね60 FPS、標準Snes9xは31.1 FPS、2010は19.5 FPS。
- 同じBlazing LazersでPCE Fastは描画あり、通常のPCEは全黒。CelesteではRetro8が60.0 FPS、Fake-08が23.4 FPS。これらは同じROMで比較可能な差。
- GBAの6コアは少なくとも1枚の画面中央に小さな言語選択表示が出た。自動画像判定の初期値では全黒と誤判定していたため、報告では描画ありに修正した。ここで音声が無いことは不具合確定ではない。
- FEは試験後に手動で再起動し、プロセス稼働を確認。試験後のSD1空き容量は約638 MiB。

## コア別結果

| コア | 機種 | ROM | 画面 | FPS | 音声 | 終了 | 注記 |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| a5200 | atari5200 | SuperBreakout.a52 | 描画あり | 60.0 | PCM無音 | timeout |  |
| atari800 | atari800 | FoodFight.rom | 全黒 | 60.0 | PCM無音 | timeout |  |
| bluemsx | msx | Ys2-p.dsk | 起動直後終了 | — | 未取得 | exit=255 |  |
| cannonball | cannonball | outrun.game | 起動直後終了 | — | 未取得 | exit=255 |  |
| cap32 | cpc | Abyssal (2022)(Cabbage Corp).sna | 描画あり | 29.9 | PCM信号あり | timeout | 45 FPS未満（公称fpsとは未照合） |
| chimerasnes | sfc | Super Mario World - Super Mario ... | 全黒 | 60.0 | PCM信号あり | timeout | 同じROMのSnes9x 2002/2005は描画あり |
| crocods | cpc | Abyssal (2022)(Cabbage Corp).sna | 異常終了 | — | 未取得 | signal=10 |  |
| dinothawr | dinothawr | dinothawr.game | 異常終了 | — | 未取得 | signal=6 |  |
| fake08 | pico8 | Celeste.p8 | 描画あり | 23.4 | PCM信号あり | timeout | 同じCelesteのRetro8は60 FPS; 45 FPS未満（公称fpsとは未照合） |
| fbalpha2012 | fbneo | rtypeleo.zip | 全黒 | 12.2 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| fbalpha2012_neogeo | neogeo | aof.zip | 起動直後終了 | — | 未取得 | exit=255 |  |
| fbneo | fbneo | rtypeleo.zip | 全黒 | 25.8 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| fceumm | nes | Baseball.nes | 描画あり | 19.8 | PCM信号あり | timeout | FCEUX参照画像とNES枠色が不一致; 45 FPS未満（公称fpsとは未照合） |
| freechaf | channelf | tents_CF.bin | 描画あり | 60.0 | PCM無音 | timeout |  |
| freeintv | intellivision | Lock 'N' Chase (USA, Europe) (v1... | 描画あり | 60.0 | PCM無音 | timeout |  |
| fuse | zxspectrum | 10th Frame (1987)(U.S. Gold).tap | 描画あり | 50.0 | PCM無音 | timeout |  |
| gambatte | gb | Super Mario Land [V1.1].gb | 描画あり | 59.7 | PCMほぼ無音 | timeout |  |
| gearboy | gb | Super Mario Land [V1.1].gb | 描画あり | 59.0 | PCMほぼ無音 | timeout |  |
| gearsystem | mastersystem | Wonder Boy 3.sms | 描画あり | 58.8 | PCM無音 | timeout |  |
| genesis_plus_gx | megadrive | Bare Knuckle - Ikari no Tekken ~... | 描画あり | 51.5 | PCM信号あり | timeout |  |
| gme | music | blueshadow.nsfe | 描画あり | 60.0 | PCM信号あり | timeout |  |
| gpsp | gba | Castlevania - Aria of Sorrow (Eu... | 描画あり | 60.0 | PCM無音 | timeout | 言語選択で待機、プレイ未確認 |
| gw | gameandwatch | Tennis Menace.mgw | 描画あり | 30.0 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| hatari | atarist | Lattice C (19xx)(Hisoft).st | 起動直後終了 | — | 未取得 | exit=255 |  |
| lowresnx | lowresnx | Rubik's cube.nx | 描画あり | 29.7 | PCMほぼ無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| lutro | lutro | lutro-pong.lutro | 起動直後終了 | — | 未取得 | exit=255 |  |
| mednafen_gba | gba | Castlevania - Aria of Sorrow (Eu... | 描画あり | 60.0 | PCM無音 | timeout | 言語選択で待機、プレイ未確認 |
| mednafen_ngp | ngpc | Bakumatsu Rouman Tokubetsu Hen -... | 描画あり | 58.5 | PCM信号あり | timeout |  |
| mednafen_pce | pcengine | BlazingLazers_U.pce | 全黒 | — | PCMほぼ無音 | timeout | 同じROMのPCE Fastは描画あり |
| mednafen_pce_fast | pcengine | BlazingLazers_U.pce | 描画あり | 60.0 | PCM信号あり | timeout |  |
| mednafen_pcfx | pcfx | simplebattle.cue | 起動直後終了 | — | 未取得 | exit=255 |  |
| mednafen_supafaust | sfc | Super Mario World - Super Mario ... | 異常終了 | — | 未取得 | signal=6 |  |
| mednafen_supergrafx | supergrafx | AxeBG.pce | 描画あり | 29.5 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| mednafen_wswan | wonderswan | Puzzle Bobble.ws | 描画あり | 59.5 | PCM信号あり | timeout |  |
| meteor | gba | Castlevania - Aria of Sorrow (Eu... | 描画あり | 58.8 | PCM無音 | timeout | 言語選択で待機、プレイ未確認 |
| mgba | gba | Castlevania - Aria of Sorrow (Eu... | 描画あり | 60.0 | PCM無音 | timeout | 言語選択で待機、プレイ未確認 |
| nekop2 | pc98 | Can Can Bunny 5 and half Limited... | 描画あり | 57.4 | PCMほぼ無音 | timeout |  |
| neocd | neogeocd | Fatal Fury/Fatal Fury.cue | 起動直後終了 | — | PCM無音 | exit=255 |  |
| nestopia | nes | Baseball.nes | 描画あり | 19.8 | PCM信号あり | timeout | FCEUX参照画像とNES枠色が不一致; 45 FPS未満（公称fpsとは未照合） |
| np2kai | pc98 | Can Can Bunny 5 and half Limited... | 異常終了 | — | 未取得 | signal=11 |  |
| numero | ti83 | tetris.8xp | 描画あり | 58.5 | PCM無音 | timeout |  |
| nxengine | cavestory | doukutsu/Doukutsu.exe | 描画あり | 60.0 | PCM無音 | timeout |  |
| o2em | odyssey2 | Interpol (Europe) (Proto).bin | 起動直後終了 | — | 未取得 | exit=255 |  |
| opera | 3do | biofury.iso | 全黒 | 19.8 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| pcsx_rearmed | psx | chroQW.img | 異常終了 | — | 未取得 | signal=11 |  |
| picodrive | megadrive | Bare Knuckle - Ikari no Tekken ~... | 描画あり | 59.8 | PCM信号あり | timeout |  |
| pokemini | pokemini | Pichu Bros. Mini (Japan).min | 描画あり | 60.0 | PCM信号あり | timeout |  |
| potator | supervision | assembloids_supervision_2022.bin | 描画あり | 60.0 | PCM信号あり | timeout |  |
| prboom | doom | freedoom2.wad | 全黒 | 5.5 | PCMほぼ無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| prosystem | atari7800 | Asteroids (1987) (Atari).a78 | 描画あり | 59.8 | PCM無音 | timeout |  |
| puae | amiga | 3rd Day - The Ripper (19xx)(Acti... | 描画あり | 19.6 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| puae2021 | amiga | 3rd Day - The Ripper (19xx)(Acti... | 描画あり | 12.0 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| quasi88 | pc88 | XeGrader100001.d88 | 描画あり | 55.3 | PCM無音 | timeout |  |
| quicknes | nes | Baseball.nes | 描画あり | 29.6 | PCM信号あり | timeout | FCEUX参照画像とNES枠色が不一致; 45 FPS未満（公称fpsとは未照合） |
| retro8 | pico8 | Celeste.p8 | 描画あり | 60.0 | PCM信号あり | timeout |  |
| scummvm | scummvm | sky.scummvm | 全黒 | 59.5 | PCM無音 | timeout |  |
| snes9x | sfc | Super Mario World - Super Mario ... | 描画あり | 31.1 | PCMほぼ無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| snes9x2002 | sfc | Super Mario World - Super Mario ... | 描画あり | 60.0 | PCM信号あり | timeout |  |
| snes9x2005 | sfc | Super Mario World - Super Mario ... | 描画あり | 60.0 | PCM信号あり | timeout |  |
| snes9x2005_plus | sfc | Super Mario World - Super Mario ... | 描画あり | 58.5 | PCM信号あり | timeout |  |
| snes9x2010 | sfc | Super Mario World - Super Mario ... | 描画あり | 19.5 | PCMほぼ無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| squirreljme | j2me | Cento.jar | 描画あり | 60.0 | PCM無音 | timeout |  |
| stella2014 | atari2600 | Asteroids.bin | 描画あり | 60.0 | PCM無音 | timeout |  |
| tgbdual | gb | Super Mario Land [V1.1].gb | 描画あり | 60.0 | PCM無音 | timeout |  |
| theodore | thomson | 3d Sub (1985)(Loriciels).k7 | 描画あり | 50.0 | PCMほぼ無音 | timeout |  |
| tyrquake | quake | PAK0.PAK | 異常終了 | — | 未取得 | signal=11 |  |
| uw8 | microw8 | tunnel.uw8 | 描画あり | — | PCM無音 | timeout |  |
| uzem | uzebox | Arkanoid2.uze | 描画あり | 14.8 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| vba_next | gba | Castlevania - Aria of Sorrow (Eu... | 描画あり | 59.8 | PCM無音 | timeout | 言語選択で待機、プレイ未確認 |
| vbam | gba | Castlevania - Aria of Sorrow (Eu... | 描画あり | 60.0 | PCM無音 | timeout | 言語選択で待機、プレイ未確認 |
| vemulator | vmu | — | ROMなし | — | 未取得 | — | 対応するVMUファイルなし |
| vice_x64 | c64 | inbread.d64 | 全黒 | — | PCM無音 | timeout |  |
| vice_xvic | vic20 | tetwels.prg | 描画あり | 18.3 | PCM無音 | timeout | 45 FPS未満（公称fpsとは未照合） |
| virtualjaguar | jaguar | ClubDrive.j64 | 全黒 | 4.9 | PCMほぼ無音 | timeout | 45 FPS未満（公称fpsとは未照合） |

数値、ROM名、PCMゼロ率、画面ハッシュは同名のCSVに記録。実画像と詳細ログはローカルの `output/validation/rg280v-picoarch-20261115/smoke/` に保存している（GitにはROM画像を含めない）。

## 次回の切り分け対象

1. NESの色と約20〜30 FPS、および実機で報告済みの音の遅さ。FCEUX参照画像とのパレット比較から開始。
2. `異常終了` と `起動直後終了` をBIOS・ROM構成不足と実装問題に分離。特にCrocods、Dinothawr、NP2kai、TyrQuake、PCSX-ReARMed。
3. 全黒または低FPSのコアは、対応BIOSを揃えた後に実プレイまで進めて再計測。
4. FE復帰の自動処理が3回失敗した。試験ランナーの遅延再試行を追加したので、次の実機試験で検証する。
