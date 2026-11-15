# RG280V PSXのFE登録と起動試験（2026-11-16）

ユーザーの方針に従い、エミュレータのクラッシュとFE登録を分けて扱う。PSXをFEの有効機種に追加し、PicoArch PCSX ReARMedを起動候補にした。plumOS-A30の既定テーマからPSXの機種ロゴを追加。ユーザーのROMライブラリからCUEと対応IMGの組を4タイトル配置し、PCSX ReARMedが検索する形式のPSX BIOSを3種配置した。ROM・BIOSはGit管理外に置く。

SD2上の転送ファイル11件はSHA-256で照合した。FEの再スキャンでPSXのCUE 4件を登録し、PSXは18番目の有効機種になった。SD2は読み取り専用マウントへ戻し、FEプロセスの再起動後の稼働を確認。個別ハッシュはGit管理外の`output/rg280v-emulators/psx-samples-20261116.json`に保存した。

`sin_FortuneQuest.cue`を使った12秒の時間制限付き起動試験では、PCSX ReARMedは画面・音声の計測開始前に`signal 11`で異常終了した。以前の`chroQW.img`試験でも同じシグナルで終了しており、今回は別のCUE/IMGとBIOSを配置しても再現した。ウォッチドッグ終了後にFEが復帰したことを確認。**PSXのFE登録は維持**し、クラッシュ原因の調査と映像・音・FPS・入力の実機確認を残す。
