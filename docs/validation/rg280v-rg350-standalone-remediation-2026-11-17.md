# RG350配布OPKの問題対策（RG280V、2026-11-17）

## 判定の修正

前回の[62本監査](rg280v-rg350-standalone-audit-2026-11-17.md)は `opkrun` をFEと異なる環境で呼んでいた。FE相当の `PLUMOS_ROOT=/media/data/plumos`、`HOME=/media/data/plumos/home`、`SDL_VIDEODRIVER=kmsdrm`、`LD_LIBRARY_PATH=/media/data/plumos/lib` を指定して、配布順に全62本を再実行した。最初に報告された共有ライブラリ不足は25件から**17件**に減った。特に `libpng14.so.14` とSDL2が足りないという初回判定は誤りだった。再試験の生ログ・DRM画面・PCM計測はGit管理外の `output/rg280v-apps/rg350-device-audit-fe-env/` に保存した。

監査スクリプトはFE環境を既定に変更し、生の環境を再現するときだけ `--raw-env` を指定する。古いOPKの一部が計測フックの状態を壊していたため、0または240を超える画面提示率はFPS集計から除外する。これにより測定不能な値を「0 FPS」や性能不足と誤認しない。

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

## 実行と記録

```
python3 scripts/audit-rg350-opks-device.py --start 1 --end 62 --seconds 8 --tag fe-env
python3 scripts/audit-rg350-opks-device.py --only 7 10 17 29 50 56 --seconds 12 --tag compat-retest
python3 scripts/audit-rg350-opks-device.py --only 10 27 31 45 46 47 --seconds 10 --tag compat2-retest
python3 scripts/audit-rg350-opks-device.py --only 41 51 59 --seconds 12 --tag libshake-retest
python3 scripts/audit-rg350-opks-device.py --only 3 4 31 34 56 --seconds 12 --extra-lib-dir /media/data/plumos/legacy-audit-lib --tag legacy-retest
```

各結果は `output/rg280v-apps/rg350-device-audit-{fe-env,compat-retest,compat2-retest,libshake-retest,legacy-retest}/` にある。スクリーンショットとPCM計測は機械判定であり、実機の色・音質・操作の代わりにはならない。
