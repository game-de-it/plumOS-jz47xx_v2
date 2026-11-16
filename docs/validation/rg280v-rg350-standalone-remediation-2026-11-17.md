# RG350配布OPKの問題対策（RG280V、2026-11-17）

## 判定の修正

前回の[62本監査](rg280v-rg350-standalone-audit-2026-11-17.md)は `opkrun` をFEと異なる環境で呼んでいた。FE相当の `PLUMOS_ROOT=/media/data/plumos`、`HOME=/media/data/plumos/home`、`SDL_VIDEODRIVER=kmsdrm`、`LD_LIBRARY_PATH=/media/data/plumos/lib` を指定して、配布順に全62本を再実行した。最初に報告された共有ライブラリ不足は25件から**17件**に減った。特に `libpng14.so.14` とSDL2が足りないという初回判定は誤りだった。再試験の生ログ・DRM画面・PCM計測はGit管理外の `output/rg280v-apps/rg350-device-audit-fe-env/` に保存した。

監査スクリプトはFE環境を既定に変更し、生の環境を再現するときだけ `--raw-env` を指定する。古いOPKの一部が計測フックの状態を壊していたため、0または240を超える画面提示率はFPS集計から除外する。これにより測定不能な値を「0 FPS」や性能不足と誤認しない。

追試で、同じ番号を再実行すると `/tmp/rg350-audit-XX.tsv` の前回値が混ざる監査スクリプトの欠陥も見つかった。実行前にリモートの計測・標準出力ファイルを消し、結果JSONを毎回新規作成するよう修正した。**修正前の再試験ログのFPSとPCM値は最終判定に使わない。** 下記の追加試験は修正後の新しいログによる。

## 共通ライブラリの対策と実機再試験

