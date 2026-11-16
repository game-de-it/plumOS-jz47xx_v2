# RG280V SuperGrafxでPCE Fastの映像・無音を修正（2026-11-16）

ユーザーはSuperGrafxのPCE Fast候補で映像が乱れ、音が出ず、停止しているように見えると報告した。実機ログでは `1941 - Counter Attack`、`Aldynes`、`Battle Ace`、`Dai Makaimura` のSuperGrafx ROMが `mednafen_pce_fast_libretro.so` でロード・終了しており、プロセスが残るハングは確認されなかった。機種別と `Dai Makaimura` のROM別選択履歴にもPCE Fastが残っていた。

原因はコアの対応範囲。Libretroの[Beetle PCE Fastの説明](https://docs.libretro.com/library/beetle_pce_fast/)はSuperGrafxモジュールを含まないと明記し、[Beetle SuperGrafxの説明](https://docs.libretro.com/library/beetle_sgx/)は同機種への対応を示す。したがってSuperGrafxのFE候補から `picoarch:mednafen_pce_fast` を外し、`picoarch:mednafen_supergrafx` のみを残した。PCエンジン側の2候補は変更しない。

修正前に、同じ `1941 - Counter Attack (Super Grafx) (J).pce` をBeetle SuperGrafxで10秒間自動起動した。DRM取得画像は警告画面からタイトル画面へ進み、全黒ではなかった。後半の画面更新窓は58.7〜59.96 FPS。音声コールバックは開始後約6秒まで無音で、最後の計測では非ゼロのPCM信号があった。音の実際の聞こえ方と操作・メニュー・FE復帰は物理確認が必要。診断終了後にFEを復旧した。

実機の `systems.json` をSHA-256 `fc873d10e6d9ec5949b27820b1a2a5a16c3153af8d26072daf2162e094aa010f` で照合し、PCE Fastを指す機種別・ROM別選択履歴を削除。FE再起動後の `plumos-text-ui core system supergrafx` にはBeetle SuperGrafxだけが表示された。FEプロセスは稼働し、SD2は読み取り専用を維持した。ROMと両コアの実体は削除していない。

修正後、ユーザーがFEから同じ `1941 - Counter Attack` を起動し、映像・音・操作・SELECT＋STARTメニューからの終了とFE復帰をすべて正常と確認した。実機ログでも `mednafen_supergrafx_libretro.so` による同ROMのロードと終了を確認。これで報告された症状の実機確認は完了した。
