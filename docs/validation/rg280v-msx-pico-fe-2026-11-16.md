# RG280V MSXのPicoArch起動ファイル確認（2026-11-16）

FEのMSX候補は当初 `retroarch:bluemsx` と `retroarch:fmsx` だった。ユーザーはRA経路の廃止と、PicoArchの両コアでゲームが起動しないことを報告した。公式の[fMSX BIOS一覧](https://docs.libretro.com/library/fmsx/)と[blueMSXのシステムファイル案内](https://docs.libretro.com/library/bluemsx/)を参照し、実機のPicoArchが `/media/data/plumos/bios` をシステムディレクトリとして渡すことをソースで確認した。

fMSXは実機にコア本体がなく、同ディレクトリに `MSX.ROM`、`MSX2.ROM`、`MSX2EXT.ROM`、`MSX2P.ROM`、`MSX2PEXT.ROM` も無かった。手元の各ファイルのMD5は公式資料と一致。ディスク用の `DISK.ROM` とともに実機へ転送し、転送前後のSHA-256一致を確認した。固定リビジョン `4de11755ce4f196ac1c8a7bb20bb4eccbc87a7d4` からビルドしたMIPS `fmsx_libretro.so` のSHA-256は `de8d1334de6dcc3db6ae40a5a951652da9b7fe523a09d06e41ffdba3e37a39ca` で、実機配置品と一致する。

blueMSXの `Machines` と `Databases` は既にあったが、ROM起動時の自動選択が要求する `Machines/MSX2+/config.ini` が欠けていた。SD2にある完全版 `blueMSXv282full` の同ファイルをBIOS領域へ追加し、SHA-256 `6d6f259bd9e161174000bcd4705b0cfbe3b9c333ea8df644049543ca3e68bebd` で照合した。同設定が参照する共有ROM 8本、`Machines/MSX2/config.ini` と `Databases/msxromdb.xml` も実機と手元のファイルでハッシュ一致。PicoArch本体は検証済みのSHA-256 `aeacea598b60e6287c65b77f0f37fb313e6ceee699315cb13cb9ea1ee58a5be4` に戻し、blueMSXの機種設定を強制する一時変更は採用しなかった。

同じSD2の `usas.rom` を短時間起動した機械的検査では、fMSXとblueMSXがともにゲームのタイトル画面へ進んだ。DRMキャプチャは `output/rg280v-emulators/msx-smoke-full-bios-20261116-fmsx/fmsx-late.png` と `output/rg280v-emulators/msx-smoke-full-bios-20261116/bluemsx-late.png`。約22秒の計測区間では両コアとも約60 FPSだった。機械的な音声サンプルではタイトル画面の音の有無を判定できなかった。その後、ユーザーはFEからfMSXとblueMSXで `usas.rom` を実機確認し、両方とも映像・音・操作・FPS・SELECT＋STARTからのFE復帰をすべて正常と報告した。blueMSXの実機ログにも同ROMのロードとコア終了が記録され、FEプロセスが稼働している。

FE候補を `picoarch:fmsx`、`picoarch:bluemsx` の2件にして、既定をfMSXに変更した。マージ処理で比較した実機設定の変更対象はMSXのみ。配置後の設定SHA-256は `8c4f65c763f02a10afe687b1b6e0e699cb1ce80a961a9b5b8d2d356864c938ce`。FEが稼働し、SD2が読み取り専用であることを確認した。ビルド・デプロイ・SDイメージ作成手順に両コアと対応するソース・ライセンスを加え、シェル構文を確認した。SDイメージ全体は生成していない。BIOSはユーザーの保有ファイルから実機へ配置し、GitとSDイメージには含めていない。新しいSDイメージではBIOSの別途配置が必要。
