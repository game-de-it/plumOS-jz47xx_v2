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

試験用コアは`libretro/libretro.c`の内部音声周波数を44.1 kHzから32 kHzに変更してビルドした。元のコアは端末の`/media/data/plumos/backups/genesis_plus_gx_libretro.so.pre-32khz-20261116`とホストの`output/rg280v-emulators/genesis_plus_gx_libretro.baseline-20261116.so`に保存済み。現在、端末には試験用32 kHzコアを配置してハッシュを照合し、FEが稼働中。ユーザーへ同じ低下場面と音の実機比較を依頼した。

比較結果が出るまでは32 kHz変更をビルド手順やFE既定には取り込まない。
