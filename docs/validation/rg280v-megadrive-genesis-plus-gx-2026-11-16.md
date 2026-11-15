# RG280V Mega Drive: Genesis Plus GXのFPS低下

## 実機報告

- FEのMega Drive候補は単体PicoDrive、PicoArch Genesis Plus GX、PicoArch PicoDriveの順。
- ユーザーはGenesis Plus GXで複数ROMを確認し、いずれも場面により約60 FPSから約30 FPSへ下がると報告。ほかの2候補は正常との報告。
- RG280VのCPU設定は996 MHz。過去に1092 MHzで不安定になったため、今回の比較では変更しない。

## 比較

| 条件 | コアSHA-256 | Shinobiの約20秒自動起動・最終FPS窓 | 注意 |
| --- | --- | ---: | --- |
| 従来の44.1 kHz | `fc36fac9bc4b1f17403d2e0c2113ef224a62b1f981a053eba0e343c3d72d2924` | 59.99 | タイトル画面付近。実ゲームの低下場面を含まない |
| 試験用32 kHz | `c400c04f3f7b5a58002cee4667daf87a4c998a8e0b8d4ecc55e7f05861331573` | 59.99 | 同上。音質の実機確認待ち |

両条件とも起動初期の窓は約29 FPSで、後続の窓は約58～60 FPS。約20秒の無操作計測だけではプレイ中の共通した低下を特定できない。音声統計はタイトル中ほぼ無音であり、音質判定にも使えない。

試験用コアは`libretro/libretro.c`の内部音声周波数を44.1 kHzから32 kHzに変更してビルドした。元のコアは端末の`/media/data/plumos/backups/genesis_plus_gx_libretro.so.pre-32khz-20261116`とホストの`output/rg280v-emulators/genesis_plus_gx_libretro.baseline-20261116.so`に保存済み。

ユーザーが比較版でも約30 FPSに落ちる場面を報告。表示中の`sega_us_CastlevaniaBloodlines.bin`で`picoarch` PID 4496を確認し、CPU周波数は996 MHz。`/proc/4496/stat`の5秒差分はCPU約258 tick、約52%相当（100 tick/秒換算）、別の4秒差分は約226 tick、約57%相当。`wchan`ではDRMのVBlank待ちも観測した。30 FPSでCPU約52～57%なら1表示フレーム当たり約17～19 msのCPU時間に相当し、60 Hzの約16.7 ms枠を超える。ただし、このサンプルには表示FPSの同時機械記録がないため、ユーザーの30 FPS表示と組み合わせた推定である。単に出力回数の半減だけでは説明できず、コア処理とVBlank同期の境界にある可能性が高い。

32 kHz比較版は改善しなかったため正式採用しない。ユーザーがゲームを終了してFEへ戻った後、元コアを端末・ホスト出力・ビルド元ソースへ復元した。端末コアSHA-256は元の`fc36fac9bc4b1f17403d2e0c2113ef224a62b1f981a053eba0e343c3d72d2924`と一致する。

Mega DriveのFE候補からGenesis Plus GXを外し、単体PicoDriveとPicoArch PicoDriveを残した。選択上書きも単体PicoDriveへ変更。端末のFE設定SHA-256は`343ab37d1611af3793c3023b3f15bd395bfdb535f3f3ae1d7fc4ceb9b685e3a9`、選択上書きは`f7601186fdd52d29a52fb36ba0530177f2cfcc57127e98b3ad8185b899b0ac59`で配置時の照合値と一致。FE再起動後にプロセスPID 4619を確認した。Genesis Plus GXコアとレシピは他システムの試験用に保持する。FEの物理表示確認は今回未取得。