Buildrootと[libShake v0.3.0](https://github.com/zear/libShake)からMIPS/uClibc向けに10種類の共有ライブラリを構築した。`libSDL_sound-1.0.so.1`、`libSDL_net-1.2.so.0`、`libvorbisidec.so.1`、`libFLAC.so.12`、`libbz2.so.1.0`、`libtheoradec.so.1`、`libintl.so.8`、`libjpeg.so.8`、`libsndfile.so.1`、`libshake.so.1`。SD1の `/media/data/plumos/lib/` へ転送し、転送後のSHA-256を照合した。ビルド、ADB配布、OSイメージ生成の各スクリプトにも同じ依存を組み込んだ。OPK本体やROMは新たにFEへ登録していない。

| 配布番号・候補 | 対策後の結果 | 残る判定 |
| --- | --- | --- |
| 07 DOSBox | SDL_sound不足が解消し、320×240のDOSプロンプトを画面取得 | DOSゲーム・入力・音は未試験 |
| 17 OpenBOR | Vorbis不足が解消し、起動ロゴまで進む | ゲームデータなし |
| 29 Temper | bzip2不足が解消し、約60回/秒のSDL画面提示と音声コールバックを計測 | DRM画面は黒く、ゲーム中の色・音は未判定 |
| 10 EasyRPG | Vorbisとsndfile不足が解消し、Player起動を確認 | 対象ゲームなし。ログ上の `Framerate is 0 FPS!` は未解決 |
| 27 Snes9x | intl不足が解消し、SFC ROMで約34〜37回/秒の画面提示と非ゼロPCMを計測 | 性能不足。既存FEの除外を維持 |
| 31 VICEx64 | jpeg不足の次にungif不足が判明。旧libungifを隔離して試すと12秒存続・音声コールバックあり | 取得画面は黒、ALSA underrunあり。ゲーム表示・実機音は未判定 |
| 45〜47 Mednafen | intl不足が解消 | 45はROMなし。46・47は `git.cpp:98` のassertで停止 |
| 41 / 51 / 59 | libshake不足が解消 | 41は終了コード11、59はROMなしで終了。51旧PCSX4ALLは黒画面かつ約3回/秒の画面提示で、既存のplumOS版PCSX4ALLより劣る |
| 50 openMSX | theoradec不足が解消して12秒存続 | ROMを指定できず、ゲーム表示未判定 |
| 56 ScummVM | SDL_net不足の次に旧FLAC、さらにlibmad不足が判明 | 旧ライブラリ依存の連鎖が残る |
| 03 / 04 Atari800 | 旧readlineを隔離して試すと、次にncurses5 / ncursesw不足 | 未解決。ROM未指定 |
| 34 FBA44 | 旧OpenSSLを隔離して試すと、次にlibao不足 | 未解決。既存FBNeoも性能問題があるが、別経路として評価が必要 |

旧 `libreadline.so.6`、`libFLAC.so.8`、`libcrypto.so.1.0.0`、`libungif.so.4` は当時のソースからMIPS版を作り、**診断用ディレクトリだけ**に置いて依存の続きを調べた。グローバルな製品ライブラリやイメージには含めない。特に旧OpenSSLを入れるだけではFBA44は起動しない。診断用ディレクトリは試験後に端末から削除する。

## 共有ライブラリでは解決しない問題

- 18 OswanはMIPS ABIが現行ユーザーランドと合わず、ライブラリ追加では起動できない。ソースからSoft float向け再ビルドが必要。
- 52〜54の配布PicoDriveはSDLマウス初期化で止まる。既存のplumOS向けPicoDriveは別ビルドであり、32Xはゲーム中約25〜56 FPSだったためFEには追加しない。
- 16 Nestopiaと57〜58 SMS Plusの配布原版は異常終了。各機種の既存FE経路を維持する。
- 26 ReGBAなど一部の配布原版ではFPS採取フックが壊れる。見かけの0や巨大な値から速度を判断しない。
- ROM/BIOSを指定できない候補とインストーラ画面のみの候補は、ゲーム実行の合否を出せない。起動ロゴ、タイトル、メニューのFPSはゲーム中のFPSではない。

既存FEで動いているコアや修正版の評価を、配布原版OPKの未合格判定で取り消さない。FEへの追加はゲーム中の色・音・速度、入力、終了後のFE復帰を揃えてから判断する。

## 追加追試: 旧ライブラリとROMの実行（同日）

診断用の隔離ディレクトリに、GNU ncurses 5.9の通常／wide版、Buildrootのlibao 1.2.0・libmad 0.15.1b、FluidSynth 1.1.11を加えた。ncurses 5.9は現代のGCCでソース生成が失敗するため、[Buildrootの修正](https://lists.busybox.net/pipermail/buildroot/2015-May/117116.html)に従い、生成時のプリプロセッサへ `-P` を追加した。これらはすべて実機へハッシュ照合して転送し、**製品領域には配布していない**。

- **Atari800 #03/#04**: 旧readlineとncursesの不足は解消。ROM未指定では両方とも終了コード10。#04へ`CavernsOfMars.rom`を指定すると15秒存続したが、取得画面は白帯で、ゲーム表示・音は不合格。OPKにはAtari BIOSが同梱されている。試験用ROMとBIOSの端末コピーは削除済み。
- **FBA44 #34**: 旧OpenSSLとlibaoの不足は解消。配布OPKのdesktop `Exec`には`%f`がなく、ROMパスが渡らないため、診断用コピーだけ`Exec=fbasdl.dge %f`に変更した。`kungfum.zip`はプログラム・グラフィック読込に成功し、計測ファイルを初期化した18秒実行ではSDL画面提示が最後の窓で約60回/秒。しかしDRM取得画面は色・文字が崩れ、音声コールバックは全ゼロ。`bmaster.zip`では最後の窓約9回/秒・黒画面。**FEへ追加しない。** SDLモードは320×240、RGB565、pitch 640で、フレーム間にsurfaceの画素ポインタ変化はなかった。`fbcon`経路はSDL初期化に失敗した。旧OpenSSLを製品へ置いていない。
- **ScummVM #56**: SDL_net→旧FLAC→libmad→FluidSynth 1.1.11の順に依存不足を解消。10秒存続し、旧ライブラリ不足では停止しなくなった。ただしOPK内`libmad.so`をプラグインと誤認する警告があり、画面取得はFEのままで、音声・入力・ゲーム起動は未確認。FE登録は保留。
- **VICE #31**: 旧ungif導入後も画面は黒で、ALSA underrunを連続記録。ROMデータ未指定であり、起動存続のみ確認。

診断中にAtari800終了後のFE再起動が一度失敗した。手動の`S95frontend restart`で復旧し、後続試験ではFE復帰を確認した。監査スクリプトはFE復帰を最大10秒再確認するよう修正。旧ライブラリ10ファイル、試験用ROM・BIOS、診断プローブは試験終了後に端末から撤去し、FEが稼働していることを確認した。

## 実行と記録

```
python3 scripts/audit-rg350-opks-device.py --start 1 --end 62 --seconds 8 --tag fe-env
python3 scripts/audit-rg350-opks-device.py --only 7 10 17 29 50 56 --seconds 12 --tag compat-retest
python3 scripts/audit-rg350-opks-device.py --only 10 27 31 45 46 47 --seconds 10 --tag compat2-retest
python3 scripts/audit-rg350-opks-device.py --only 41 51 59 --seconds 12 --tag libshake-retest
python3 scripts/audit-rg350-opks-device.py --only 3 4 31 34 56 --seconds 12 --extra-lib-dir /media/data/plumos/legacy-audit-lib --tag legacy-retest
```

各結果は `output/rg280v-apps/rg350-device-audit-{fe-env,compat-retest,compat2-retest,libshake-retest,legacy-retest}/` にある。スクリーンショットとPCM計測は機械判定であり、実機の色・音質・操作の代わりにはならない。
